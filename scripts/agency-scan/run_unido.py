#!/usr/bin/env python3
"""UNIDO SuccessFactors — careers.unido.org"""
import asyncio, re
from datetime import datetime, date
from pathlib import Path
from scrapling.fetchers import StealthyFetcher

BASE_DIR=Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES"); DIR=BASE_DIR/"UN_UNIDO"; CONCURRENT=4
HARD_REJECT=re.compile(r"(intern|stagiaire|volunteer|unpaid|nutrition|agricultur|wash specialist|sanitation engineer|civil engineer|shelter|procurement|human rights|medical|doctor|nurse|midwife|teacher|pedagog|child protection|gender|accountant|finance officer|budget officer|audit|hr officer|human resources|admin officer|logistics|supply chain|warehouse|fleet|security officer|driver|interpreter|translator|cook|cleaner|maintenance|electrician|plumber)",re.I)
ICT_KW=[" it "," ict "," isp "," ai "," artificial "," telecom "," connectivity "," innovation ","information technology","chief technology"," cto "," chief information "," cio "," digital transformation "," digital officer "," systems administrator "," network engineer "," network administrator "," software engineer "," software developer "," data engineer "," data scientist "," cybersecurity "," information security "," devops "," cloud engineer "," cloud architect "," database administrator "," web developer "," full stack "," machine learning "," deep learning "," solutions architect "," enterprise architect "," technical lead ","it officer","it specialist","it manager","ict officer","ict specialist","ict coordinator","ai engineer","ai research","telecommunications","innovation officer","digital specialist","digital officer","digital advisor","tech lead","technology officer","technology specialist","system administrator","systems engineer","platform engineer","fullstack","front-end developer","backend developer","cloud computing","data analyst","data analytics","business intelligence","information management","knowledge management","infrastructure engineer","site reliability","devsecops","machine learning engineer","natural language processing","computer vision","robotics engineer","automation engineer","blockchain","distributed systems","microservices","api developer","integration engineer","middleware","erp consultant","crm consultant","business analyst it","it project manager","it director","head of it","head of digital","chief digital","digital innovation","emerging technology","technology strategy","it strategy","it governance","information systems","management information","gis specialist","geospatial","spatial data","data warehouse","data lake","etl developer","bi developer","business intelligence developer","report developer","database developer","sql developer","python developer","java developer","javascript developer","web application","mobile developer","app developer","ui designer","ux designer","product designer digital","technology for development","digital development","digital health","e-health","mhealth","telemedicine","fintech","digital finance","mobile money","internet of things","iot developer","embedded systems","firmware engineer","hardware engineer it","quantum computing","high performance computing","hpc","data center","data centre","network operations","noc engineer","it support","help desk","technical support it","it procurement","it asset management","digital platform","platform developer","developer platform","open source developer","freelance developer web"]
def is_ict_title(title):
    t=" "+title.lower()+" "
    return any(kw in t for kw in ICT_KW)
def is_ict_full(title,body): return any(kw in (title+" "+body[:1000]).lower() for kw in ICT_KW)
def sanitize(name): return re.sub(r'\s+','_',re.sub(r'[^a-zA-Z0-9\-_\s]','',name).strip())[:60]
def clean_expired():
    if not DIR.exists(): return 0
    today=date.today(); removed=0
    for f in DIR.glob("UNIDO_*.md"):
        try:
            m=re.search(r'(?:closing|deadline)\s*[:\\s]\s*(\d{4}-\d{2}-\d{2}|\d{1,2}\s+\w+\s+\d{4})',f.read_text("utf-8",errors="ignore"),re.I)
            if m:
                raw=m.group(1).replace(',','')
                try:
                    dl=datetime.strptime(raw,"%Y-%m-%d").date()
                    if dl<today: f.unlink(); removed+=1
                except: pass
        except: pass
    return removed
def extract_jobs_sf(html):
    """Extract jobs from SuccessFactors search results. Format: /job/Title/NUMERIC_ID/"""
    results={}
    for url,jid,reftitle in re.findall(r'<a[^>]*href="(/job/[^"]+/(\d{6,})[^"]*)"[^>]*>(.*?)</a>',html,re.S):
        title=re.sub(r'<[^>]+>','',reftitle).strip()
        if title and len(title)>5 and jid not in results: results[jid]=(jid,title,url)
    return list(results.values())
async def fetch_job(sem,jid,url):
    try:
        async with sem:
            page=await StealthyFetcher.async_fetch(f"https://careers.unido.org{url}",headless=True,disable_resources=True,wait=4000)
    except: return None
    if page.status!=200: return None
    text=page.get_all_text()
    return (jid,text) if len(text)>=500 else None
async def main():
    DIR.mkdir(exist_ok=True)
    print(f"UNIDO v1.0 {datetime.now():%Y-%m-%d %H:%M:%S}")
    r=clean_expired(); print(f"Expired removed: {r}")
    existing=set(f.stem.split("_",2)[1] for f in DIR.glob("UNIDO_*.md") if f.stem.split("_",2)[1].isdigit())
    print(f"Existing: {len(existing)}")
    KEYWORDS=["Digital","AI","IT","Innovation","Technology","Data"]
    all_candidates=[]; seen=set(existing)
    sem=asyncio.Semaphore(CONCURRENT)
    for kw in KEYWORDS:
        try:
            page=await StealthyFetcher.async_fetch(f"https://careers.unido.org/search/?q={kw}",headless=True,disable_resources=True,wait=4000)
            if page.status!=200: continue
            jobs=extract_jobs_sf(page.html_content)
            new=[(j,t,u) for j,t,u in jobs if j not in seen]; seen.update(j for j,_,_ in jobs)
            passing=[(j,t,u) for j,t,u in new if is_ict_title(t)]
            all_candidates.extend(passing)
            print(f"kw={kw}: {len(jobs)} jobs, {len(new)} new, {len(passing)} ICT")
        except Exception as e: print(f"kw={kw}: {e}")
    # dedup
    d={}; [(d.update({j:(j,t,u)})) for j,t,u in all_candidates]
    unique=list(d.values())
    print(f"Candidates: {len(unique)}")
    saved=0
    for i in range(0,len(unique),CONCURRENT*2):
        batch=unique[i:i+CONCURRENT*2]
        tasks=[fetch_job(sem,j,u) for j,t,u in batch]
        for idx,res in enumerate(await asyncio.gather(*tasks)):
            jid,title,url=batch[idx]
            if not res: continue
            if not is_ict_full(title,res[1]): continue
            out=DIR/f"UNIDO_{jid}_{sanitize(title)[:60]}.md"
            if out.exists(): continue
            out.write_text(f"# {title}\n\n**Job ID:** {jid}\n**URL:** https://careers.unido.org{url}\n**Scraped:** {datetime.now():%Y-%m-%d %H:%M}\n\n---\n\n{res[1]}",encoding="utf-8")
            saved+=1; print(f"SAVED: {jid} — {title[:60]}")
    print(f"DONE: {saved} saved, files: {len(list(DIR.glob('UNIDO_*.md')))}")
if __name__=="__main__": asyncio.run(main())
