"""Build the bilingual, dependency-free GitHub Pages portfolio."""
from pathlib import Path
from html import escape
import json,re,math,textwrap

ROOT=Path(__file__).resolve().parents[1]
projects=json.loads((ROOT/'content/projects.json').read_text(encoding='utf8'))
papers=json.loads((ROOT/'content/publications.json').read_text(encoding='utf8'))
ed=json.loads((ROOT/'content/editorial.json').read_text(encoding='utf8'))
BASE='https://dhkim-kr.github.io'
LANG='ko'
def t(ko,en):return ko if LANG=='ko' else en
def e(v):return escape(str(v),quote=True)
def local(v):return v.get(LANG,v.get('ko','')) if isinstance(v,dict) else v
def route(p='/'):return ('/en' if LANG=='en' else '')+p
def a(url,label,cls=''):
    ext=url.startswith('http');attrs=' target="_blank" rel="noopener noreferrer"' if ext else ''
    return f'<a href="{e(url)}"{attrs}'+(f' class="{e(cls)}"' if cls else '')+f'>{e(label)}</a>'
SOCIAL=[('https://scholar.google.com/citations?user=CcqJMb0AAAAJ','Google Scholar'),('https://github.com/dhkim-kr','GitHub'),('https://orcid.org/0009-0005-7105-0894','ORCID'),('https://www.linkedin.com/in/dhkim-kr','LinkedIn')]
def socials(email=True):return '<div class="link-list">'+(a('mailto:dhkim1016@kw.ac.kr','Email') if email else '')+''.join(a(u,l) for u,l in SOCIAL)+'</div>'
def header(path):
    alt=('/en'+path) if LANG=='ko' else path
    return f'''<a class="skip" href="#main">{t('본문 바로가기','Skip to content')}</a><header class="site-header"><div class="wrap header-inner"><a class="brand" href="{route('/')}">Dae Hyeon Kim <span>RESEARCH</span></a><button class="menu-button" type="button" aria-expanded="false" aria-controls="main-nav">{t('메뉴','Menu')}</button><nav class="main-nav" id="main-nav" aria-label="{t('주 메뉴','Main navigation')}">{a(route('/#about'),t('소개','About'))}{a(route('/projects/'),t('프로젝트','Projects'))}{a(route('/publications/'),t('논문','Publications'))}{a(route('/#experience'),t('경력','Experience'))}{a(route('/#contact'),t('연락처','Contact'))}</nav><a class="language" href="{alt}" lang="{t('en','ko')}" hreflang="{t('en','ko')}" aria-label="{t('Switch to English','한국어로 보기')}">{t('EN','한국어')}</a></div></header>'''
def footer():return f'''<footer class="footer" id="contact"><div class="wrap"><div class="footer-top"><div><p class="eyebrow">CONTACT</p><h2>{t('연구 및 협업 연락처','Research & collaboration')}</h2>{a('mailto:dhkim1016@kw.ac.kr','dhkim1016@kw.ac.kr','mail')}<p class="affiliation">{t('광운대학교 전자통신공학과, NeuroAI Lab<br>서울, 대한민국','NeuroAI Lab, Kwangwoon University<br>Seoul, Republic of Korea')}</p></div>{socials(False)}</div><div class="footer-bottom"><span>© 2026 Dae Hyeon Kim</span><span>{t('연구 정보 기준: 2026년 9월','Research information as of September 2026')}</span></div></div></footer>'''
def page(path,title,description,body):
    full=route(path);out=ROOT/full.lstrip('/')/'index.html';out.parent.mkdir(parents=True,exist_ok=True)
    html=f'''<!doctype html><html lang="{LANG}"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>{e(title)} | Dae Hyeon Kim</title><meta name="description" content="{e(description)}"><link rel="canonical" href="{BASE+full}"><link rel="alternate" hreflang="ko" href="{BASE+path}"><link rel="alternate" hreflang="en" href="{BASE+'/en'+path}"><link rel="alternate" hreflang="x-default" href="{BASE+path}"><meta name="theme-color" content="#ffffff"><meta property="og:title" content="{e(title)}"><meta property="og:description" content="{e(description)}"><meta property="og:type" content="website"><meta property="og:url" content="{BASE+full}"><link rel="icon" href="/assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="/assets/site.css"><script src="/assets/site.js" defer></script></head><body>{header(path)}<main id="main">{body}</main>{footer()}</body></html>'''
    out.write_text(html.replace('><','>\n<'),encoding='utf8')
