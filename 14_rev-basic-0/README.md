# 14_rev-basic-0

- 문제 링크: [Dreamhack 14_rev-basic-0](https://dreamhack.io/wargame/challenges/14/)
- 분류: 리버싱

## 풀이

### 입력 처리

PE x64 바이너리의 `main` 역할을 하는 함수는 `0x140001100`에 있습니다. 해당 함수는 스택에 0x100바이트 크기의 입력 버퍼를 만들고 다음 문자열을 사용해 입력을 받습니다.

```text
%256s
```

따라서 공백 전까지의 문자열을 최대 256바이트까지 입력받은 뒤, 입력 버퍼를 `0x140001000`의 검증 함수에 전달합니다.

```asm
; 0x140001100
lea     rdx, [rsp+0x20]       ; 입력 버퍼
lea     rcx, [0x140002244]    ; "%256s"
call    scanf_wrapper

lea     rcx, [rsp+0x20]       ; 첫 번째 인자: 입력값
call    0x140001000          ; 검증 함수
```

검증 결과가 0이 아니면 `0x140002250`의 `Correct`를 출력하고, 0이면 `0x140002258`의 `Wrong`을 출력합니다.

### 검증 로직

`0x140001000`에서는 Windows x64 호출 규약에 따라 `rcx`에 입력값을, `rdx`에 비교 대상 문자열 주소를 넣고 `strcmp`를 호출합니다.

```asm
; 0x140001000
lea     rdx, [rip+0x1210]      ; 0x140002220
mov     rcx, [rsp+0x40]        ; 입력값
call    strcmp

test    eax, eax
jne     not_equal
mov     DWORD PTR [rsp+0x20], 1 ; strcmp == 0이면 성공
```

비교 대상인 `0x140002220`의 문자열을 `.rdata`에서 확인하면 다음과 같습니다.

```text
Compar3_the_str1ng
```

즉, `strcmp(input, "Compar3_the_str1ng") == 0`이 되도록 입력하면 `Correct`가 출력됩니다.

## 바이너리 추출 결과

### 파일 형식

`file` 명령으로 확인한 바이너리 형식은 다음과 같습니다.

```console
$ file chall0.exe
chall0.exe: PE32+ executable (console) x86-64, for MS Windows
```

즉, Windows용 64비트 PE 콘솔 프로그램입니다. `objdump -h`로 확인한 섹션 구성은 다음과 같습니다.

| 섹션 | 가상 주소 | 크기 | 주요 용도 |
|---|---:|---:|---|
| `.text` | `0x140001000` | `0xF98` | 실행 코드와 함수 |
| `.rdata` | `0x140002000` | `0xEFC` | 문자열, import 정보 등 읽기 전용 데이터 |
| `.data` | `0x140003000` | `0x200` | 초기화된 전역 데이터 |
| `.pdata` | `0x140004000` | `0x1B0` | 예외 처리 및 unwind 정보 |
| `.rsrc` | `0x140005000` | `0x1E0` | PE 리소스 |
| `.reloc` | `0x140006000` | `0x1C` | 재배치 정보 |

추출 명령은 다음과 같습니다.

```console
$ objdump -h chall0.exe
$ strings -a -n 4 chall0.exe
$ objdump -s -j .rdata chall0.exe
$ objdump -d -Mintel chall0.exe
```

### 문자열 추출

`strings`에서 검증에 직접 사용되는 문자열을 추출하면 다음과 같습니다.

```console
$ strings -a -n 4 chall0.exe | grep -E 'Compar3|Input|%256s|Correct|Wrong'
Compar3_the_str1ng
Input :␠
%256s
Correct
Wrong
```

여기서 `␠`는 문자열 끝에 포함된 공백 한 칸을 눈에 보이도록 표시한 기호입니다.

`.rdata`의 해당 영역을 hexadecimal dump로 확인하면 문자열의 주소와 배치를 확인할 수 있습니다.

```text
140002220  436f6d70 6172335f 7468655f 73747231  Compar3_the_str1
140002230  6e670000 00000000 496e7075 74203a20  ng......Input :␠
140002240  00000000 25323536 73000000 00000000  ....%256s.......
140002250  436f7272 65637400 57726f6e 67000000  Correct.Wrong...
```

따라서 문자열 주소를 정리하면 다음과 같습니다.

| 주소 | 문자열 | 역할 |
|---|---|---|
| `0x140002220` | `Compar3_the_str1ng` | 입력 비교 대상 |
| `0x140002238` | `Input : ` | 입력 안내 문구 |
| `0x140002244` | `%256s` | 입력 형식 문자열 |
| `0x140002250` | `Correct` | 검증 성공 출력 |
| `0x140002258` | `Wrong` | 검증 실패 출력 |

import table에는 `strcmp`, `puts`, `__stdio_common_vfscanf`, `__stdio_common_vfprintf` 등이 포함되어 있습니다. 이 import 정보를 통해 문자열 비교, 입력, 출력에 표준 C 런타임 함수가 사용되었음을 추정할 수 있습니다.

### 핵심 디스어셈블리 추출

검증 함수 `0x140001000`의 핵심 명령은 다음과 같습니다.

```asm
; strcmp(input, 0x140002220)
0x140001009: lea  rdx, [rip+0x1210]  ; rdx = 0x140002220
0x140001010: mov  rcx, [rsp+0x40]    ; rcx = input
0x140001015: call 0x140001eb8        ; strcmp
0x14000101a: test eax, eax
0x14000101c: jne  0x140001028
0x14000101e: mov  DWORD PTR [rsp+0x20], 1
```

Windows x64 호출 규약에서는 첫 번째 인자를 `rcx`, 두 번째 인자를 `rdx`로 전달합니다. 따라서 위 코드는 `strcmp(input, "Compar3_the_str1ng")`을 호출하고, 반환값이 0일 때 검증 성공을 의미하는 값 1을 반환하는 코드입니다.

입력과 출력을 담당하는 `0x140001100`의 흐름은 다음과 같습니다.

```asm
0x14000112c: lea  rcx, [rip+0x1105]  ; "Input : "
0x140001133: call 0x140001190        ; 안내 문구 출력
0x140001138: lea  rdx, [rsp+0x20]    ; 입력 버퍼
0x14000113d: lea  rcx, [rip+0x1100]  ; "%256s"
0x140001144: call 0x1400011f0        ; 문자열 입력
0x140001149: lea  rcx, [rsp+0x20]
0x14000114e: call 0x140001000        ; 검증
0x140001155: je   0x140001166
0x140001157: lea  rcx, [rip+0x10f2]  ; "Correct"
0x14000115e: call puts
0x140001164: jmp  0x140001173        ; Wrong 분기 건너뜀
0x140001166: lea  rcx, [rip+0x10eb]  ; "Wrong"
0x14000116d: call puts
```

## 소스코드 형태로 재구성

PE 파일에는 원본 C 소스가 그대로 포함되어 있지 않으므로, 디스어셈블리와 추출한 문자열을 바탕으로 동작이 같은 형태의 C 코드로 재구성할 수 있습니다. 실제 컴파일러가 생성한 코드와 변수명까지 완전히 동일한 원본 소스가 아니라, 바이너리의 동작을 설명하기 위한 복원 코드입니다.

프로그램 구조는 다음과 같이 나눌 수 있습니다.

```text
main()
├── char input[256] 버퍼 생성 및 초기화
├── "Input : " 출력
├── scanf("%256s", input)
├── check_input(input) 호출
└── Correct 또는 Wrong 출력

check_input(input)
└── strcmp(input, "Compar3_the_str1ng") == 0 확인
```

이를 C 문법으로 표현하면 다음과 같습니다.

```c
#include <stdio.h>
#include <string.h>

int check_input(const char *input)
{
    const char *expected = "Compar3_the_str1ng";

    if (strcmp(input, expected) == 0) {
        return 1;
    }

    return 0;
}

int main(void)
{
    char input[256] = {0};

    printf("Input : ");
    scanf("%256s", input);

    if (check_input(input)) {
        puts("Correct");
    } else {
        puts("Wrong");
    }

    return 0;
}
```

바이너리와 재구성한 소스의 대응 관계는 다음과 같습니다.

| 바이너리 요소 | 재구성한 소스 요소 |
|---|---|
| `0x140001100` | `main` 함수 |
| `0x140001000` | `check_input` 함수 |
| `0x140002220` | `expected` 문자열 |
| `0x140002238` | `printf`의 안내 문구 |
| `0x140002244` | `scanf`의 입력 형식 문자열 |
| `0x140002250` | `puts("Correct")` |
| `0x140002258` | `puts("Wrong")` |

## 실행 결과

Wine으로 정답 입력을 전달해 바이너리 자체를 실행했습니다.

```console
$ printf 'Compar3_the_str1ng\n' | /usr/bin/wine64-stable ./chall0.exe
Input : Correct
```

따라서 정답 입력은 다음과 같습니다.

```text
Compar3_the_str1ng
```

문제에서 요구한 `DH{}` 형식으로 작성한 flag는 다음과 같습니다.

```text
DH{Compar3_the_str1ng}
```
