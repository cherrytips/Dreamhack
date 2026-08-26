# 852. ROT128

## 문제 설명

`rot128.py`는 `flag.png`를 바이트 단위로 읽어 암호화한 뒤, 결과를 `encfile`에 저장한다. 주어진 `encfile`을 복호화하여 원본 PNG를 복원하고, 이미지에 표시된 `DH{...}` 형식의 플래그를 확인한다.

## 암호화 분석

`rot128.py`는 각 평문 바이트를 다음과 같이 처리한다.

1. 바이트를 2자리 대문자 hexadecimal 문자열로 변환한다.
2. hexadecimal 값에 `128`을 더하고 `256`으로 나눈 나머지를 구한다.
3. 변환된 2자리 hexadecimal 문자열을 모두 이어 붙여 `encfile`에 저장한다.

평문 바이트를 `p`, `encfile`에서 읽은 값을 `e`라고 하면 암호화 식은 다음과 같다.

```text
e = (p + 128) mod 256
```

따라서 복호화는 다음과 같다.

```text
p = (e - 128) mod 256
```

`encfile`에는 바이트 사이의 구분자가 없으므로 2글자씩 분리해야 한다. 복호화한 값들을 다시 바이트열로 합치면 `flag.png`를 얻을 수 있다.

## 복호화

`solve.py`로 복호화한다.

```python
from pathlib import Path

enc = Path("encfile").read_text(encoding="utf-8").strip()
if len(enc) % 2:
    raise ValueError("encfile 길이가 홀수입니다.")

plain = bytes(
    (int(enc[i : i + 2], 16) - 128) % 256
    for i in range(0, len(enc), 2)
)
Path("flag.png").write_bytes(plain)
```

실행 방법은 다음과 같다.

```bash
cd 852_ROT128
python3 solve.py
```

## 결과 검증

복호화 결과는 다음과 같다.

```text
복호화 완료: 74405 bytes -> flag.png
PNG signature: 89 50 4E 47 0D 0A 1A 0A
```

`flag.png`는 `1792 x 848` 크기의 정상적인 PNG 이미지이며, 이미지를 열어 플래그를 확인한다.

![복호화된 flag.png](flag.png)

## 플래그

```text
DH{y0u_So1ved_basic_cryp7o_How_wa5_1t?}
```
