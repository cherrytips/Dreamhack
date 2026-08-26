#!/usr/bin/env python3
from pathlib import Path

enc = Path("encfile").read_text(encoding="utf-8").strip()
if len(enc) % 2:
    raise ValueError("encfile 길이가 홀수입니다.")

# 암호화는 b -> (b + 128) mod 256 이므로, 복호화는 b -> (b - 128) mod 256.
plain = bytes(
    (int(enc[i : i + 2], 16) - 128) % 256
    for i in range(0, len(enc), 2)
)
Path("flag.png").write_bytes(plain)
print(f"복호화 완료: {len(plain)} bytes -> flag.png")
print(f"PNG signature: {plain[:8].hex(' ').upper()}")
