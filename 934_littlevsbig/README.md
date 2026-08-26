# 934_littlevsbig

- 문제 링크: [Dreamhack 934_littlevsbig](https://dreamhack.io/wargame/challenges/934/)
- 분류: 시스템 해킹
- 난이도: Sprout

## 풀이

`chall.c`는 8바이트 입력을 `unsigned int` 두 개로 해석한 뒤, 다음 값과 비교합니다.

```c
unsigned char arr[9];
scanf("%8s", arr);

unsigned int *int_arr = (unsigned int *)arr;

if (int_arr[0] == 0x64726d68 && int_arr[1] == 0x636b3a29) {
    puts("Nice!");
    puts(flag);
}
```

x86 환경은 little-endian이므로 정수 상수는 메모리에 바이트가 역순으로 저장됩니다.

| 비교 값 | 메모리 바이트 | ASCII 문자 |
|---|---|---|
| `0x64726d68` | `68 6d 72 64` | `h m r d` |
| `0x636b3a29` | `29 3a 6b 63` | `) : k c` |

따라서 두 값을 만족하는 8바이트 입력은 다음과 같습니다.

```text
hmrd):kc
```

## 실행 결과

```console
$ printf 'hmrd):kc\n' | ./chall
Input: arr  | 0x68  0x6d  0x72  0x64  0x29  0x3a  0x6b  0x63 |
arr  | 0x64726d68  0x636b3a29 |
Nice!
DH{sample}
```

따라서 flag는 다음과 같습니다.

```text
DH{sample}
```
