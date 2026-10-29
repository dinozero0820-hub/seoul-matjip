import json,base64,struct,os,html,sys
from urllib.parse import quote
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT=ROOT
BASE="https://dinozero0820-hub.github.io/seoul-matjip/"
d=json.load(open(os.path.join(ROOT,"pts.json")))
b=base64.b64decode(d["b"]);N=len(b)//8
LAT=[0]*N;LNG=[0]*N;C=[0]*N;S=[0]*N;P=[0]*N
for i in range(N):
    x,y,c,m,p=struct.unpack_from("<HHBHB",b,i*8)
    LNG[i]=d["ln0"]+x/1e5;LAT[i]=d["la0"]+y/1e5;C[i]=c;S[i]=m;P[i]=p
CUR={int(k):v for k,v in d["cur"].items()}
TAGN={"s":"혼밥","l":"늦게까지","g":"단체","d":"데이트","w":"줄 서는 편"}
e=html.escape
import re
clean=lambda s:re.sub(r"\(.*?\)|주\)|㈜","",s or "").strip()
CSS="""
:root{--bg:#F3F4F1;--surface:#fff;--ink:#1B2220;--muted:#5F6B67;--line:#DCE1DC;--accent:#E0412B;--soft:#EEF1ED}
@media (prefers-color-scheme:dark){:root{--bg:#121614;--surface:#1B211F;--ink:#E8EDEA;--muted:#9AA6A1;--line:#2D3532;--accent:#FF6A50;--soft:#252C29;color-scheme:dark}}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font-family:"IBM Plex Sans KR",system-ui,-apple-system,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;line-height:1.55;
padding:20px max(16px,env(safe-area-inset-right,0px)) 48px max(16px,env(safe-area-inset-left,0px))}
.w{max-width:720px;margin:0 auto;display:grid;gap:16px}
a{color:var(--accent)}
.brand{font-family:"Black Han Sans",sans-serif;color:var(--accent);font-size:20px;text-decoration:none}
h1{font-family:"Black Han Sans",sans-serif;font-weight:400;font-size:clamp(28px,7vw,40px);line-height:1.15;margin:0;letter-spacing:-.01em;text-wrap:balance}
.lead{color:var(--muted);margin:0}
.cta{display:inline-flex;align-items:center;justify-content:center;background:var(--accent);color:#fff;text-decoration:none;font-weight:700;border-radius:12px;padding:12px 18px;justify-self:start}
ol{list-style:none;margin:0;padding:0;display:grid;gap:10px}
li{background:var(--surface);border:1px solid var(--line);border-radius:16px;padding:14px 16px;display:grid;gap:6px}
li h2{margin:0;font-size:18px;display:flex;gap:8px;align-items:baseline;flex-wrap:wrap}
li h2 small{font-size:12px;color:var(--muted);font-weight:500}
.m{display:flex;justify-content:space-between;gap:10px;background:var(--soft);border-radius:10px;padding:8px 10px;font-weight:700}
.m span:last-child{color:var(--accent);white-space:nowrap}
.t{display:flex;flex-wrap:wrap;gap:4px}.t span{font-size:12px;border:1px solid var(--line);border-radius:6px;padding:0 7px;color:var(--muted)}
.a{font-size:13px;color:var(--muted)}
.links{display:flex;gap:14px;font-size:14px;font-weight:700}
.unis{display:grid;grid-template-columns:repeat(auto-fill,minmax(150px,1fr));gap:8px}
.unis a{background:var(--surface);border:1px solid var(--line);border-radius:14px;padding:12px;text-decoration:none;color:var(--ink);display:grid}
.unis span{font-size:12px;color:var(--muted)}
footer{font-size:12px;color:var(--muted)}
"""
def page(title,desc,canon,body):
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1,viewport-fit=cover">
<title>{e(title)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{canon}">
<meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{canon}"><meta property="og:type" content="website">
<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Black+Han+Sans&family=IBM+Plex+Sans+KR:wght@400;500;700&display=swap">
<link rel="icon" href="{BASE}icon.svg" type="image/svg+xml"><style>{CSS}</style></head>
<body><div class="w">{body}<footer>가게 정보는 공개된 맛집 소개 글과 서울시 인허가 정보를 바탕으로 정리했어요. 가격·영업시간은 바뀔 수 있어요.</footer></div></body></html>"""
unis=[u for u in d["unis"] if u["picks"]]
import shutil
shutil.rmtree(f"{OUT}/u",ignore_errors=True)
os.makedirs(f"{OUT}/u",exist_ok=True)
for u in unis:
    name=u["u"];short=name.split("·")[0];items=[]
    for pk in u["picks"]:
        i=pk["i"];c=CUR[i];nm=clean(c[5]);mins=max(2,round(pk["d"]*1.3/70))
        cat=d["c1"][C[i]];subs=[s for b2,s in enumerate(d["sub"][C[i]]) if S[i]&(1<<b2)]
        tags=[]
        if (P[i]&3)==2:tags.append("매운맛")
        if c[1] and c[1]<=10000:tags.append("1만원 이하")
        tags+=[TAGN[k] for k in c[2] if k in TAGN]
        share=f"{BASE}?p={quote(nm)}&at={LAT[i]:.5f},{LNG[i]:.5f}"
        items.append(f"""<li><h2>{e(nm)} <small>{e(cat)}{(' · '+e(', '.join(subs))) if subs else ''} · 도보 약 {mins}분</small></h2>
<div class="m"><span>{e(c[0])}</span><span>{(format(c[1],',')+'원') if c[1] else ''}</span></div>
{('<p style="margin:0">'+e(c[3])+'</p>') if c[3] else ''}
{('<div class="t">'+''.join('<span>'+e(t)+'</span>' for t in tags)+'</div>') if tags else ''}
<div class="a">{e(c[6])}</div>
<div class="links"><a href="{share}">지도에서 보기</a><a href="https://map.kakao.com/link/to/{quote(nm)},{LAT[i]:.6f},{LNG[i]:.6f}" rel="noopener">길찾기</a></div></li>""")
    title=f"{short} 맛집 추천 {len(items)}곳 · 근처 밥집 지도"
    desc=f"{name} 근처 맛집 {len(items)}곳. 대표 메뉴, 가격, 맵기, 혼밥·단체·데이트 정보를 한눈에. "+", ".join(clean(CUR[p['i']][5]) for p in u['picks'][:5])
    body=f"""<a class="brand" href="{BASE}">서울 맛집 지도</a>
<h1>{e(short)} 근처 맛집 추천 {len(items)}곳</h1>
<p class="lead">{e(name)} 근처에서 메뉴·가격·맵기를 확인한 집만 모았어요. 혼밥, 늦게까지, 단체, 데이트 조건은 지도에서 바로 걸러볼 수 있어요.</p>
<a class="cta" href="{BASE}?u={u['slug']}">지도에서 {e(short)} 맛집 보기</a>
<ol>{''.join(items)}</ol>
<p><a href="{BASE}u/">다른 학교 맛집 보기</a></p>"""
    os.makedirs(f"{OUT}/u/{u['slug']}",exist_ok=True)
    open(f"{OUT}/u/{u['slug']}/index.html","w").write(page(title,desc,f"{BASE}u/{u['slug']}/",body))
hub="".join(f'<a href="{BASE}u/{u["slug"]}/"><b>{e(u["u"].split("·")[0])}</b><span>추천 {len(u["picks"])}곳</span></a>' for u in unis)
open(f"{OUT}/u/index.html","w").write(page("대학가 맛집 추천 · 서울 맛집 지도","서울 주요 대학 근처 맛집을 학교별로 모았어요. 연세대, 홍대, 고려대, 경희대 등.",f"{BASE}u/",
 f'<a class="brand" href="{BASE}">서울 맛집 지도</a><h1>학교별 맛집 추천</h1><p class="lead">학교를 고르면 근처에서 확인된 맛집을 보여드려요.</p><div class="unis">{hub}</div><a class="cta" href="{BASE}">지도 열기</a>'))
urls=[BASE,BASE+"u/"]+[f"{BASE}u/{u['slug']}/" for u in unis]
open(f"{OUT}/sitemap.xml","w").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'+"".join(f"<url><loc>{x}</loc><lastmod>{d['v']}</lastmod></url>\n" for x in urls)+"</urlset>\n")
open(f"{OUT}/robots.txt","w").write(f"User-agent: *\nAllow: /\nSitemap: {BASE}sitemap.xml\n")
print(len(unis),"pages")
