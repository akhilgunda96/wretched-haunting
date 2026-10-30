"""BrandShield's visual system. Escape all variable HTML before rendering."""
from html import escape
import streamlit as st

CSS = '''
:root{--ink:#252341;--muted:#77758e;--accent:#6951e8;--line:#e8e5f2}
.stApp{background:#f5f4fa;color:var(--ink)}
/* Leave room for Streamlit's fixed toolbar above the app wordmark. */
.block-container{max-width:1440px;padding:4.75rem 2.7rem 2rem}
h1,h2,h3{color:var(--ink);letter-spacing:-.045em}h2{font-size:1.8rem!important}h3{font-size:1.15rem!important}
p{line-height:1.6}[data-testid=stCaptionContainer]{color:var(--muted)}
[data-testid=stHeader]{background:#f5f4faf2}
[data-testid=stSidebar]{background:linear-gradient(180deg,#211d3b,#17152c);border-right:1px solid #312c4d;width:265px!important;min-width:265px!important}
[data-testid=stSidebar] [data-testid=stMarkdownContainer],[data-testid=stSidebar] [data-testid=stCaptionContainer],[data-testid=stSidebar] [data-testid=stWidgetLabel]{color:#c6c2dc}
[data-testid=stSidebar] h2{color:#fff}
[data-testid=stSidebar] [role=radiogroup]{gap:7px}
[data-testid=stSidebar] [role=radiogroup] label{width:100%;padding:11px 15px;border-radius:11px;color:#c6c2dc;transition:background .18s}
[data-testid=stSidebar] [role=radiogroup] label:hover{background:#332d52}
[data-testid=stSidebar] [role=radiogroup] label:has(input:checked){background:#7055dc;box-shadow:0 6px 18px #100b3825}
[data-testid=stSidebar] [role=radiogroup] label:has(input:checked) p{color:white!important}
[data-testid=stSidebar] [role=radiogroup] label>div:first-child{display:none}
[data-testid=stSidebar] button{background:#302a48!important;color:#f6f2ff!important;border:1px solid #514865!important;border-radius:10px}
[data-testid=stSidebar] button p,[data-testid=stSidebar] button [data-testid=stMarkdownContainer]{color:#f6f2ff!important}
.bs-side-name{font-size:23px;font-weight:800;color:#fff;letter-spacing:-1px;margin-top:10px}
.bs-side-name:before{content:'◈';display:inline-grid;place-items:center;background:#b9f382;color:#231d3c;border-radius:10px;width:35px;height:38px;margin-right:9px}
.bs-side-label{font-size:11px;color:#a8a0c7;letter-spacing:2px;margin:10px 0 30px}
.bs-brand{display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line);padding-bottom:16px;margin-bottom:22px}
.bs-brand-left{display:flex;align-items:center;gap:11px}.bs-mark{background:#6951e8;border-radius:10px;width:32px;height:35px;display:grid;place-items:center;color:white;font-size:21px;font-weight:800}
.bs-name{font-size:18px;font-weight:800;letter-spacing:-.6px}.bs-tag{font-size:11px;color:var(--muted);letter-spacing:1.6px;margin-top:2px}
.bs-top-pill{font-size:11px;font-weight:650;border:1px solid #ded9ed;color:#63577d;background:#fff;border-radius:30px;padding:6px 12px}
.bs-hero{position:relative;overflow:hidden;background:linear-gradient(115deg,#30234d,#554080);border:1px solid #67508d;border-radius:20px;padding:26px 30px;color:#f2ecff;margin:2px 0 22px}
.bs-hero h2{font-size:30px!important;line-height:1.16;color:#fff;letter-spacing:-1.1px;margin:10px 0}
.bs-hero p{color:#ded4ed;max-width:650px;font-size:13px;margin:0}
.bs-eyebrow{font-size:11px;letter-spacing:2.1px;font-weight:750;color:#c9f5a4}
.bs-hero-tags{display:flex;flex-wrap:wrap;gap:7px;margin-top:18px}
.bs-hero-tags span{border:1px solid #847195;background:#ffffff09;padding:4px 10px;border-radius:30px;font-size:11px;color:#eee8f5}
.bs-hero-split{display:grid;grid-template-columns:1.35fr 1fr;gap:10px;align-items:center;min-height:224px}
.bs-hero-split h2{font-size:clamp(28px,3vw,43px)!important;line-height:1.12;max-width:550px}
.bs-highlight{color:#c8f69e}.bs-hero-split p{max-width:430px}
.bs-art{height:220px;position:relative;display:grid;place-items:center;isolation:isolate}
.bs-art:before{content:'';width:210px;height:210px;background:#b8a0fa12;border:1px solid #cbb4ff25;border-radius:50%;position:absolute;box-shadow:0 0 0 28px #b8a0fa08,0 0 0 56px #b8a0fa05}
.bs-shield{width:120px;height:148px;position:relative;filter:drop-shadow(0 16px 20px #140e4444);animation:float 6s ease-in-out infinite}
.bs-float{position:absolute;background:#fdfbff;color:#35304c;padding:10px 13px;border-radius:11px;box-shadow:0 8px 28px #120a3829;font-size:11px;z-index:2}
.bs-float small{display:block;color:#81758e;font-size:11px;margin-top:3px}.bs-float.one{top:23px;right:0;transform:rotate(4deg)}.bs-float.two{bottom:16px;left:0;transform:rotate(-5deg)}
.bs-float b{display:inline-block;color:#438e4b;background:#e7f5dd;border-radius:50%;padding:1px 5px;margin-right:5px}
.bs-welcome{display:flex;align-items:center;justify-content:space-between;margin:2px 0 18px;gap:12px}.bs-welcome h2{font-size:24px!important;margin:0}.bs-welcome p{font-size:12px;color:var(--muted);margin:3px 0 0}
.bs-live{color:#526644;background:#e9f2e3;border:1px solid #d9e7d0;font-size:11px;border-radius:20px;padding:6px 11px;white-space:nowrap}
.bs-stat-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin:0 0 18px}
.bs-stat{border:1px solid var(--line);background:#fff;padding:17px 18px;border-radius:14px;box-shadow:0 4px 15px #2f244204;position:relative}
.bs-stat-top{display:flex;justify-content:space-between;align-items:center;font-size:11px;color:#78718d}.bs-stat-icon{width:29px;height:29px;display:grid;place-items:center;border-radius:9px;background:#ede9fc;color:#7051d9;font-size:16px}
.bs-stat:nth-child(2) .bs-stat-icon{background:#fff1dc;color:#ad792b}.bs-stat:nth-child(3) .bs-stat-icon{background:#e5f3e7;color:#43894a}.bs-stat:nth-child(4) .bs-stat-icon{background:#fce8ef;color:#b45b7d}
.bs-stat-value{font-size:31px;line-height:1.2;font-weight:800;letter-spacing:-1.4px;margin:8px 0 3px}.bs-stat-foot{color:#91889e;font-size:11px}
[data-testid=stMetric]{background:#fff;border:1px solid var(--line);border-radius:13px;padding:17px 20px}
[data-testid=stMetricValue]{font-weight:750;color:var(--ink);letter-spacing:-1px}[data-testid=stMetricLabel]{color:var(--muted);font-size:12px}
.bs-section{margin:16px 0 12px;display:flex;align-items:baseline;justify-content:space-between;gap:12px}.bs-section strong{font-size:16px;letter-spacing:-.4px}.bs-section span{color:var(--muted);font-size:11px}
.bs-panel{border:1px solid var(--line);border-radius:15px;background:#fff;padding:20px;margin:0 0 13px}.bs-panel h3{margin:0 0 5px!important}.bs-panel p{margin:0;color:var(--muted);font-size:12px}
.bs-status{display:inline-block;padding:4px 9px;border-radius:6px;font-size:11px;font-weight:700;background:#eeeaf7;color:#77648e;white-space:nowrap}
.bs-status.approved{background:#e4f4e5;color:#387546}.bs-status.pending{background:#fff2dc;color:#996d29}.bs-status.changes{background:#ffe7ed;color:#b04c6d}
.bs-review-row{display:flex;align-items:center;justify-content:space-between;gap:12px;padding:15px 17px;border:1px solid var(--line);border-radius:11px;background:#fff;margin:8px 0;transition:box-shadow .18s}
.bs-review-row:hover{box-shadow:0 5px 20px #4430620c}.bs-review-row strong{font-size:14px}.bs-review-row small{display:block;font-size:11px;color:var(--muted);margin-top:4px}
.bs-evidence{background:#f0edf9;border-left:3px solid #8a70dc;border-radius:0 9px 9px 0;padding:13px 16px;margin:10px 0;color:#504468;font-size:13px}.bs-evidence small{display:block;font-size:11px;letter-spacing:1px;font-weight:700;color:#7c63a5;margin-bottom:5px}
.bs-bars{margin-top:18px}.bs-bar{margin:14px 0}.bs-bar-label{display:flex;justify-content:space-between;font-size:11px;margin-bottom:6px;color:#756a86}.bs-bar-track{height:7px;background:#f1edf8;border-radius:20px;overflow:hidden}.bs-bar-fill{height:100%;background:linear-gradient(90deg,#8c70e8,#bea9f6);border-radius:20px}
.bs-brand-mini{display:flex;align-items:center;gap:11px;padding:12px 0;border-top:1px solid #f1edf7}.bs-brand-avatar{width:36px;height:36px;flex-shrink:0;border-radius:11px;background:#ecf4df;color:#608734;font-size:16px;display:grid;place-items:center;font-weight:800}.bs-brand-mini:nth-child(odd) .bs-brand-avatar{background:#f3e8f7;color:#9258ac}.bs-brand-mini strong{font-size:13px}.bs-brand-mini small{display:block;font-size:11px;color:#897b97;margin-top:2px}
.stButton>button,.stDownloadButton>button,.stFormSubmitButton>button{border-radius:9px;font-weight:600;min-height:41px;font-size:12px;transition:transform .15s,box-shadow .15s}.stButton>button:hover,.stDownloadButton>button:hover{transform:translateY(-1px);box-shadow:0 4px 12px #6951e81c}
.stButton>button[kind=primary],.stFormSubmitButton>button[kind=primary]{background:#6951e8;border-color:#6951e8;color:#fff;box-shadow:0 4px 12px #6951e824}
[data-testid=stTextInput] input,[data-testid=stTextArea] textarea{border-radius:9px}[data-testid=stTextArea] textarea{line-height:1.75;font-size:14px}
[data-testid=stExpander]{background:#fff;border:1px solid var(--line);border-radius:12px;margin-bottom:10px;overflow:hidden}[data-testid=stForm]{background:#fff;border:1px solid var(--line);border-radius:16px;padding:24px}
[data-testid=stTabs] [role=tablist]{gap:24px;border-bottom:1px solid var(--line)}[data-testid=stTabs] [role=tab]{font-weight:600}
button:focus-visible,a:focus-visible{outline:3px solid #9c7de8!important;outline-offset:3px}
.bs-footer{display:flex;justify-content:space-between;gap:16px;flex-wrap:wrap;color:#94889e;font-size:11px;padding:18px 0;border-top:1px solid var(--line);margin-top:28px}
@keyframes float{0%,100%{transform:translateY(0) rotate(-4deg)}50%{transform:translateY(-8px) rotate(1deg)}}
@media(max-width:1100px){.block-container{padding:4.75rem 1.5rem 1.5rem}.bs-hero-split{grid-template-columns:1.3fr 1fr}.bs-art{transform:scale(.9)}}
@media(max-width:700px){.block-container{padding:4.75rem 1rem 1rem}.bs-hero{padding:22px}.bs-hero-split{grid-template-columns:1fr}.bs-art{display:none}.bs-hero h2{font-size:28px!important}.bs-stat-grid{grid-template-columns:repeat(2,1fr);gap:9px}.bs-section{flex-wrap:wrap;gap:4px}.bs-review-row{align-items:flex-start}.bs-top-pill{display:none}.bs-welcome{align-items:flex-start}.bs-live{display:none}}
@media(prefers-reduced-motion:reduce){*,*:before,*:after{animation:none!important;transition:none!important}}
'''


