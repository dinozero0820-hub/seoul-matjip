"""앱이 실제로 받는 가벼운 데이터 파일 만들기 (데이터 요금 아끼기용)

pts.json, gu/*.json 은 작업용 원본으로 그대로 두고,
앱은 여기서 만든 작은 파일만 받는다.
  m.json      : 추천 집·학교 목록 등 (작음)
  p.gz        : 서울 음식점 전체 좌표·분류 (압축, 원래 pts.json 의 절반 이하)
  n/<구>.gz   : 구별 가게 이름·짧은 주소·전화 (압축)
add_curated.py 가 끝날 때 자동으로 실행된다. 직접 돌려도 된다:  python3 tools/build_app.py
"""
import json, base64, struct, gzip, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)

d = json.load(open(P("pts.json")))
raw = base64.b64decode(d["b"])
n = len(raw) // 8
X = []; Y = []; C = bytearray(n); SL = bytearray(n); SH = bytearray(n); F = bytearray(n)
for i in range(n):
    x, y, c, m, p = struct.unpack_from("<HHBHB", raw, i * 8)
    X.append(x); Y.append(y); C[i] = c; SL[i] = m & 255; SH[i] = m >> 8; F[i] = p

out = bytearray()
def varint(v):
    while v >= 0x80:
        out.append((v & 0x7F) | 0x80); v >>= 7
    out.append(v)
zig = lambda v: (v << 1) ^ (v >> 31)
px = py = 0
for x, y in zip(X, Y):
    varint(zig(x - px)); varint(zig(y - py)); px, py = x, y
blob = bytes(out) + bytes(C) + bytes(SL) + bytes(SH) + bytes(F)
open(P("p.gz"), "wb").write(gzip.compress(blob, 9, mtime=0))

m = {k: v for k, v in d.items() if k != "b"}
m["n"] = n
json.dump(m, open(P("m.json"), "w"), ensure_ascii=False, separators=(",", ":"))

os.makedirs(P("n"), exist_ok=True)
short = lambda a: re.split(r"[,(]", a or "")[0].strip()
tot = 0
for g in range(len(d["gu"])):
    rows = json.load(open(P("gu", f"{g}.json")))
    rr = [[r[0], short(r[1]), r[3] if len(r) > 3 else ""] for r in rows]
    b = gzip.compress(json.dumps(rr, ensure_ascii=False, separators=(",", ":")).encode(), 9, mtime=0)
    open(P("n", f"{g}.gz"), "wb").write(b); tot += len(b)
print(f"앱 데이터: p.gz {os.path.getsize(P('p.gz'))//1024}KB, m.json {os.path.getsize(P('m.json'))//1024}KB, 구별 이름 평균 {tot//len(d['gu'])//1024}KB")
