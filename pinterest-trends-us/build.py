"""Build offline HTML reports and a weekly archive from dated JSON snapshots."""
import json
from pathlib import Path
from datetime import date
from html import escape

ROOT = Path(__file__).resolve().parent
MODULES = [('focus','焦点 Topic'),('search','搜索热词'),('shopping','购物趋势'),('editorial','编辑推荐'),('moments','节日专题'),('predicts','年度预测')]
def esc(v): return escape(str(v if v is not None else '未提供'), quote=True)
def link(url, label):
    if not str(url).startswith(('https://', 'http://')): return esc(label)
    return f'<a href="{esc(url)}" target="_blank" rel="noopener noreferrer">{esc(label)} ↗</a>'
def table(headers, rows):
    return '<div class="scroll"><table><thead><tr>'+''.join('<th>'+esc(h)+'</th>' for h in headers)+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+c+'</td>' for c in row)+'</tr>' for row in rows)+'</tbody></table></div>'
STYLE = '''*{box-sizing:border-box}body{margin:0;background:#f5f3ef;color:#23282b;font:15px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif}main{max-width:1200px;margin:auto;padding:44px 26px 80px}a{color:#15695e;text-underline-offset:4px}header{border-bottom:1px solid #d6d9d3;padding-bottom:28px;margin-bottom:26px}.eyebrow{font-size:12px;letter-spacing:2px;color:#6a7470}h1{font-size:38px;line-height:1.25;margin:12px 0}h2{font-size:23px;margin:0 0 10px}p{margin:10px 0}.muted{color:#65716c}.stats{display:grid;grid-template-columns:repeat(6,1fr);gap:12px;margin:24px 0}.stat,section{background:#fff;border:1px solid #e0e3dd;border-radius:14px;padding:22px}.stat strong{display:block;font-size:30px}.stat span{font-size:13px;color:#65716c}section{margin:20px 0;scroll-margin-top:20px}.scroll{overflow:auto}table{border-collapse:collapse;width:100%;font-size:14px;text-align:left}td,th{padding:13px 12px;border-bottom:1px solid #edf0eb;vertical-align:top}th{white-space:nowrap;color:#68736c;font-size:12px;background:#f7f9f6}tr:last-child td{border-bottom:0}td:first-child{font-weight:550}nav{display:flex;gap:18px;flex-wrap:wrap;margin:18px 0}.tag{display:inline-block;border-radius:7px;background:#edf5f1;color:#276253;padding:3px 9px;font-size:12px}.note{border-left:3px solid #cf955a;padding:12px 18px;background:#fff7eb}.controls{display:flex;gap:12px;margin:22px 0;flex-wrap:wrap}input,select{font:inherit;padding:10px 14px;border:1px solid #cbd4cb;border-radius:8px;background:white}input{flex:1;min-width:200px}ul{padding-left:22px}.empty{display:none}footer{margin-top:28px;color:#65716c;font-size:13px}@media(max-width:760px){main{padding:24px 14px}h1{font-size:29px}.stats{grid-template-columns:repeat(3,1fr)}section{padding:16px}.stat{padding:14px}td,th{padding:10px 8px}}@media print{body{background:white}.controls,nav{display:none}section{break-inside:avoid}.scroll{overflow:visible}main{padding:0}}'''
SCRIPT = '''const query=document.querySelector('#query');if(query){query.addEventListener('input',()=>{const q=query.value.toLowerCase().trim();let count=0;document.querySelectorAll('tbody tr').forEach(r=>{const show=r.textContent.toLowerCase().includes(q);r.hidden=!show;if(show)count++});document.querySelector('#result').textContent=q?'匹配 '+count+' 条记录':''})}const week=document.querySelector('#week');if(week){week.addEventListener('change',()=>{document.querySelectorAll('tbody tr').forEach(r=>r.hidden=!!week.value&&r.dataset.week!==week.value)})}'''
def page(title, body):
    return '<!doctype html><html lang="zh-CN"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>'+esc(title)+'</title><style>'+STYLE+'</style><main>'+body+'</main><script>'+SCRIPT+'</script></html>'