def section_head(num,ko,en,href=None,label=None):return f'<div class="section-head"><div><p class="eyebrow">{num}</p><h2>{t(ko,en)}</h2></div>'+(a(href,label,'text-link') if href else '')+'</div>'
def paper_role(p):return p['role'] if LANG=='ko' else {'제1저자':'First author','공동제1저자':'Co-first author','제2저자':'Second author','제2저자 (발표자)':'Second author, presenter'}.get(p['role'],p['role'])
def paper_status(p):return p['status'] if LANG=='ko' else {'게재':'Published','게재 확정':'Accepted','게재 (Early Access)':'Published, Early Access','심사 중':'Under review','투고 예정':'In preparation','구두':'Oral presentation','포스터':'Poster presentation'}[p['status']]
def paper_links(p):return ''.join(a(u,'DOI' if 'doi.org/' in u else t('연구 저장소','Research repository')) for u in p['links'])
def publication_row(p):
    return f'<li class="publication-row"><div class="publication-year">{p["year"]}</div><div><h3>{a(route("/publications/"+p["slug"]+"/"),p["title"])}</h3><div class="publication-meta"><span>{e(p["venue"])}</span><span>{e(paper_role(p))}</span><span class="status">{e(paper_status(p))}</span></div><div class="publication-links">{a(route("/publications/"+p["slug"]+"/"),t('연구 상세','Read study'))}{paper_links(p)}</div></div></li>'
def project_row(p,i=0):
    url=route('/projects/'+p['slug']+'/');thumb=f'<img src="{p["thumbnail"]}" alt="{e(local(p["short"]))}" loading="lazy" width="220" height="150">' if p['thumbnail'] else f'<span class="index-number">{i+1:02}</span>'
    return f'<article class="project-row"><a class="thumb" href="{url}" tabindex="-1" aria-hidden="true">{thumb}</a><div><p class="category">{e(p["category"])}</p><h3>{a(url,local(p["short"]))}</h3><p class="summary">{e(local(p["summary"]))}</p><span class="role">{e(local(p["role"]))}</span></div></article>'
