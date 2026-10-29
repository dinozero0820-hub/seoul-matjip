"""추천 집 반영 스크립트 (저장소 파일만으로 동작)

사용법 (저장소 루트에서):  python3 tools/add_curated.py
- tools/curated.json 의 항목을 지도 데이터(pts.json, gu/*.json)의 실제 영업 중 가게와 맞춰서
  추천(★) 표시, 대표 메뉴·가격·맵기·태그·한줄평을 넣고, 학교별 추천 목록을 다시 만든다.
- 몇 번을 다시 돌려도 결과가 같다(이미 반영된 항목은 그대로).
- 끝나면 tools/gen_pages.py 로 학교별 페이지와 sitemap.xml 을 다시 만든다.

curated.json 항목 형식:
 {"u":"학교 이름(campuses.json의 u)", "key":"가게 이름 일부", "hint":"주소 일부(없으면 빈칸)",
  "c1":"한식|일식|중식|양식|아시안|치킨|카페·디저트|주점", "sub":["메뉴 분류", ...],
  "menu":"대표 메뉴", "price":1인 가격(원, 모르면 0), "sp":0 안매움/1 모름·일부/2 매움,
  "tags":"s혼밥 l늦게까지(자정 이후) w줄서는편 g단체 d데이트 조합", "why":"한 줄 평(내 말로)", "src":"출처 사이트명"}
출처에 적힌 사실만 넣는다. 문장·사진을 그대로 가져오지 않는다.
"""
import json, base64, struct, math, re, os, sys, datetime

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)

d = json.load(open(P("pts.json")))
raw = bytearray(base64.b64decode(d["b"]))
N = len(raw) // 8
LAT = [0.0] * N; LNG = [0.0] * N; C = [0] * N; S = [0] * N; F = [0] * N
for i in range(N):
    x, y, c, m, p = struct.unpack_from("<HHBHB", raw, i * 8)
    LNG[i] = d["ln0"] + x / 1e5; LAT[i] = d["la0"] + y / 1e5; C[i] = c; S[i] = m; F[i] = p
offs = [0]
for c in d["cnt"]: offs.append(offs[-1] + c)
G = [0] * N
for g in range(len(d["gu"])):
    for i in range(offs[g], offs[g + 1]): G[i] = g
names = [json.load(open(P("gu", f"{g}.json"))) for g in range(len(d["gu"]))]
row = lambda i: names[G[i]][i - offs[G[i]]]  # [이름, 주소, 업종]

camps = json.load(open(P("tools", "campuses.json")))
CAMP = {c["u"]: c for c in camps}
cur = json.load(open(P("tools", "curated.json")))
CUR = {int(k): v for k, v in d.get("cur", {}).items()}
C1 = d["c1"]; SUB = d["sub"]

def dist(a, b, c, e): return math.hypot((a - c) * 111000, (b - e) * 88000)
norm = lambda s: re.sub(r"\s", "", s or "")

picks = {c["u"]: {} for c in camps}
for u in d.get("unis", []):
    if u["u"] in picks:
        for p in u["picks"]: picks[u["u"]][p["i"]] = p["d"]

miss = []; added = 0
for e in cur:
    cp = CAMP.get(e["u"])
    if not cp: miss.append((e["u"], e["key"], "학교 없음")); continue
    k = norm(e["key"]); hint = norm(e.get("hint", ""))
    best = None
    lat0, lng0 = cp["lat"], cp["lng"]
    for i in range(N):
        if abs(LAT[i] - lat0) > 0.02 or abs(LNG[i] - lng0) > 0.026: continue
        r = row(i)
        if k not in norm(r[0]): continue
        dd = dist(LAT[i], LNG[i], lat0, lng0)
        if dd > 2200: continue
        h = 1 if hint and hint in norm(r[1]) else 0
        cand = (-h, -(i in CUR), dd, i)  # 이미 추천된 같은 이름 가게가 있으면 그걸 다시 씀(중복 방지)
        if best is None or cand < best: best = cand
    if best is None: miss.append((e["u"], e["key"], "가게를 못 찾음")); continue
    if e.get("hint") and best[0] == 0 and len(k) <= 2: miss.append((e["u"], e["key"], "이름이 짧고 주소가 안 맞음")); continue
    i = best[3]
    if e["c1"] not in C1: miss.append((e["u"], e["key"], "음식 종류 오타")); continue
    ci = C1.index(e["c1"]); mask = 0
    for s in e.get("sub", []):
        if s in SUB[ci]: mask |= 1 << SUB[ci].index(s)
    if i not in CUR: added += 1
    C[i] = ci; S[i] = mask; F[i] = (int(e.get("sp", 1)) & 3) | 4
    r = row(i)
    CUR[i] = [e.get("menu", ""), int(e.get("price") or 0), e.get("tags", ""), e.get("why", ""), e.get("src", ""), r[0], r[1]]
    picks[e["u"]][i] = int(best[2])

for i in range(N):
    struct.pack_into("<HHBHB", raw, i * 8, round((LNG[i] - d["ln0"]) * 1e5), round((LAT[i] - d["la0"]) * 1e5), C[i], S[i], F[i])
d["b"] = base64.b64encode(bytes(raw)).decode()
d["cur"] = {str(k): v for k, v in CUR.items()}
d["unis"] = [{"u": c["u"], "slug": c["slug"], "lat": c["lat"], "lng": c["lng"],
              "picks": [{"i": i, "d": dd} for i, dd in sorted(picks[c["u"]].items(), key=lambda x: x[1])]}
             for c in sorted(camps, key=lambda c: c["u"])]
d["v"] = d.get("v", "")
json.dump(d, open(P("pts.json"), "w"), ensure_ascii=False, separators=(",", ":"))

print(f"새로 추천에 들어간 집: {added}곳 / 전체 추천 집: {len(CUR)}곳")
for u in d["unis"]: print(f"  {u['u']}: {len(u['picks'])}곳")
if miss:
    print("반영 못 한 항목:")
    for m in miss: print("  ", *m)
os.system(f'python3 "{P("tools","gen_pages.py")}"')
