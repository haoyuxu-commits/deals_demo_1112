"""Render official CSV exports as offline weekly trend reports."""
import csv, json, re, runpy
from pathlib import Path
from datetime import date
from html import escape

ROOT=Path(__file__).resolve().parent
helpers=runpy.run_path(str(ROOT.parent/'pinterest-trends-us/build.py'))
page,table,link=helpers['page'],helpers['table'],helpers['link']
def e(v): return escape(str(v or '未提供'),quote=True)
CONSUMER=['walmart black friday 2026','nintendo black friday','target black friday 2026','walmart thanksgiving meal deal','krispy kreme thanksgiving donuts','walmart black friday deals 2026','nintendo switch black friday',"kohl's black friday early deals 2026"]
VERIFIED_GROWTH={'microsoft outage':'1,000%','jensen huang':'1,000%','commanders vs giants':'1,000%','mark mcguinn':'1,000%','dan hicks':'1,000%','yella beezy':'1,000%','social security cuts':'1,000%','anthony clark':'1,000%','italy vs france':'1,000%','stacy keach':'1,000%','james gunn':'1,000%','disco singer rochelle fleming passes':'1,000%','coachella 2027 lineup':'900%','dc shooting':'1,000%','building collapse nyc':'1,000%','the body netflix':'700%','gta 6':'75%','usman nurmagomedov':'1,000%','raptors vs 76ers':'1,000%','mavericks vs timberwolves':'1,000%','pistons vs wizards':'1,000%','dane cook':'400%','alaina kunes':'400%','ss united states':'1,000%','tomb of the unknown soldier':'1,000%'}
entries=[]
for path in sorted(ROOT.glob('????-??-??.csv'),reverse=True):
    day=path.stem
    with path.open(encoding='utf-8-sig',newline='') as f: raw=list(csv.DictReader(f))
    rows=[]
    for i,r in enumerate(raw):
        rows.append(dict(id=f'{day}-{i+1}',order=i+1,name=r['趋势'],volume=r['搜索量'],started=r['已开始'],ended=r['已结束'] or None,status='已结束' if r['已结束'] else '活跃',related=r['趋势细分'],url=r['浏览链接'],growth=VERIFIED_GROWTH.get(r['趋势']) if day=='2026-11-13' and i<25 else None,consumer_candidate=r['趋势'] in CONSUMER))
    unique=len({r['name'] for r in rows}); active=sum(r['status']=='活跃' for r in rows)
    meta={'date':day,'region':'US','window':'过去7天（168小时滚动窗口）','source':'https://trends.google.com/trending?geo=US&hours=168','collected_at':'2026-11-13T17:18:00+08:00' if day=='2026-11-13' else day,'row_count':len(rows),'unique_names':unique,'active':active,'baseline':True,'coverage':'官方CSV全部行；首页25条增长率来自可见页面。CSV无增长率字段。','items':rows}
    (ROOT/f'{day}.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
    iso=date.fromisoformat(day).isocalendar(); week=f'{iso.year}-W{iso.week:02}'
    body=f'<header><div class="eyebrow">GOOGLE TRENDS · UNITED STATES</div><h1>Google 美国趋势周报</h1><p>{day} · {week} · 首期基线</p><p class="muted">采集：{e(meta["collected_at"])} · 美国 · 过去7天 · 所有类别 · 所有趋势 · 按相关性排序</p><nav><a href="index.html">历史目录</a><a href="../pinterest-trends-us/index.html">Pinterest 周报</a><a href="{day}.csv" download>官方 CSV</a><a href="{day}.json" download>结构化 JSON</a>{link(meta["source"],"Google 来源")}</nav></header>'
    body+='<div class="stats">'+''.join(f'<div class="stat"><strong>{v:,}</strong><span>{label}</span></div>' for v,label in [(len(rows),'导出记录'),(unique,'不同趋势名称'),(active,'活跃记录'),(len(rows)-active,'已结束记录'),(sum(bool(r['growth']) for r in rows),'已核实增长率'),(sum(r['consumer_candidate'] for r in rows),'消费主题候选')])+'</div>'
    body+='<p class="note">这是一份搜索热点清单。热点词不等于经核实的新闻事实或购物意向；相关查询中的传言和疑问也不代表事实。搜索量为来源显示的量级，不能当精确值。增长率为平台口径，不能直接解释为周环比。</p>'
    body+='<section><h2>本期观察</h2><p>完整列表包含新闻、人物、体育和消费等多种热点。消费候选中可见 Walmart 与 Nintendo 黑五，以及感恩节餐食主题。可以把这些作为选题线索，但需要进一步验证商品相关性与需求。</p><p>与本期 Pinterest 的感恩节聚会主题存在语义关联：Google 的 Walmart 感恩节餐食、Krispy Kreme 感恩节甜甜圈可作为补充线索。这不是相同关键词的双平台增长证明。</p><p class="muted">首次采集无历史基线；本期未完成 Google Explore 的长期走势核验，不声称持续升温。</p></section>'
    picks=[r for r in rows if r['consumer_candidate']]
    body+='<section><h2>消费相关主题候选</h2><p class="muted">人工按主题语义选取，并非 Google 官方分类或完整购物榜单。</p>'+table(['关键词','搜索量级','状态','开始时间'],[[link(r['url'],r['name']),e(r['volume']),e(r['status']),e(r['started'])] for r in picks])+'</section>'
    body+='<section><h2>完整趋势列表</h2><p class="muted">同名记录分别保留。序号是导出顺序，不是搜索量排名。关联查询可展开查看。</p><div class="controls"><input id="searchInput" placeholder="搜索关键词或关联查询" aria-label="搜索趋势"><select id="statusFilter" aria-label="筛选状态"><option value="">所有状态</option><option>活跃</option><option>已结束</option></select><span id="counter" aria-live="polite"></span></div><div class="scroll"><table><thead><tr><th>序号</th><th>趋势</th><th>搜索量级</th><th>增长率</th><th>状态</th><th>开始 / 结束（UTC+8）</th><th>关联查询</th></tr></thead><tbody id="records">'
    for r in rows:
        related=e(r['related']) if r['related'] else '未提供'
        body+=f'<tr data-status="{r["status"]}"><td>{r["order"]}</td><td>{link(r["url"],r["name"])}</td><td>{e(r["volume"])}</td><td>{e(r["growth"]) if r["growth"] else "未采集"}</td><td>{r["status"]}</td><td>{e(r["started"])}<br>{e(r["ended"]) if r["ended"] else "未结束"}</td><td><details><summary>展开</summary><p style="min-width:240px;max-width:480px">{related}</p></details></td></tr>'
    body+='</tbody></table></div><p><button id="more" style="padding:10px 20px">再显示100条</button></p></section><footer>数据：Google Trends 官方导出。CSV为空的结束时间按本次页面状态解释为活跃。各主题搜索量不可相加作为去重总量。CSV不提供增长率，只有首页25条补充了可见值。链接在Google Explore中可能需要加载或遇到访问限制。原始CSV保留未改动。</footer>'
    body+='''<script>const rr=[...document.querySelectorAll('#records tr')],q=document.querySelector('#searchInput'),s=document.querySelector('#statusFilter');let limit=100;function filter(){let n=0;rr.forEach(r=>{const ok=r.textContent.toLowerCase().includes(q.value.trim().toLowerCase())&&(!s.value||r.dataset.status===s.value);r.hidden=!(ok&&++n<=limit)});document.querySelector('#counter').textContent=`匹配 ${n} 条，显示 ${Math.min(n,limit)} 条`;document.querySelector('#more').hidden=n<=limit}q.oninput=s.onchange=()=>{limit=100;filter()};document.querySelector('#more').onclick=()=>{limit+=100;filter()};filter();</script>'''
    (ROOT/f'{day}.html').write_text(page('Google 美国趋势 · '+day,body),encoding='utf-8')
    entries.append({'date':day,'week':week,'count':len(rows)})
index='<header><div class="eyebrow">GOOGLE TRENDS · WEEKLY ARCHIVE</div><h1>Google 美国趋势档案</h1><p>每周一北京时间15:00 · 与 Pinterest 同期采集</p><nav><a href="../pinterest-trends-us/index.html">Pinterest 历史周报</a></nav></header><section><h2>按周查询</h2>'+table(['周次','采集日期','记录数','原始数据'],[[e(r['week']),f'<a href="{r["date"]}.html">{r["date"]} 首期报告 →</a>',str(r['count']),f'<a href="{r["date"]}.csv">CSV</a>'] for r in entries])+'</section>'
(ROOT/'index.html').write_text(page('Google 美国趋势档案',index),encoding='utf-8')
(ROOT/'archive.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps({'reports':len(entries),'rows':len(rows),'unique':unique,'active':active,'consumer_candidates':len(picks)}))