def archive_intro(title,description,bread):return f'<div class="page-intro"><div class="breadcrumb">{a(route("/"),t("홈","Home"))}<span>/</span><span>{e(bread)}</span></div><h1>{e(title)}</h1><p class="lead">{e(description)}</p></div>'
def home():
    hero=f'''<div class="wrap"><section class="hero" id="about"><div class="hero-copy"><p class="eyebrow">NEUROAI LAB / KWANGWOON UNIVERSITY</p><div class="hero-name"><h1>{t('김대현','Dae Hyeon Kim')}</h1><p class="name-en">{t('Dae Hyeon Kim','김대현 / Integrated M.S.–Ph.D. student')}</p></div><h2 class="hero-title">{t('그래프와 다중모달 학습의<br>강건성과 효율성을 연구합니다.','Robust and efficient learning<br>for graphs and multimodal data.')}</h2><p class="hero-intro">{t('적은 레이블과 변화하는 측정 환경에서도 유효한 관계를 학습하는 모델을 연구합니다. 생체신호 수집과 분석, 그래프 모델 설계, 실제 시스템 구현까지 연구를 수행해 왔습니다.','I study models that learn useful relationships from limited labels and changing measurement conditions. My work covers biosignal acquisition and analysis, graph learning, and implementation in research and deployed systems.')}</p>{socials()}</div><div class="portrait"><figure><img src="/assets/portrait.png" alt="{t('김대현 프로필 사진','Portrait of Dae Hyeon Kim')}" width="270" height="350" fetchpriority="high"><figcaption>{t('전자통신공학과 석박사통합과정<br>지도교수 최영석 / 2027.02 졸업 예정','Electronics and Communications Engineering<br>Advisor: Young-Seok Choi<br>Expected graduation: February 2027')}</figcaption></figure></div></section><div class="stats" aria-label="{t('연구 이력 요약','Research record')}">'''
    for n,ko,en in [('6','SCIE 게재 및 확정','SCIE published / accepted'),('7','국제학회 논문','International conference papers'),('8','정부과제 참여','Government-funded projects'),('4','기술 세부과제 리드','Technical work packages led')]:hero+=f'<div class="stat"><strong>{n}</strong><span>{t(ko,en)}</span></div>'
    hero+='</div>'
    topics=[('그래프 표현과 구조 학습','Graph representations and structure','표본과 채널의 관계를 적응적으로 구성하고, 준지도 대조학습과 구조적 희소성으로 적은 레이블과 관계 잡음을 다룹니다.','Adaptive sample and channel graphs, semi-supervised contrastive learning and structural sparsity for limited labels and noisy relationships.'),('다중모달 학습과 도메인 적응','Multimodal learning and domain adaptation','생체신호, 음성, 언어를 관계 기반으로 융합합니다. 교차모달 정렬을 통해 입력 결손과 피험자 및 세션 변화에 대응합니다.','Relation-aware fusion of biosignals, speech and language. Cross-modal alignment addresses missing inputs and subject or session changes.'),('경량 모델과 근거 기반 에이전트','Efficient models and evidence-based agents','경량 시간 모델과 공유 그래프 연산자를 연구하고, 관측 근거를 보존하는 상태 표현을 검색과 다중 에이전트 실행에 연결합니다.','Compact temporal models and shared graph operators, with observation-based state representations for retrieval and multi-agent execution.')]
    body=hero+'<section class="section" id="research">'+section_head('01 / RESEARCH','연구 분야','Research focus')+'<div class="research-grid">'
    for i,(ko,en,kp,ep) in enumerate(topics,1):body+=f'<div class="research-item"><span class="number">0{i}</span><h3>{t(ko,en)}</h3><p>{t(kp,ep)}</p></div>'
    body+='</div></section>'
    body+='<section class="section" id="projects">'+section_head('02 / PROJECTS','주요 프로젝트','Selected projects',route('/projects/'),t('전체 프로젝트 13개 보기','View all 13 projects'))+'<div class="project-list">'
    for slug in ['eeg-graph-learning','multimodal-emotion','kist-ultrasound','bcg-blood-pressure','neurosync','neurotruth']:body+=project_row(next(p for p in projects if p['slug']==slug))
    body+='</div></section>'
    body+='<section class="section" id="publications">'+section_head('03 / PUBLICATIONS','주요 논문','Selected publications',route('/publications/'),t('전체 논문 및 원고 보기','All publications and manuscripts'))+'<ol class="publication-list">'
    for slug in ['simnext-eeg','mda-gcl','asgcrl','emotionheart','sgcl','multiscale-entropy']:body+=publication_row(next(p for p in papers if p['slug']==slug))
    body+='</ol></section>'
    experiences=[('2022.03 – Present','석박사통합과정 / 대학원 연구원','Integrated M.S.–Ph.D. / Graduate research assistant','광운대학교 전자통신공학과, NeuroAI Lab. 지도교수 최영석. 2027.02 졸업 예정. GPA 4.50/4.50.','NeuroAI Lab, Kwangwoon University. Advisor: Young-Seok Choi. Expected February 2027. GPA 4.50/4.50.'),('2022.01 – 2022.02','NeuroAI 연구 인턴','Research intern, NeuroAI Lab','EEG 엔트로피와 연결성 기반 그래프 학습. 후속 MBE 논문 공동 제1저자.','EEG entropy and connectivity-based graph learning; co-first author of the subsequent MBE paper.'),('2021.01 – 2021.02','KIST 연구 인턴','Research intern, KIST','바이오닉스연구센터. CT/MRI 정합, 위치추적, 집속초음파 측정과 로봇 제어.','Bionics Research Center. CT/MRI registration, tracking, focused-ultrasound measurement and robotic control.'),('2020.09 – 2021.06','BCML 학부 연구 인턴','Undergraduate research intern, BCML','광운대학교. ECG, PPG, BCG 신호 수집과 혈압 추정. 산학연계 SW 프로젝트 공동 개발.','Kwangwoon University. ECG, PPG and BCG acquisition, blood-pressure estimation and industry-linked software development.'),('2016.03 – 2022.02','컴퓨터공학 학사','B.S. in Computer Engineering','광운대학교. GPA 3.86/4.50.','Kwangwoon University. GPA 3.86/4.50.')]
    body+='<section class="section" id="experience"><div class="split-section"><div><p class="eyebrow">04 / EXPERIENCE</p><h2>'+t('학력 및 연구 경력','Education & experience')+'</h2></div><ul class="timeline">'
    for date,ko,en,kp,ep in experiences:body+=f'<li><span class="date">{e(date)}</span><div><h3>{t(ko,en)}</h3><p>{t(kp,ep)}</p></div></li>'
    body+='</ul></div></section>'
    body+='<section class="section" id="awards">'+section_head('05 / SERVICE','수상과 학술 활동','Awards & academic service')+'<div class="service-grid"><div><h3>'+t('수상 및 연구 성과','Recognition')+'</h3><ul>'
    for ko,en in [('AI Champion 2026 일반 및 국내 AI 트랙 본선 진출','AI Champion 2026 main round in the regular and Korean-AI tracks'),('KOSOMBE 2024 우수 포스터상','KOSOMBE 2024 Best Poster Award'),('기업 기술이전 1건, 2,000만원','One technology transfer, KRW 20 million'),('6학기 등록금 전액 RA 장학금, 학부 성적우수 장학금 3회','Full-tuition RA scholarship for six semesters; three undergraduate merit scholarships')]:body+=f'<li>{t(ko,en)}</li>'
    body+='</ul></div><div><h3>'+t('심사와 교육','Reviewing & teaching')+'</h3><ul>'
    for ko,en in [('npj Artificial Intelligence, Scientific Reports, Cluster Computing 심사','Reviewer for npj Artificial Intelligence, Scientific Reports and Cluster Computing'),('IEEE 대학원생 회원, SPS 및 EMBS','IEEE Graduate Student Member; SPS and EMBS'),('Signals & Systems, Digital Signal Processing 조교','Teaching assistant: Signals & Systems and Digital Signal Processing'),('KW-VIP 및 학부생 21명 연구 튜토리얼','KW-VIP mentoring and research tutorials for 21 undergraduates'),('국내학회 논문 13편','13 domestic conference papers')]:body+=f'<li>{t(ko,en)}</li>'
    body+='</ul></div></div></section>'
    body+='<section class="section" id="news"><div class="split-section"><div><p class="eyebrow">06 / NEWS</p><h2>'+t('최근 연구 소식','Research updates')+'</h2></div><ul class="news-list">'
    for slug,ko,en in [('simnext-eeg','SimNeXt-EEG, IEEE Signal Processing Letters 게재','SimNeXt-EEG published in IEEE Signal Processing Letters'),('mda-gcl','MDA-GCL, Knowledge-Based Systems 게재 확정','MDA-GCL accepted at Knowledge-Based Systems'),('emotionheart','EmotionHeart, ICASSP 2026 제1저자 발표','First-author presentation of EmotionHeart at ICASSP 2026')]:body+=f'<li><time>2026</time><p>{a(route("/publications/"+slug+"/"),t(ko,en))}</p></li>'
    body+='</ul></div></section></div>'
    page('/',t('김대현 연구 프로필','Research profile'),t('그래프 학습, 다중모달 표현학습, 생체신호 분석과 경량 AI를 연구하는 김대현의 연구 프로필.','Research by Dae Hyeon Kim on graph learning, multimodal representations, biosignal analysis and efficient AI.'),body)
