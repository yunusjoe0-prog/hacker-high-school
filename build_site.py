# -*- coding: utf-8 -*-
"""
مولّد موقع مدرسة الهاكر الثانوية (13 كتابًا: المقدمة + 12 درسًا)
الاستخدام:
    python build_site.py                 -> يبحث عن الـ PDF ويبني المجلد site/
    python build_site.py --src /path     -> مجلد ملفات الـ PDF
    python build_site.py --serve         -> يبني ثم يشغّل الموقع على http://localhost:8000
ارفع مجلد site/ كما هو إلى GitHub Pages.
"""
import os, re, sys, shutil, argparse, html

HERE = os.path.dirname(os.path.abspath(__file__))

LESSONS = [
    (0,  "مقدمة: مدرسة الهاكر الثانوية", "دليل شامل يعرّف بالمشروع ويلخص الدروس مع مسرد للمصطلحات.", "map"),
    (1,  "أن تكون هاكر", "مهارات التعلم والبحث، ومصادر المعرفة الموثوقة.", "book"),
    (2,  "الأوامر الأساسية في لينكس وويندوز", "نافذة الأوامر والطرفية وأهم أوامرها.", "terminal"),
    (3,  "المنافذ والبروتوكولات", "نموذج TCP/IP وعناوين IP والمنافذ.", "network"),
    (4,  "الخدمات والاتصالات", "الويب والبريد وFTP وDNS وطرق الاتصال.", "server"),
    (5,  "تحديد هوية الأنظمة", "Whois وping وفحص المنافذ على جهازك.", "radar"),
    (6,  "البرمجيات الخبيثة", "الفيروسات والديدان وأحصنة طروادة وطرق الدفاع.", "bug"),
    (7,  "تحليل الهجمات", "Netstat وكشف التسلل وأنظمة الطُّعم.", "shield"),
    (8,  "الأدلة الجنائية الرقمية", "جمع الأدلة وتحليلها وحفظ سلسلة الحيازة.", "magnifier"),
    (9,  "أمان البريد الإلكتروني", "التصيد والاحتيال والإرسال والاستلام الآمن.", "mail"),
    (10, "أمان الويب والخصوصية", "ثغرات الويب وSSL وحماية الخصوصية.", "globe"),
    (11, "كلمات المرور", "بناء كلمات قوية وطرق الحماية.", "key"),
    (12, "القانون والأخلاق", "جرائم المعلوماتية والاختراق الأخلاقي.", "scales"),
]

ICONS = {
    "book": '<path d="M4 5a2 2 0 0 1 2-2h13v16H6a2 2 0 0 0-2 2z"/><path d="M8 7h7"/>',
    "terminal": '<rect x="3" y="4" width="18" height="16" rx="2"/><path d="M7 9l3 3-3 3M12 15h5"/>',
    "network": '<circle cx="12" cy="5" r="2"/><circle cx="5" cy="19" r="2"/><circle cx="19" cy="19" r="2"/><path d="M12 7v5M12 12l-6 5M12 12l6 5"/>',
    "server": '<rect x="3" y="4" width="18" height="6" rx="1"/><rect x="3" y="14" width="18" height="6" rx="1"/><path d="M7 7h.01M7 17h.01"/>',
    "radar": '<circle cx="12" cy="12" r="9"/><circle cx="12" cy="12" r="4"/><path d="M12 12l6-6"/>',
    "bug": '<rect x="8" y="8" width="8" height="11" rx="4"/><path d="M12 8V5M8 12H4M16 12h4M8 16l-3 2M16 16l3 2"/>',
    "shield": '<path d="M12 3l8 3v6c0 5-3.5 8-8 9-4.5-1-8-4-8-9V6z"/><path d="M8.5 12l2.5 2.5L16 9.5"/>',
    "magnifier": '<circle cx="10.5" cy="10.5" r="6"/><path d="M15 15l6 6"/>',
    "mail": '<rect x="3" y="5" width="18" height="14" rx="2"/><path d="M3 7l9 6 9-6"/>',
    "globe": '<circle cx="12" cy="12" r="9"/><path d="M3 12h18M12 3c3 3 3 15 0 18M12 3c-3 3-3 15 0 18"/>',
    "key": '<circle cx="8" cy="15" r="4"/><path d="M11 12l9-9M16 7l3 3"/>',
    "map": '<path d="M9 4l-6 2v14l6-2 6 2 6-2V4l-6 2z"/><path d="M9 4v14M15 6v14"/>',
    "scales": '<path d="M12 4v16M6 20h12M5 7h14M5 7l-3 7h6zM19 7l-3 7h6z"/>',
}

