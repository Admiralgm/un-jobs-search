#!/usr/bin/env python3
"""Workday scraper v2 — IMF, WFP, UNHCR, WTO"""
import asyncio, re, sys
from datetime import datetime, date
from pathlib import Path
from scrapling.fetchers import StealthyFetcher

BASE_DIR=Path("~/Downloads/DATA_REPOSITORY/WORKDIR/JD_FILES"); CONCURRENT=4

ICT_KW=[" it "," ict "," isp "," ai "," artificial "," telecom "," connectivity "," innovation ","information technology","chief technology"," cto "," chief information "," cio "," digital transformation "," digital officer "," systems administrator "," network engineer "," network administrator "," software engineer "," software developer "," data engineer "," data scientist "," cybersecurity "," information security "," devops "," cloud engineer "," cloud architect "," database administrator "," web developer "," full stack "," machine learning "," deep learning "," solutions architect "," enterprise architect "," technical lead ","it officer","it specialist","it manager","ict officer","ict specialist","ict coordinator","ai engineer","ai research","telecommunications","innovation officer","digital specialist","digital officer","digital advisor","tech lead","technology officer","technology specialist","system administrator","systems engineer","platform engineer","fullstack","front-end developer","backend developer","cloud computing","data analyst","data analytics","business intelligence","information management","knowledge management","infrastructure engineer","site reliability","devsecops","machine learning engineer","natural language processing","computer vision","robotics engineer","automation engineer","blockchain","distributed systems","microservices","api developer","integration engineer","middleware","erp consultant","crm consultant","business analyst it","it project manager","it director","head of it","head of digital","chief digital","digital innovation","emerging technology","technology strategy","it strategy","it governance","information systems","management information","gis specialist","geospatial","spatial data","data warehouse","data lake","etl developer","bi developer","business intelligence developer","report developer","database developer","sql developer","python developer","java developer","javascript developer","web application","mobile developer","app developer","ui designer","ux designer","product designer digital","technology for development","digital development","digital health","e-health","mhealth","telemedicine","fintech","digital finance","mobile money","internet of things","iot developer","embedded systems","firmware engineer","hardware engineer it","quantum computing","high performance computing","hpc","data center","data centre","network operations","noc engineer","it support","help desk","technical support it","it procurement","it asset management","digital platform","platform developer","developer platform","open source developer","freelance developer web","engineer","developer","technology","digital","cyber","software","data","cloud","full stack","fullstack","data strategist","it strategist","data governance","it governance","information governance"]
HARD_REJECT = re.compile(
    r"(audit|agricultur|pedagog|wash specialist|maintenance|warehouse|"
    r"admin officer|driver|translator|unpaid|cleaner|hr officer|accountant|"
    r"stagiaire|child protection|interpreter|cook|security officer|volunteer|"
    r"doctor|gender|civil engineer|procurement|human rights|logistics|"
    r"supply chain|plumber|fleet|intern|shelter|medical|budget officer|"
    r"sanitation engineer|nurse|midwife|nutrition|teacher|human resources|"
    r"electrician|finance officer)", re.I)

def is_ict_title(title):
    t=" "+title.lower()+" "
    return any(kw in t for kw in ICT_KW)
def is_ict_full(title,body): return any(kw in (title+" "+body[:3000]).lower() for kw in ICT_KW)
def sanitize(name): return re.sub(r'\s+','_',re.sub(r'[^a-zA-Z0-9\-_\s]','',name).strip())[:60]

PORTALS = {
    "imf": {"dir":"UN_IMF","base":"https://imf.wd5.myworkdayjobs.com","list":"https://imf.wd5.myworkdayjobs.com/IMF","prefix":"IMF"},
    "wfp": {"dir":"UN_WFP","base":"https://wd3.myworkdaysite.com","list":"https://wd3.myworkdaysite.com/recruiting/wfp/job_openings","prefix":"WFP"},
    "unhcr": {"dir":"UN_UNHCR","base":"https://unhcr.wd3.myworkdayjobs.com","list":"https://unhcr.wd3.myworkdayjobs.com/en-GB/External","prefix":"UNHCR"},
    "wto": {"dir":"UN_WTO","base":"https://careers.smartrecruiters.com","list":"https://careers.smartrecruiters.com/WTO","prefix":"WTO","type":"smartrecruiters"},
}