def archives():
    body='<div class="wrap">'+archive_intro(t('프로젝트','Projects'),t('연구 설계부터 구현과 평가까지, 프로젝트별 역할과 결과를 정리했습니다.','Project-specific methods, contributions and evidence, from research design to implementation and evaluation.'),t('프로젝트','Projects'))
    groups=[(t('국가과제 및 기업 공동 연구','Government-funded and industry research'),projects[:8]),(t('KIST 및 학부 연구 인턴','KIST and undergraduate internships'),projects[8:10]),('AI Champion 2026',projects[10:12]),(t('연구 인턴 및 후속 논문','Research internship and subsequent publication'),projects[12:])]
    for title,rows in groups:body+='<section class="archive-group"><h2>'+e(title)+'</h2><div class="project-list">'+''.join(project_row(p,i) for i,p in enumerate(rows))+'</div></section>'
    page('/projects/',t('프로젝트','Projects'),t('국가과제, KIST 및 학부 인턴, AI Champion 프로젝트 13개.','13 projects spanning funded research, internships and AI Champion.'),body+'</div>')
    body='<div class="wrap">'+archive_intro(t('논문 및 원고','Publications & manuscripts'),t('게재 및 확정 논문과 심사 중, 준비 중 원고를 구분했습니다. 각 항목에서 연구 상세와 원문으로 이동할 수 있습니다.','Published and accepted work is listed separately from manuscripts under review or in preparation.'),t('논문','Publications'))
    for key,ko,en in [('published','게재 및 확정','Published & accepted'),('review','심사 중','Under review'),('preparation','투고 준비','In preparation')]:
        rows=sorted([p for p in papers if p['group']==key],key=lambda p:-p['year'])
        body+=f'<section class="archive-group"><h2>{t(ko,en)} <small>({len(rows)})</small></h2><ol class="publication-list">'+''.join(publication_row(p) for p in rows)+'</ol></section>'
    page('/publications/',t('논문 및 원고','Publications & manuscripts'),t('논문별 연구 소개, 역할, 평가 조건과 DOI 및 코드 링크.','Study summaries, author roles, evaluation conditions, DOI and code links.'),body+'</div>')