def inject_styles():
    st.markdown('<style>'+CSS+'</style>',unsafe_allow_html=True)


def brand():
    st.markdown('<div class="bs-brand"><div class="bs-brand-left"><div class="bs-mark">◈</div><div><div class="bs-name">BrandShield <span style="color:#8b76bd;font-weight:500">AI</span></div><div class="bs-tag">YOUR BRAND. EVERY DETAIL.</div></div></div><div class="bs-top-pill">TECHCIRCUIT / GRUMPYBOT</div></div>',unsafe_allow_html=True)


SHIELD = '<svg class="bs-shield" viewBox="0 0 140 170" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true"><defs><linearGradient id="shield" x1="20" y1="0" x2="120" y2="170" gradientUnits="userSpaceOnUse"><stop stop-color="#d3bfff"/><stop offset="1" stop-color="#8361d7"/></linearGradient></defs><path d="M70 5L130 29V85C130 120 105 148 70 165C35 148 10 120 10 85V29L70 5Z" fill="url(#shield)" stroke="#e7dcff" stroke-width="2"/><path d="M70 22L114 40V85C114 111 96 133 70 148C44 133 26 111 26 85V40L70 22Z" fill="#6b46b5" stroke="#d8c2ff" stroke-opacity=".55"/><circle cx="70" cy="81" r="30" fill="#cef4a7"/><path d="M55 81L65 92L85 69" stroke="#374c35" stroke-width="7" stroke-linecap="round" stroke-linejoin="round"/></svg>'


