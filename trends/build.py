"""Build a standalone multi-source dashboard from immutable source snapshots."""
import json,re,unicodedata
from pathlib import Path
from datetime import date
ROOT=Path(__file__).resolve().parent
rows=[]
modules={'focus':'焦点趋势','search':'搜索趋势','shopping':'购物趋势','moments':'节日专题入口','editorial':'编辑推荐','predicts':'年度预测'}
def norm(s): return ' '.join(unicodedata.normalize('NFKC',s).casefold().split())
def add(source,day,name,raw,**kw):
    iso=date.fromisoformat(day).isocalendar()
    rows.append(dict(id=f'{source}-{day}-{len(rows)}',source=source,date=day,week=f'{iso.year}-W{iso.week:02}',name=name,key=norm(name),raw=raw,**kw))
for path in sorted((ROOT.parent/'google-trends-us').glob('????-??-??.json')):
 d=json.loads(path.read_text()); day=path.stem
 for r in d['items']:
  add('Google',day,r['name'],r,zh='',module='实时热搜',category='消费候选' if r.get('consumer_candidate') else '未分类',scope='US',collected=d.get('collected_at'),period=d.get('window','未提供'),url=r['url'],report=f'../google-trends-us/{day}.html',metrics={'搜索量级':r.get('volume'),'平台增长率':r.get('growth')},status=r.get('status','未提供'))
for path in sorted((ROOT.parent/'pinterest-trends-us').glob('????-??-??.json')):
 d=json.loads(path.read_text()); day=path.stem
 for mod,label in modules.items():
  block=d.get(mod,{})
  for r in block.get('items',[]):
   metrics={}
   for key,caption in [('weekly_change','周变化'),('monthly_change','月变化'),('yearly_change','年变化')]:
    if key in r: metrics[caption]=r[key]
   common=dict(zh=r.get('zh',r['name'] if r.get('name_en') else ''),module=label,category=r.get('category') or ('消费候选' if mod=='shopping' else '未分类'),scope='全球预测' if mod=='predicts' else 'US',collected=d.get('collected_at'),period=r.get('chart_period') or block.get('period') or ('2026年度预测' if mod=='predicts' else '未提供'),url=r.get('url') or d['source'],report=f'../pinterest-trends-us/{day}.html',metrics=metrics,status='预测' if mod=='predicts' else ('仅入口' if mod=='moments' else '已采集'),metric_note=block.get('metric','未提供定量指标'))
   add('Pinterest',day,r.get('name_en') or r['name'],r,**common)
   for word in r.get('keywords',[]):
    add('Pinterest',day,word,{'name':word,'parent':r['name']},**{**common,'zh':'','module':'编辑关联词','metrics':{},'metric_note':'编辑推荐关联词；未提供增长率'})
# Semantic groups are editorial associations, never synonym equivalence.
rules=[('thanksgiving','感恩节 · 关联主题',r'thanksgiving|friendsgiving|感恩节'),('christmas','圣诞 · 关联主题',r'christmas|圣诞'),('black-friday','黑五 · 关联主题',r'black friday|黑五')]
for r in rows:
 r['theme']=None
 for key,label,pattern in rules:
  if re.search(pattern,r['name'],re.I): r['theme']={'key':key,'label':label,'rule':pattern};break
payload={'records':rows,'weeks':sorted({r['week'] for r in rows},reverse=True),'rules':[{'key':k,'label':l,'pattern':p} for k,l,p in rules]}
text=json.dumps(payload,ensure_ascii=False,separators=(',',':'))
(ROOT/'data.json').write_text(text)
html=(ROOT/'template.html').read_text().replace('__DATA__',text.replace('<','\\u003c'))
(ROOT/'index.html').write_text(html)
print(json.dumps({'records':len(rows),'Google':sum(r['source']=='Google' for r in rows),'Pinterest':sum(r['source']=='Pinterest' for r in rows),'weeks':payload['weeks']}))