def build_report(d, day, week):
    body=f'<header><div class="eyebrow">PINTEREST TRENDS · UNITED STATES</div><h1>美国趋势周报</h1><p>{day} · {week} <span class="tag">'+('首期基线' if d.get('baseline') else '每周采集')+'</span></p><p class="muted">采集时间：'+esc(d['collected_at'])+'</p><nav><a href="index.html">← 历史周报</a><a href="'+day+'.json" download>下载原始 JSON</a>'+link(d['source'],'Pinterest 来源')+'</nav></header>'
    body+='<div class="stats">'+''.join(f'<div class="stat"><strong>{len(d.get(k,{}).get("items",[]))}</strong><span>{n}</span></div>' for k,n in MODULES)+'</div>'
    body+='<p class="note">'+esc(d.get('coverage',''))+'</p>'
    if d.get('baseline'):
        body+='<section><h2>本期观察</h2><p>圣诞公寓装饰月增长 500%，圣诞窗户彩绘增长 200%。节日装饰与手工派对同时出现在焦点主题和编辑推荐中，值得持续跟踪。秋冬美甲、麂皮与半身裙穿搭也是本期选题线索。</p><p class="muted">以上为编辑分析，不是平台综合排名。本期建立历史基线，尚无两次采集之间的周对比。</p></section>'
    elif d.get('summary'):
        body+='<section><h2>本期观察与变化</h2><p>'+esc(d['summary'])+'</p></section>'
    body+='<nav>'+''.join(f'<a href="#{k}">{n}</a>' for k,n in MODULES)+'</nav><div class="controls"><input id="query" aria-label="搜索报告" placeholder="搜索英文主题、中文类别或关键词…"><span id="result" aria-live="polite"></span></div>'
    for k,n in MODULES:
        m=d.get(k,{}); items=m.get('items',[])
        body+=f'<section id="{k}"><h2>{n} <span class="tag">{len(items)} 条</span></h2>'
        notes=[m.get(x) for x in ('metric','period','note','scope','coverage') if m.get(x)]
        if notes: body+='<p class="muted">'+esc(' · '.join(notes))+'</p>'
        if k=='focus':
            headers=['排名','Topic / 中文','类别','月增长']; rows=[[esc(r['rank']),esc(r['name'])+'<br><span class="muted">'+esc(r.get('zh'))+'</span>',esc(r.get('category')),esc(r.get('monthly_change'))] for r in items]
        elif k=='search':
            headers=['关键词 / 中文','周变化','月变化','年变化']; rows=[[esc(r['name'])+'<br><span class="muted">'+esc(r.get('zh'))+'</span>',esc(r.get('weekly_change')),esc(r.get('monthly_change')),esc(r.get('yearly_change'))] for r in items]
            body+='<p class="muted">统计起止日：'+esc(m.get('period'))+'。增长率不代表绝对搜索量。</p>'
        elif k=='shopping':
            headers=['排名','产品类别','月增长','预测功能','图表区间']; rows=[[esc(r['rank']),esc(r['name']),esc(r.get('monthly_change')),'可用' if r.get('prediction_available') else '未标示',esc(r.get('chart_period'))] for r in items]
        elif k=='editorial':
            headers=['主题','类别','关联关键词']; rows=[[link(r['url'],r['name']),esc(r.get('category')),'<br>'.join(esc(w) for w in r.get('keywords',[]))] for r in items]
        elif k=='moments':
            headers=['专题','英文名称','采集范围']; rows=[[link(r['url'],r['name']),esc(r.get('name_en')),'公开专题入口'] for r in items]
        else:
            headers=['序号','年度主题','口径']; rows=[[str(i+1),link(r['url'],r['name']),'全球年度预测参考'] for i,r in enumerate(items)]
        body+=table(headers,rows)+'</section>'
    body+='<section><h2>数据说明</h2><ul>'+''.join('<li>'+esc(v)+'</li>' for v in d.get('limitations',[]))+'</ul></section><footer>采集与分析报告 · 历史数据按采集日期保留 · 所有百分比保留来源显示口径</footer>'
    return page(day+' · Pinterest 美国趋势周报',body)

def main():
    entries=[]
    for path in sorted(ROOT.glob('????-??-??.json'),reverse=True):
        day=path.stem; iso=date.fromisoformat(day).isocalendar(); week=f'{iso.year}-W{iso.week:02}'
        d=json.loads(path.read_text()); count=sum(len(d.get(k,{}).get('items',[])) for k,_ in MODULES)
        (ROOT/f'{day}.html').write_text(build_report(d,day,week),encoding='utf-8')
        entries.append({'date':day,'week':week,'file':f'{day}.html','count':count,'baseline':d.get('baseline',False)})
    body='<header><div class="eyebrow">TREND INTELLIGENCE · WEEKLY ARCHIVE</div><h1>Pinterest 美国趋势档案</h1><p class="muted">每周一下午 3 点（北京时间）采集 · 六类趋势 · 按周回查历史报告</p></header>'
    if entries: body+='<p><a href="'+entries[0]['file']+'">打开最新一期 → '+entries[0]['date']+'</a></p>'
    body+='<div class="controls"><label for="week">选择周次 </label><select id="week"><option value="">全部周次</option>'+''.join('<option>'+w+'</option>' for w in dict.fromkeys(e['week'] for e in entries))+'</select></div><section><h2>历史报告</h2><p class="muted">按 ISO 周归档；同周多次采集分别保留。首期为周五补采基线。</p><div class="scroll"><table><thead><tr><th>采集日期</th><th>周次</th><th>模块条目</th><th>报告类型</th><th>原始数据</th></tr></thead><tbody>'
    for e in entries:
        body+=f'<tr data-week="{e["week"]}"><td><a href="{e["file"]}">{e["date"]} →</a></td><td>{e["week"]}</td><td>{e["count"]}</td><td>'+('首期基线' if e['baseline'] else '周报')+f'</td><td><a href="{e["date"]}.json" download>JSON</a></td></tr>'
    body+='</tbody></table></div></section><p class="note">公开预览与完整列表的覆盖范围以各期报告为准。年度预测单独标注全球口径。跨模块条目可能重叠。</p>'
    (ROOT/'index.html').write_text(page('Pinterest 美国趋势 · 历史周报',body),encoding='utf-8')
    (ROOT/'archive.json').write_text(json.dumps(entries,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(f'Built {len(entries)} reports and archive index.')
if __name__=='__main__': main()