def table_html(tbl,caption):
    rows=[[c['text'] for c in row] for row in tbl['rows']]
    def ct(v):return translate_cell(v) if LANG=='en' else v
    return '<div class="table-wrap" role="region" tabindex="0" aria-label="'+e(caption)+'"><table><caption>'+e(caption)+'</caption><thead><tr>'+''.join('<th scope="col">'+e(ct(v))+'</th>' for v in rows[0])+'</tr></thead><tbody>'+''.join('<tr>'+''.join('<td>'+e(ct(v))+'</td>' for v in row)+'</tr>' for row in rows[1:])+'</tbody></table></div>'
CELL={}
transpath=ROOT/'content/table-translations.json'
if transpath.exists():CELL=json.loads(transpath.read_text(encoding='utf8'))
def translate_cell(v):return CELL.get(v,v)
def figures_html(figs,title):
    if not figs:return ''
    h='<div class="evidence-gallery'+(' one' if len(figs)==1 else '')+'">'
    for i,f in enumerate(figs,1):
        caption=f.get('caption') or title
        if LANG=='en':caption=f.get('captionEn',title+f': source figure {i}')
        h+=f'<figure><a class="figure-link" href="{e(f["src"])}" target="_blank" rel="noopener" aria-label="{e(t("그림 확대: ","Enlarge figure: ")+caption)}"><img src="{e(f["src"])}" alt="{e(caption)}" loading="lazy"></a><figcaption>{e(caption)}<br>{a(f["src"],t("원본 그림 확대","View full-size figure"))}</figcaption></figure>'
    return h+'</div>'