async def scrape(portal_id):
    cfg=PORTALS[portal_id]; d=BASE_DIR/cfg["dir"]; d.mkdir(exist_ok=True)
    prefix=cfg["prefix"]
    print(f"\n{prefix} v2.0 {datetime.now():%Y-%m-%d %H:%M:%S}")
    
    existing=set()
    for f in d.glob(f"{prefix}_*.md"):
        parts=f.stem.split("_",2)
        if len(parts)>=2: existing.add(parts[1])
    print(f"Existing: {len(existing)}")
    
    try:
        page=await StealthyFetcher.async_fetch(cfg["list"],headless=True,disable_resources=True,wait=5000)
        if page.status!=200: print(f"Status: {page.status}"); return
        
        if cfg.get("type")=="smartrecruiters":
            # SmartRecruiters links
            all_links=re.findall(r'href="(https://jobs\.smartrecruiters\.com/WTO/[^"]+)"',page.html_content)
            jobs=[]
            seen=set(existing)
            for url in all_links:
                jid=re.search(r'/([^/]+)/?$',url)
                jid=jid.group(1) if jid else url
                if jid not in seen:
                    seen.add(jid)
                    title=re.search(r'/([^/]+)/?$',url).group(1).replace('-',' ').title()
                    jobs.append((jid,title,url))
        else:
            # Workday links: /en-US/.../job/Location/Title_ID where ID can be 26-R9291 or JR123407
            all_links=re.findall(r'href="((?:/en-US|/en-GB|/en)[^"]*/job/[^"]+_([\w-]+))"',page.html_content)
            
            text=page.get_all_text()
            jobs=[]
            seen=set(existing)
            for url_path,jid in all_links:
                if jid in seen: continue
                seen.add(jid)
                # Get title from anchor text
                title_m=re.search(r'href="'+re.escape(url_path)+r'"[^>]*>(.*?)</a>',page.html_content,re.S)
                title=re.sub(r'<[^>]+>','',title_m.group(1)).strip() if title_m else f"{prefix}-{jid}"
                full_url=cfg["base"]+url_path
                jobs.append((jid,title,full_url))
        
        print(f"Jobs found: {len(jobs)}")
        ict=[(j,t,u) for j,t,u in jobs if is_ict_title(t) or not HARD_REJECT.search(t)]
        print(f"ICT: {len(ict)}")
        for j,t,u in ict: print(f"  {j}: {t[:70]}")
        
        saved=0; sem=asyncio.Semaphore(CONCURRENT)
        for i in range(0,len(ict),CONCURRENT*2):
            batch=ict[i:i+CONCURRENT*2]
            tasks=[]
            for jid,title,url in batch:
                async def fetch(u=url,j=jid):
                    try:
                        async with sem:
                            p=await StealthyFetcher.async_fetch(u,headless=True,disable_resources=True,wait=4000)
                        return (j,p.get_all_text()) if p.status==200 and len(p.get_all_text())>=500 else None
                    except: return None
                tasks.append(fetch())
            for idx,res in enumerate(await asyncio.gather(*tasks)):
                jid,title,url=batch[idx]
                if not res: continue
                if not is_ict_full(title,res[1]): continue
                out=d/f"{prefix}_{jid}_{sanitize(title)[:60]}.md"
                if out.exists(): continue
                out.write_text(f"# {title}\n\n**Job ID:** {jid}\n**URL:** {url}\n**Scraped:** {datetime.now():%Y-%m-%d %H:%M}\n\n---\n\n{res[1]}",encoding="utf-8")
                saved+=1; print(f"SAVED: {jid} — {title[:60]}")
        print(f"DONE: {saved} saved")
    except Exception as e: print(f"ERROR: {e}")

async def main():
    portal=sys.argv[1] if len(sys.argv)>1 else "imf"
    await scrape(portal)

import sys
if __name__=="__main__": asyncio.run(main())