def hero(eyebrow,title,description,tags=()):
    labels=''.join(f'<span>{escape(t)}</span>' for t in tags)
    st.markdown(f'<div class="bs-hero"><div class="bs-eyebrow">{escape(eyebrow)}</div><h2>{escape(title)}</h2><p>{escape(description)}</p>'+ (f'<div class="bs-hero-tags">{labels}</div>' if labels else '')+'</div>',unsafe_allow_html=True)


def showcase(eyebrow='THE BRAND GOVERNANCE WORKSPACE'):
    st.markdown('<div class="bs-hero bs-hero-split"><div><div class="bs-eyebrow">'+escape(eyebrow)+'</div><h2>Big ideas.<br><span class="bs-highlight">On-brand impact.</span></h2><p>A little more clarity. A lot more confidence. Give every message the review it deserves.</p><div class="bs-hero-tags"><span>Source-backed checks</span><span>Focused corrections</span><span>Human approval</span></div></div><div class="bs-art">'+SHIELD+'<div class="bs-float one"><b>✓</b> Evidence first<small>Every configured rule has a source</small></div><div class="bs-float two"><b>✓</b> People in control<small>Your message. Your final decision.</small></div></div></div>',unsafe_allow_html=True)


def dashboard_header(name):
    st.markdown(f'<div class="bs-welcome"><div><h2>Welcome back, {escape(name)}.</h2><p>Here’s what’s happening in your brand workspace.</p></div><span class="bs-live">● Local rule engine</span></div>',unsafe_allow_html=True)
    showcase('CREATE BOLDLY. REVIEW CONFIDENTLY.')