def chart_html(c,title,i):
    series=c['series'];cats=series[0]['categories'];values=[x for s in series for x in s['values']];maximum=max(values,default=1)*1.22 or 1
    if '%' in title:maximum=min(100,maximum)
    width=680;height=410;left=65;right=15;top=35;bottom=120;pw=width-left-right;ph=height-top-bottom
    description='; '.join((translate_cell(s['name']) if LANG=='en' else s['name'])+': '+', '.join((translate_cell(k) if LANG=='en' else k)+' '+str(v) for k,v in zip(s['categories'],s['values'])) for s in series)
    svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {width} {height}" role="img" aria-labelledby="chart-{i}" aria-describedby="chart-desc-{i}"><title id="chart-{i}">{e(title)}</title><desc id="chart-desc-{i}">{e(description)}</desc><rect width="680" height="410" fill="white"/>'
    for tick in range(5):
        y=top+ph*(1-tick/4);v=maximum*tick/4
        svg+=f'<line x1="{left}" y1="{y}" x2="665" y2="{y}" stroke="#dce5f1"/><text x="{left-10}" y="{y+5}" text-anchor="end" fill="#596b82" font-size="14">{v:.0f}</text>'
    group=pw/max(len(cats),1);bar=min(68,group*.65/max(len(series),1));colors=['#a7bddd','#1f5fbf','#174895']
    for ci,cat in enumerate(cats):
        cx=left+group*(ci+.5)
        for si,s in enumerate(series):
            value=s['values'][ci];bh=value/maximum*ph;x=cx+(si-len(series)/2)*bar;y=top+ph-bh
            svg+=f'<rect x="{x}" y="{y}" width="{bar-3}" height="{bh}" rx="2" fill="{colors[si%3]}"/><text x="{x+(bar-3)/2}" y="{y-8}" text-anchor="middle" fill="#172a43" font-size="15" font-weight="600">{value:g}</text>'
        label=translate_cell(cat) if LANG=='en' else cat
        lines=textwrap.wrap(label,width=max(10,int(group/8))) or ['']
        for li,line in enumerate(lines):svg+=f'<text x="{cx}" y="{top+ph+25+li*17}" text-anchor="middle" fill="#172a43" font-size="14">{e(line)}</text>'
    for si,s in enumerate(series):
        label=translate_cell(s['name']) if LANG=='en' else s['name'];x=left+si*210
        svg+=f'<rect x="{x}" y="379" width="10" height="10" rx="2" fill="{colors[si%3]}"/><text x="{x+17}" y="389" fill="#596b82" font-size="13">{e(label)}</text>'
    svg+='</svg>'
    return '<figure class="chart-figure">'+svg+'<figcaption>'+e(title)+'</figcaption></figure>'