def icon(name, size=28):
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" '
            f'stroke="currentColor" stroke-width="1.7" stroke-linecap="round" '
            f'stroke-linejoin="round" aria-hidden="true">{ICONS[name]}</svg>')

HERO_LOGO = '''<svg viewBox="0 0 200 220" class="hero-logo" aria-hidden="true">
  <path d="M100 8l82 30v62c0 55-36 92-82 112-46-20-82-57-82-112V38z" fill="#fff" stroke="#0a6b3b" stroke-width="7" stroke-linejoin="round"/>
  <path d="M100 26l66 24v50c0 44-28 75-66 92-38-17-66-48-66-92V50z" fill="#e6f5ec"/>
  <rect x="68" y="92" width="64" height="52" rx="8" fill="#0a6b3b"/>
  <path d="M80 92V78a20 20 0 0 1 40 0v14" fill="none" stroke="#0a6b3b" stroke-width="9" stroke-linecap="round"/>
  <circle cx="100" cy="114" r="7" fill="#fff"/><rect x="97" y="116" width="6" height="16" rx="3" fill="#fff"/>
  <g stroke="#0a6b3b" stroke-width="3" fill="#0a6b3b" opacity=".55">
    <path d="M18 120h-14M182 120h14M30 160l-12 8M170 160l12 8" fill="none" stroke-linecap="round"/>
    <circle cx="4" cy="120" r="4"/><circle cx="196" cy="120" r="4"/><circle cx="18" cy="168" r="4"/><circle cx="182" cy="168" r="4"/>
  </g>
</svg>'''