def stats(reviews):
    cards=[('Total reviews',len(reviews),'▤','Across your visible workspace'),('Awaiting review',sum(r['status']=='Pending review' for r in reviews),'◷','Ready for a human decision'),('Approved',sum(r['status']=='Approved' for r in reviews),'✓','Explicitly approved by reviewers'),('Changes requested',sum(r['status']=='Changes requested' for r in reviews),'↗','Feedback ready to work on')]
    st.markdown('<div class="bs-stat-grid">'+''.join(f'<div class="bs-stat"><div class="bs-stat-top">{label}<span class="bs-stat-icon">{icon}</span></div><div class="bs-stat-value">{value}</div><div class="bs-stat-foot">{foot}</div></div>' for label,value,icon,foot in cards)+'</div>',unsafe_allow_html=True)


def section(title,description=''):
    st.markdown(f'<div class="bs-section"><strong>{escape(title)}</strong><span>{escape(description)}</span></div>',unsafe_allow_html=True)


def status_badge(status):
    kind={'Approved':'approved','Pending review':'pending','Changes requested':'changes'}.get(status,'')
    return f'<span class="bs-status {kind}">{escape(status)}</span>'


def recent_reviews(reviews):
    if not reviews:
        st.markdown('<div class="bs-panel"><h3>A fresh start for your brand</h3><p>Create a draft to see review status and activity here.</p></div>',unsafe_allow_html=True)
    for r in reviews[:5]:
        st.markdown(f'<div class="bs-review-row"><div><strong>{escape(r["title"])}</strong><small>#{r["id"]} · {escape(r["creator"])} · Revision {r["version"]} · {escape(r["updated"])} UTC</small></div>{status_badge(r["status"])}</div>',unsafe_allow_html=True)


def findings_panel(counts,dismissed):
    total=sum(counts.values())
    bars=''.join(f'<div class="bs-bar"><div class="bs-bar-label"><span>{escape(k)}</span><strong>{v}</strong></div><div class="bs-bar-track"><div class="bs-bar-fill" style="width:{v/max(counts.values())*100:.2f}%"></div></div></div>' for k,v in counts.most_common(5)) if counts else '<p>No findings yet. Start a review to see patterns here.</p>'
    st.markdown(f'<div class="bs-panel"><h3>Finding patterns</h3><p>{total} findings · {sum(dismissed.values())} dismissed · latest revisions</p><div class="bs-bars">{bars}</div></div>',unsafe_allow_html=True)


def brands_panel(profiles):
    rows=''.join(f'<div class="bs-brand-mini"><div class="bs-brand-avatar">{escape(p["name"][:1])}</div><div><strong>{escape(p["name"])}</strong><small>{len(p["body"]["sources"])} approved sources · Profile v{p["version"]}</small></div></div>' for p in profiles)
    st.markdown('<div class="bs-panel"><h3>Your brand library</h3><p>Different voices. One review workspace.</p><div style="margin-top:14px">'+rows+'</div></div>',unsafe_allow_html=True)


def evidence(text,source_id):
    label='APPROVED SOURCE · '+source_id if source_id else 'EVIDENCE NOT CONFIGURED'
    st.markdown(f'<div class="bs-evidence"><small>{escape(label)}</small>{escape(text)}</div>',unsafe_allow_html=True)