def project_page(p,index):
    title=local(p['title']);path='/projects/'+p['slug']+'/'
    body='<div class="wrap">'+archive_intro(title,local(p['summary']),t('프로젝트','Projects'))
    body+='<div class="link-list">'+''.join(a(u,l if LANG=='ko' else ('Paper DOI' if 'doi.org' in u else 'GitHub: '+u.rstrip('/').split('/')[-1])) for l,u in p['links'])+'</div>'
    date=p['date'] if LANG=='ko' else p['date'].replace('현재','Present').replace('광운대학교','Kwangwoon University').replace('바이오닉스연구센터','Bionics Research Center').replace('팀 TOG','Team TOG').replace('연구 인턴','Research internship').replace('공동 제1저자','Co-first author').replace('쿠도커뮤니케이션','CUDO Communication')
    body+='<dl class="detail-meta">'
    for label,value in [(t('역할','Role'),local(p['role'])),(t('담당 업무','Contribution'),local(p['work'])),(t('기간 및 소속','Period & affiliation'),date)]:body+=f'<div><dt>{label}</dt><dd>{e(value)}</dd></div>'
    body+='</dl><div class="detail-layout"><aside class="detail-toc"><p>'+t('이 프로젝트에서','On this page')+'</p>'
    for j,st in enumerate(p['stages'],1):body+=a('#stage-'+str(j),f'{j:02} '+(st['title'].split('/')[0].strip() if LANG=='ko' else ed['stageEnglish'][str(st['slide'])][0].split(':')[0]))
    body+=a('#related',t('관련 논문','Related work'))+'</aside><div class="detail-body">'
    for j,st in enumerate(p['stages'],1):
        en=ed['stageEnglish'][str(st['slide'])];heading=st['title'] if LANG=='ko' else en[0]
        args=st['arguments'] if LANG=='ko' else [{'label':l,'text':v} for l,v in zip(['Problem / context','Approach','Contribution / next steps'],en[1:4])]
        body+=f'<section class="detail-stage" id="stage-{j}"><h2><span class="section-number">{j:02} / RESEARCH DETAIL</span>{e(heading)}</h2><dl class="arguments">'+''.join(f'<dt>{e(arg["label"])}</dt><dd>{e(arg["text"])}</dd>' for arg in args)+'</dl>'
        body+=figures_html(st['figures'],heading)
        if st['charts']:body+='<div class="chart-set'+(' one' if len(st['charts'])==1 else '')+'">'+''.join(chart_html(c,(c['title'] if LANG=='ko' else translate_cell(c['title'])),f'{st["slide"]}-{k}') for k,c in enumerate(st['charts']))+'</div>'
        for k,tbl in enumerate(st['tables']):body+=table_html(tbl,t('모델 구성 및 평가 수치','Model specification and evaluation')+f' {k+1}')
        body+='<div class="evidence-note"><strong>'+t('평가 조건 및 연구 범위','Evaluation conditions and scope')+'</strong>'+e(st['note'] if LANG=='ko' else en[4])+'</div></section>'
    rel=[q for q in papers if q['related']==p['slug']]
    body+='<section class="related" id="related"><h2>'+t('관련 논문과 연구 자료','Related publications and research')+'</h2><ul>'
    if rel:body+=''.join('<li>'+a(route('/publications/'+q['slug']+'/'),q['title'])+'</li>' for q in rel)
    elif p['links']:body+=''.join('<li>'+a(u,l if LANG=='ko' else 'Research repository')+'</li>' for l,u in p['links'])
    else:body+='<li>'+t('최종 구조와 정량 평가 자료는 연구 진행에 따라 추가할 예정이다.','Final architecture and quantitative evaluation will be added as the research progresses.')+'</li>'
    body+='</ul></section><nav class="next-project" aria-label="'+t('다른 프로젝트','More projects')+'">'+a(route('/projects/'),t('전체 프로젝트','All projects'))
    if index+1<len(projects):body+=a(route('/projects/'+projects[index+1]['slug']+'/'),t('다음: ','Next: ')+local(projects[index+1]['short']))
    body+='</nav></div></div></div>'
    page(path,title,local(p['summary']),body)