PAGE = '''<!DOCTYPE html>
<html lang="ar" dir="rtl">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>مدرسة الهاكر الثانوية - الوعي الأمني للمراهقين</title>
<meta name="description" content="13 كتابًا مجانيًا للاطلاع والتحميل في الوعي الأمني والأمن السيبراني للمراهقين.">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Tajawal:wght@400;500;700;800&display=swap" rel="stylesheet">
<style>
:root{--green:#0a6b3b;--green-d:#064d2a;--green-l:#e6f5ec;--line:#cfe7d8;--ink:#12261b;--mute:#4d6a5a;--bg:#fff}
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{margin:0;font-family:"Tajawal","Segoe UI",Tahoma,Arial,sans-serif;background:var(--bg);color:var(--ink);line-height:1.7}
a{color:inherit;text-decoration:none}
:focus-visible{outline:3px solid #f5b700;outline-offset:2px}
.wrap{max-width:1080px;margin:0 auto;padding:0 18px}
header.top{background:var(--green);color:#fff}
.top .wrap{display:flex;align-items:center;gap:10px;padding-top:12px;padding-bottom:12px;font-weight:700}
.hero{background:linear-gradient(180deg,var(--green) 0,var(--green-d) 100%);color:#fff;position:relative;overflow:hidden}
.hero::before{content:"";position:absolute;inset:0;opacity:.12;
 background-image:linear-gradient(#fff 1px,transparent 1px),linear-gradient(90deg,#fff 1px,transparent 1px);background-size:34px 34px}
.hero .wrap{position:relative;display:grid;grid-template-columns:1.3fr 1fr;gap:24px;align-items:center;padding-top:42px;padding-bottom:54px}
.hero h1{font-size:clamp(28px,5.4vw,46px);line-height:1.25;margin:0 0 12px;font-weight:800}
.hero p{margin:0 0 22px;font-size:18px;color:#d7f0e1;max-width:34em}
.btn{display:inline-flex;align-items:center;gap:8px;border-radius:10px;padding:11px 20px;font-weight:700;font-size:16px;border:2px solid transparent;cursor:pointer}
.btn-w{background:#fff;color:var(--green)}
.btn-w:hover{background:var(--green-l)}
.hero-art{display:flex;justify-content:center}
.hero-logo{width:min(220px,55vw);filter:drop-shadow(0 10px 24px rgba(0,0,0,.3))}
.stats{display:flex;gap:26px;flex-wrap:wrap;margin-top:22px;color:#d7f0e1;font-size:15px}
.stats b{display:block;color:#fff;font-size:24px}
section{padding:44px 0}
h2{font-size:28px;margin:0 0 6px;color:var(--green-d)}
.sub{margin:0 0 26px;color:var(--mute)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(250px,1fr));gap:16px}
.card{border:1.5px solid var(--line);border-radius:14px;padding:18px;background:#fff;display:flex;flex-direction:column;gap:10px;position:relative}
.card .head{display:flex;align-items:center;gap:12px}
.ico{width:50px;height:50px;border-radius:12px;background:var(--green-l);color:var(--green);display:grid;place-items:center;flex:none}
.num{font-size:13px;color:var(--mute);font-weight:500}
.card h3{margin:0;font-size:19px;line-height:1.35;color:var(--green-d)}
.card p{margin:0;color:var(--mute);font-size:15px;flex:1}
.actions{display:flex;gap:8px;margin-top:4px}
.actions .btn{flex:1;justify-content:center;padding:9px 10px;font-size:15px;border-radius:9px}
.btn-g{background:var(--green);color:#fff}
.btn-g:hover{background:var(--green-d)}
.btn-o{border-color:var(--green);color:var(--green);background:#fff}
.btn-o:hover{background:var(--green-l)}
.soon{opacity:.6}
.soon .actions span{flex:1;text-align:center;padding:9px;border:1.5px dashed var(--line);border-radius:9px;color:var(--mute);font-size:15px}
.tips{background:var(--green-l);border-block:1.5px solid var(--line)}
.tips ul{margin:0;padding:0;list-style:none;display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px}
.tips li{display:flex;gap:10px;align-items:flex-start;background:#fff;border:1.5px solid var(--line);border-radius:12px;padding:14px}
.tips li svg{color:var(--green);flex:none;margin-top:2px}
footer{background:var(--green-d);color:#cfe7d8;padding:26px 0;font-size:14px}
footer b{color:#fff}
@media(max-width:720px){.hero .wrap{grid-template-columns:1fr;text-align:center}.hero p{margin-inline:auto}.stats{justify-content:center}.hero-art{order:-1}}
@media(prefers-reduced-motion:reduce){html{scroll-behavior:auto}}
</style>
</head>
<body>
<header class="top"><div class="wrap">__MINI__ <span>مدرسة الهاكر الثانوية</span></div></header>

<div class="hero"><div class="wrap">
  <div>
    <h1>الوعي الأمني للمراهقين: تعلّم كيف تحمي نفسك وتفهم عالم الأمن السيبراني</h1>
    <p>13 كتابًا تعليميًا مجانيًا تقرؤها على الموقع مباشرة أو تحمّل كل كتاب على حدة.</p>
    <a class="btn btn-w" href="#books">ابدأ بالكتب</a>
    <div class="stats"><div><b>13</b>كتابًا</div><div><b>PDF</b>اطلاع وتحميل</div><div><b>مجاني</b>للتعلم</div></div>
  </div>
  <div class="hero-art">__HERO__</div>
</div></div>

<section id="books"><div class="wrap">
  <h2>الكتب</h2>
  <p class="sub">اضغط «اطلاع» للقراءة على المتصفح أو «تحميل» لحفظ الكتاب على جهازك.</p>
  <div class="grid">
__CARDS__
  </div>
</div></section>

<section class="tips"><div class="wrap">
  <h2>قواعد الهاكر المسؤول</h2>
  <p class="sub">المعرفة قوة، واستخدامها بمسؤولية هو ما يصنع الفرق.</p>
  <ul>
    <li>__I1__<span>جرّب الأدوات على جهازك فقط، ولا تفحص أجهزة الآخرين دون إذن.</span></li>
    <li>__I2__<span>أبلغ عن الثغرات بدل استغلالها.</span></li>
    <li>__I3__<span>استخدم كلمات مرور قوية وطويلة ومختلفة لكل حساب مهم.</span></li>
    <li>__I4__<span>تحقق من أي معلومة بالبحث عن تأييدها ثم عن ردودها.</span></li>
  </ul>
</div></section>

<footer><div class="wrap">
  <p><b>مدرسة الهاكر الثانوية</b> - مواد تعليمية من مشروع ISECOM (hackerhighschool.org).</p>
  <p>المواد مفتوحة للاستخدام غير التجاري مع طلاب المدارس والتعليم المنزلي، ويمنع بيعها أو تقديمها في دورات مدفوعة دون ترخيص. المشروع تعليمي ولا يتحمل المسؤولية عن إساءة استخدام المعلومات.</p>
</div></footer>
</body>
</html>
'''