PAPER_FIGURES={'sgcl':['sgcl-architecture.png','sgcl-embeddings.png'],'sparse-dgcnn':['sparse-dgcnn-l21-architecture.png','sparse-dgcnn-l21-edge-density.png'],'idcl':['idcl-architecture.png','idcl-inter-dialog.png'],'axis-ecg':['axis-ecg-model_architecture.png']}
PAPER_STAGE={'asgcrl':13,'simnext-eeg':14,'mda-gcl':25,'multiscale-entropy':41,'emotionheart':17,'glcl-rppg':27,'fr-ptt':23}
def paper_page(p):
    notes=ed['paperNotes'][p['slug']];summary=t(notes[0],notes[1]);results=t(notes[2],notes[3])
    body='<div class="wrap"><div class="paper-body">'+archive_intro(p['title'],summary,t('논문','Publications'))
    label=t('투고 예정 학술지/학회','Intended venue') if p['group']=='preparation' else t('심사 중 학술지/학회','Submitted venue') if p['group']=='review' else t('학술지/학회','Venue')
    body+='<p class="paper-status">'+e(paper_status(p))+'</p><dl class="detail-meta">'
    for k,v in [(label,p['venue']),(t('저자 역할','Author role'),paper_role(p)),(t('연도','Year'),str(p['year']))]:body+=f'<div><dt>{e(k)}</dt><dd>{e(v)}</dd></div>'
    body+='</dl><div class="publication-links">'+paper_links(p)+'</div><h2>'+t('연구 내용','Research approach')+'</h2><p>'+e(summary)+'</p>'
    figs=[]
    if p['slug'] in PAPER_FIGURES:figs=[{'src':'/assets/figures/'+f,'caption':p['slug'].upper()+t(' 원본 구조 및 분석 그림',' original architecture and analysis'),'captionEn':p['slug'].upper()+' original architecture and analysis'} for f in PAPER_FIGURES[p['slug']]]
    elif p['slug'] in PAPER_STAGE:
        st=next(s for pr in projects for s in pr['stages'] if s['slide']==PAPER_STAGE[p['slug']]);figs=st['figures']
    body+=figures_html(figs,p['title'])
    body+='<h2>'+t('결과와 평가 범위','Results and evaluation scope')+'</h2><p>'+e(results)+'</p>'
    if p['slug'] in PAPER_STAGE:
        st=next(s for pr in projects for s in pr['stages'] if s['slide']==PAPER_STAGE[p['slug']])
        for k,tbl in enumerate(st['tables']):
            if p['slug']=='fr-ptt':
                tbl={**tbl,'rows':tbl['rows'][:3]}
            if p['slug']=='mda-gcl':tbl={**tbl,'rows':tbl['rows'][:3]}
            body+=table_html(tbl,t('논문 구성과 결과','Paper specification and results'))
        body+='<div class="evidence-note"><strong>'+t('해석 범위','Interpretation')+'</strong>'+e(st['note'] if LANG=='ko' else ed['stageEnglish'][str(st['slide'])][4])+'</div>'
    if p['slug']=='graph-mamba':body+='<div class="evidence-note">'+t('최종 모델 구조, 검증 프로토콜, 정량 결과, 공개 코드가 추가될 예정이다.','Final architecture, validation protocol, quantitative results and public code are pending.')+'</div>'
    if p['related']:
        pr=next(x for x in projects if x['slug']==p['related']);body+='<section class="related"><h2>'+t('관련 프로젝트','Related project')+'</h2><p>'+a(route('/projects/'+pr['slug']+'/'),local(pr['short']))+'</p></section>'
    body+='<section class="related"><h2>'+t('원문 및 코드','Paper and code')+'</h2><ul>'+''.join('<li>'+a(u,'DOI: '+u.split('doi.org/')[-1] if 'doi.org/' in u else u.replace('https://github.com/','GitHub / '))+'</li>' for u in p['links'])+'</ul></section>'+a(route('/publications/'),t('전체 논문 목록','All publications'),'text-link')+'</div></div>'
    page('/publications/'+p['slug']+'/',p['title'],summary,body)

for p in projects:
    data=ed['projectEnglish'][p['slug']]
    for key,value in zip(['summary','role','work','scope','status'],data):p[key]['en']=value

for language in ['ko','en']:
    LANG=language
    home();archives()
    for i,p in enumerate(projects):project_page(p,i)
    for p in papers:paper_page(p)
LANG='ko'
notfound='<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>페이지를 찾을 수 없습니다 | Dae Hyeon Kim</title><link rel="stylesheet" href="/assets/site.css"></head><body><main class="wrap error-page"><p class="eyebrow">404 / PAGE NOT FOUND</p><h1>페이지를 찾을 수 없습니다.</h1><p>주소를 확인하거나 연구 프로필에서 다시 이동해 주세요.</p>'+a('/','연구 프로필로 이동')+'</main></body></html>'
(ROOT/'404.html').write_text(notfound,encoding='utf8')
(ROOT/'assets/favicon.svg').write_text('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 48 48"><rect width="48" height="48" rx="8" fill="#1f5fbf"/><text x="24" y="32" text-anchor="middle" font-family="Arial,sans-serif" font-size="24" font-weight="700" fill="white">DK</text></svg>',encoding='utf8')
print(f'Built {2*(3+len(projects)+len(papers))} bilingual pages, plus 404. No runtime dependencies.')