def find_pdfs(src):
    """يرجع {رقم الدرس: مسار الملف} من أسماء مثل: الدرس_1_...pdf أو lesson1.pdf"""
    found = {}
    if not os.path.isdir(src):
        return found
    for f in sorted(os.listdir(src)):
        if not f.lower().endswith(".pdf"):
            continue
        m = re.search(r"الدرس[\s_\-]*(\d+)", f) or re.search(r"(?:lesson|book)[\s_\-]*(\d+)", f, re.I)
        if m and 1 <= int(m.group(1)) <= 12:
            found.setdefault(int(m.group(1)), os.path.join(src, f))
        elif not m and ("الوعي" in f or "مقدمة" in f or "intro" in f.lower()):
            found.setdefault(0, os.path.join(src, f))
    return found

def build(src, out):
    pdfs = find_pdfs(src)
    books_dir = out
    os.makedirs(books_dir, exist_ok=True)
    cards = []
    for n, title, desc, ic in LESSONS:
        t, d = html.escape(title), html.escape(desc)
        head = (f'<div class="head"><div class="ico">{icon(ic)}</div>'
                f'<div><div class="num">{"المقدمة" if n == 0 else "الكتاب %d" % n}</div><h3>{t}</h3></div></div>')
        if n in pdfs:
            name = f"lesson-{n:02d}.pdf"
            shutil.copyfile(pdfs[n], os.path.join(books_dir, name))
            acts = (f'<a class="btn btn-g" href="{name}" target="_blank" rel="noopener">اطلاع</a>'
                    f'<a class="btn btn-o" href="{name}" download="{html.escape("مقدمة_مدرسة_الهاكر_الثانوية.pdf" if n == 0 else "الدرس_%d_%s.pdf" % (n, title))}">تحميل</a>')
            cls = "card"
        else:
            acts = '<span>قريبًا</span>'
            cls = "card soon"
        cards.append(f'    <article class="{cls}">{head}<p>{d}</p><div class="actions">{acts}</div></article>')
    page = (PAGE.replace("__CARDS__", "\n".join(cards))
                .replace("__HERO__", HERO_LOGO)
                .replace("__MINI__", icon("shield", 26))
                .replace("__I1__", icon("terminal", 22)).replace("__I2__", icon("shield", 22))
                .replace("__I3__", icon("key", 22)).replace("__I4__", icon("magnifier", 22)))
    with open(os.path.join(out, "index.html"), "w", encoding="utf-8") as f:
        f.write(page)
    open(os.path.join(out, ".nojekyll"), "w").close()
    print(f"تم: {len(pdfs)} من 13 كتابًا -> {out}")
    missing = [n for n in range(0, 13) if n not in pdfs]
    if missing:
        print("كتب لم يُعثر عليها:", missing, "(ضع ملفاتها في المجلد ثم أعد التشغيل)")

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--src", help="مجلد ملفات الـ PDF")
    ap.add_argument("--out", default=os.path.join(HERE, "site"))
    ap.add_argument("--serve", action="store_true", default=True)
    a = ap.parse_args()
    candidates = [a.src] if a.src else [os.path.join(HERE, "books"), HERE,
                  "/storage/emulated/0/Download", os.path.expanduser("~/Download")]
    src = next((c for c in candidates if c and find_pdfs(c)), candidates[0])
    build(src, a.out)
    if a.serve:
        import http.server, socketserver
        os.chdir(a.out)
        socketserver.TCPServer.allow_reuse_address = True
        for port in range(8000, 8020):
            try:
                s = socketserver.TCPServer(("", port), http.server.SimpleHTTPRequestHandler)
            except OSError:
                continue
            print(f"افتح في المتصفح: http://localhost:{port}")
            s.serve_forever()
            break
        else:
            print("تعذر فتح أي منفذ، أغلق Pydroid وأعد المحاولة.")

if __name__ == "__main__":
    main()
