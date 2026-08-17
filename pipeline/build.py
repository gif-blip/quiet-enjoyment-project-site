#!/usr/bin/env python3
"""Generate the complete quietenjoymentproject.org static site.

    python3 build_site.py

Copy lives in site_content.py. Data (watch list, charts, stats) comes from the
analysis pipeline. Output goes to ./site/ — deploy that folder anywhere.
"""
import json, os, re, shutil, html, datetime, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
from site_content import (SITE, NAV, FOOTER, HOME, REPORTS, WATCH, LAW,
                          HEALTH, ASKS, RESIDENTS, ABOUT, DATA)

PROJECT = os.path.dirname(HERE)                     # .../University Hill Noise
OUT = os.path.dirname(HERE)   # repo root: GitHub Pages serves from here
ASSETS = os.path.join(OUT, 'assets')
# Pipeline artifacts (charts + watch-list data) produced by the report build.
PIPELINE = os.path.join(HERE, 'build-input')

CSS = """
:root{
  --bg:#ffffff; --surface:#f7f7f5; --ink:#14140f; --ink-2:#4a4a44; --muted:#7a7a72;
  --rule:#e3e3dc; --accent:#1f4e79; --accent-soft:#eaf1f8; --warn:#b3261e; --good:#1c6b3c;
  --max:70rem;
}
@media (prefers-color-scheme: dark){
  :root:not([data-theme="light"]){
    --bg:#14140f; --surface:#1d1d18; --ink:#f4f4ee; --ink-2:#c9c9c0; --muted:#94948b;
    --rule:#2f2f28; --accent:#8ab6e0; --accent-soft:#1b2b3a; --warn:#f0857d; --good:#7cc79b;
  }
}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--ink);
  font:16px/1.65 -apple-system,BlinkMacSystemFont,"Segoe UI",Helvetica,Arial,sans-serif;
  -webkit-font-smoothing:antialiased}
a{color:var(--accent)}
.wrap{max-width:var(--max);margin:0 auto;padding:0 1.5rem}
header.site{border-bottom:1px solid var(--rule);background:var(--bg);position:sticky;top:0;z-index:10}
header.site .wrap{display:flex;flex-wrap:wrap;align-items:baseline;gap:.5rem 1.5rem;padding-top:1rem;padding-bottom:.85rem}
.brand{font-weight:700;font-size:1.05rem;letter-spacing:-.01em;color:var(--ink);text-decoration:none;white-space:nowrap}
nav.site{display:flex;flex-wrap:wrap;gap:.35rem 1.1rem;font-size:.9rem}
nav.site a{color:var(--ink-2);text-decoration:none;padding:.15rem 0;border-bottom:2px solid transparent}
nav.site a:hover{color:var(--accent)}
nav.site a[aria-current="page"]{color:var(--ink);border-bottom-color:var(--accent);font-weight:600}
main{padding:2.5rem 0 3.5rem}
h1{font-size:2rem;line-height:1.2;letter-spacing:-.02em;margin:0 0 .6rem}
h1 .sub{display:block;font-size:1.35rem;color:var(--ink-2);font-weight:600;margin-top:.35rem}
h2{font-size:1.3rem;letter-spacing:-.01em;margin:2.25rem 0 .5rem}
h3{font-size:1.02rem;margin:1.5rem 0 .3rem}
p{margin:0 0 1rem}
.lede{font-size:1.12rem;color:var(--ink-2);max-width:46rem}
.hero{background:var(--surface);border:1px solid var(--rule);border-radius:12px;padding:1.4rem 1.5rem;margin:1.5rem 0}
.hero p{margin:0;font-size:1.05rem}
.doors{display:grid;grid-template-columns:repeat(auto-fit,minmax(15rem,1fr));gap:1rem;margin:1.75rem 0}
.door{display:block;border:1px solid var(--rule);border-radius:12px;padding:1.1rem 1.2rem;text-decoration:none;
  background:var(--bg);transition:border-color .15s,transform .15s}
.door:hover{border-color:var(--accent);transform:translateY(-2px)}
.door strong{display:block;color:var(--ink);margin-bottom:.3rem}
.door span{color:var(--ink-2);font-size:.94rem}
figure{margin:1.5rem 0}
figure img{width:100%;height:auto;border:1px solid var(--rule);border-radius:10px;background:#fff}
figcaption{color:var(--muted);font-size:.85rem;margin-top:.5rem}
.callout{border-left:3px solid var(--accent);background:var(--accent-soft);padding:.9rem 1.1rem;border-radius:0 8px 8px 0;margin:1.25rem 0}
.callout p:last-child{margin-bottom:0}
.callout.plain{border-left-color:var(--muted);background:var(--surface)}
.tablewrap{overflow-x:auto;margin:1.25rem 0}
table{border-collapse:collapse;width:100%;font-size:.92rem;min-width:38rem}
th,td{text-align:left;padding:.55rem .7rem;border-bottom:1px solid var(--rule);vertical-align:top}
th{font-size:.78rem;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);font-weight:600}
td.num,th.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}
tbody tr:hover{background:var(--surface)}
.chip{display:inline-block;font-size:.74rem;padding:.14rem .5rem;border-radius:999px;white-space:nowrap;
  border:1px solid var(--rule);color:var(--ink-2);background:var(--surface)}
.chip.up{color:var(--warn);border-color:currentColor}
.chip.down{color:var(--good);border-color:currentColor}
ul.clean{list-style:none;padding:0;margin:1rem 0}
ul.clean li{padding-left:1.2rem;position:relative;margin-bottom:.6rem}
ul.clean li::before{content:"";position:absolute;left:0;top:.62em;width:.42rem;height:.42rem;border-radius:50%;background:var(--accent)}
ol.steps{padding-left:0;counter-reset:s;list-style:none;margin:1rem 0}
ol.steps li{counter-increment:s;position:relative;padding-left:2.1rem;margin-bottom:.85rem}
ol.steps li::before{content:counter(s);position:absolute;left:0;top:.05em;width:1.5rem;height:1.5rem;border-radius:50%;
  background:var(--accent);color:#fff;font-size:.82rem;font-weight:700;display:grid;place-items:center}
.asks-group{margin:1.5rem 0}
.ask{display:flex;gap:.9rem;align-items:flex-start;padding:.85rem 0;border-bottom:1px solid var(--rule)}
.ask .body{flex:1}
.reportcard{border:1px solid var(--rule);border-radius:12px;padding:1.1rem 1.2rem;margin:1rem 0;background:var(--bg)}
.reportcard h3{margin-top:0}
.dl{display:inline-block;margin-top:.4rem;font-weight:600;font-size:.92rem}
footer.site{border-top:1px solid var(--rule);background:var(--surface);color:var(--muted);font-size:.83rem}
footer.site .wrap{padding-top:1.5rem;padding-bottom:2.5rem}
footer.site a{color:var(--ink-2)}
.updated{color:var(--muted);font-size:.85rem;margin-top:-.3rem}
@media (max-width:640px){
  h1{font-size:1.6rem} h1 .sub{font-size:1.15rem}
  header.site .wrap{padding-top:.85rem}
}
"""


def esc(t):
    return html.escape(t, quote=False)


def fmt(t):
    """Interpolate {email} etc. into copy strings."""
    return t.replace('{email}', SITE['email'])


def page(filename, title, body, subtitle=None):
    nav = '\n'.join(
        f'        <a href="{h}"{" aria-current=\"page\"" if h == filename else ""}>{esc(label)}</a>'
        for h, label in NAV)
    doc = f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)} · {esc(SITE['name'])}</title>
<meta name="description" content="{esc(HOME['mission'][:155])}">
<style>{CSS}</style>
</head>
<body>
<header class="site">
  <div class="wrap">
    <a class="brand" href="index.html">{esc(SITE['name'])}</a>
    <nav class="site">
{nav}
    </nav>
  </div>
</header>
<main>
  <div class="wrap">
{body}
  </div>
</main>
<footer class="site">
  <div class="wrap">
    <p>{fmt(FOOTER)}</p>
  </div>
</footer>
</body>
</html>
"""
    with open(os.path.join(OUT, filename), 'w') as f:
        f.write(doc)


# ---------------------------------------------------------------- data loading
LOWER = {'of', 'the', 'and', 'at', 'for', 'on', 'in', 'a', 'to'}
UPPER = {'llc', 'lllp', 'llp', 'lp', 'ii', 'iii', 'iv', 'vi', 'usa', 'pmb'}


def owner_case(name):
    """Title-case an assessor owner name without mangling ordinals, roman
    numerals, or entity suffixes. Names otherwise stay exactly as recorded."""
    words = name.strip().split()
    out = []
    for i, w in enumerate(words):
        low = w.lower().strip('.,')
        if low in UPPER:
            out.append(w.upper().strip('.,') + ('.' if w.endswith('.') else ''))
        elif low in LOWER and i not in (0, len(words) - 1):
            out.append(low)
        elif re.match(r'^\d+(st|nd|rd|th)$', low):        # 14th, 1st
            out.append(low)
        elif re.match(r'^\d', w):                          # 891, 1043
            out.append(w)
        elif '-' in w:
            out.append('-'.join(p.capitalize() for p in w.split('-')))
        else:
            out.append(w.capitalize())
    return ' '.join(out)


def trend_chip(h1, ry2025, tot3=None):
    """Compare the annualized current half-year against last full report year.
    'New' is reserved for addresses with no complaint history at all."""
    annualized = h1 * 2
    if tot3 == 0:
        return '<span class="chip up">New</span>'
    if ry2025 == 0:
        return '<span class="chip up">Up sharply</span>'
    ratio = annualized / ry2025
    if ratio >= 2:
        return '<span class="chip up">Up sharply</span>'
    if ratio >= 1.25:
        return '<span class="chip up">Up</span>'
    if ratio <= 0.75:
        return '<span class="chip down">Down</span>'
    return '<span class="chip">Steady</span>'


def load_watch_rows():
    """Current watch list from refreshed open data, joined to frozen history."""
    wl = os.path.join(PIPELINE, 'watch-list.json')
    hp = os.path.join(HERE, 'history.json')
    if not os.path.exists(wl):
        return [], []
    data = json.load(open(wl))
    hist = json.load(open(hp))['counts'] if os.path.exists(hp) else {}
    SX = {'pleasant': 'Pleasant St', 'college': 'College Ave', 'aurora': 'Aurora Ave',
          'broadway': 'Broadway', 'pennsylvania': 'Pennsylvania Ave', 'grandview': 'Grandview Ave',
          'university': 'University Ave', 'euclid': 'Euclid Ave', 'baseline': 'Baseline Rd',
          'marine': 'Marine St', 'lincoln': 'Lincoln Pl', 'cascade': 'Cascade Ave'}

    def disp(key):
        parts = key.split(' ', 1)
        if len(parts) != 2:
            return key.title()
        num, street = parts
        if street in SX:
            return f'{num} {SX[street]}'
        if re.match(r'^\d+(st|nd|rd|th)$', street):
            return f'{num} {street} St'
        return f'{num} {street.title()} St'

    recent_by = {r['addr']: r['recent'] for r in data['rows']}
    current = []
    for r in data['rows']:
        h = hist.get(r['addr'], {})
        earlier = r['prior'] + h.get('ry2023', 0) + h.get('ry2024', 0) + h.get('ry2025', 0)
        current.append({'property': disp(r['addr']), 'recent': r['recent'],
                        'prior': earlier, 'ry2025': h.get('ry2025', 0)})
    off = []
    for addr, h in hist.items():
        if h.get('ry2025', 0) >= 5 and recent_by.get(addr, 0) < max(2, h['ry2025'] // 3):
            off.append({'property': disp(addr), 'ry2025': h['ry2025'],
                        'h1_2026': recent_by.get(addr, 0)})
    off.sort(key=lambda r: -r['ry2025'])
    return current, off[:8]


def copy_assets():
    os.makedirs(ASSETS, exist_ok=True)
    for name in ('chart_monthly.png', 'chart_h1.png', 'chart_heatmap.png'):
        src = os.path.join(PIPELINE, name)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(ASSETS, name))
    # reports, if placed alongside
    for key, fname in SITE['reports'].items():
        src = os.path.join(PIPELINE, fname)
        if os.path.exists(src):
            shutil.copy2(src, os.path.join(ASSETS, fname))


def asset(name):
    return os.path.exists(os.path.join(ASSETS, name))


# ---------------------------------------------------------------- pages
def build_home():
    doors = '\n'.join(
        f'      <a class="door" href="{href}"><strong>{esc(t)}</strong><span>{esc(d)}</span></a>'
        for t, d, href in HOME['doors'])
    chart = ''
    if asset('chart_monthly.png'):
        chart = ('    <figure><img src="assets/chart_monthly.png" alt="University Hill noise complaints per month, '
                 'January 2023 through July 2026">'
                 '<figcaption>Noise complaints per month on University Hill, from Boulder Police dispatch records. '
                 'The dashed line marks November 2025, when police expanded the Hill enforcement team.</figcaption></figure>')
    body = f"""    <h1>{esc(HOME['headline'])}<span class="sub">{esc(HOME['headline_2'])}</span></h1>
    <p class="lede">{esc(HOME['mission'])}</p>
    <div class="hero"><p>{esc(HOME['stat_block'])}</p></div>
{chart}
    <div class="doors">
{doors}
    </div>"""
    page('index.html', 'Home', body)


def build_reports():
    items = []
    for title, key, blurb in REPORTS['items']:
        fname = SITE['reports'][key]
        link = (f'<a class="dl" href="assets/{fname}">Download the PDF →</a>'
                if asset(fname) else '<span class="chip">PDF coming with the final release</span>')
        items.append(f"""    <div class="reportcard">
      <h3>{esc(title)}</h3>
      <p>{esc(blurb)}</p>
      {link}
    </div>""")
    findings = '\n'.join(f'      <li>{esc(f)}</li>' for f in REPORTS['findings'])
    charts = ''
    for name, alt, cap in [
        ('chart_h1.png', 'First-half noise complaints by year',
         'First-half (January–June) complaints from University Hill addresses: 248, 234, 236, then 353 in 2026.'),
        ('chart_heatmap.png', 'Complaints by day of week and hour',
         'When complaints happen. Half of all complaints land Thursday–Saturday between 9 p.m. and 2 a.m.')]:
        if asset(name):
            charts += (f'    <figure><img src="assets/{name}" alt="{esc(alt)}">'
                       f'<figcaption>{esc(cap)}</figcaption></figure>\n')
    body = f"""    <h1>The Reports</h1>
    <p class="lede">{esc(REPORTS['intro'])}</p>
{chr(10).join(items)}
    <h2>{esc(REPORTS['findings_title'])}</h2>
    <ul class="clean">
{findings}
    </ul>
{charts}    <div class="callout"><p>Want each report when it publishes? Email
      <a href="mailto:{SITE['email']}">{SITE['email']}</a> and we will add you to the list.</p></div>"""
    page('reports.html', 'The Reports', body)


def build_watch():
    current, off = load_watch_rows()
    wl = os.path.join(PIPELINE, 'watch-list.json')
    window = json.load(open(wl)).get('window', '') if os.path.exists(wl) else ''
    if current:
        rows = []
        for r in current:
            h1 = int(r['recent']); prior = r['prior']
            trend = trend_chip(h1, r['ry2025'], prior)
            rows.append(f'        <tr><td>{esc(r["property"])}</td>'
                        f'<td class="num">{h1}</td><td class="num">{prior}</td><td>{trend}</td></tr>')
        current_tbl = f"""    <div class="tablewrap">
      <table>
        <thead><tr><th>Address</th><th class="num">Complaints, last 12 months</th>
          <th class="num">Complaints, earlier years</th><th>Trend</th></tr></thead>
        <tbody>
{chr(10).join(rows)}
        </tbody>
      </table>
    </div>"""
    else:
        current_tbl = ('    <div class="callout plain"><p>The current table is generated from the analysis pipeline '
                       'at build time.</p></div>')
    if off:
        orows = '\n'.join(
            f'        <tr><td>{esc(r["property"])}</td><td class="num">{r["ry2025"]}</td>'
            f'<td class="num">{r["h1_2026"]}</td><td><span class="chip down">Off the list</span></td></tr>'
            for r in off)
        off_tbl = f"""    <div class="tablewrap">
      <table>
        <thead><tr><th>Address</th><th class="num">Complaints, Oct 2024–Oct 2025</th>
          <th class="num">Complaints, last 12 months</th><th>Status</th></tr></thead>
        <tbody>
{orows}
        </tbody>
      </table>
    </div>"""
    else:
        off_tbl = ''
    body = f"""    <h1>The Watch List</h1>
    <p class="lede">{esc(WATCH['intro'])}</p>
    <div class="callout">
      <p><strong>{esc(WATCH['disclaimer_title'])}.</strong> {fmt(WATCH['disclaimer'])}</p>
    </div>
    <p class="updated">{esc(WATCH['as_of_prefix'])} <strong>{esc(window)}</strong>. {esc(WATCH['as_of_suffix'])}</p>
    <div class="callout plain"><p>{esc(WATCH['criteria'])}</p></div>
    <h2>{esc(WATCH['current_title'])}</h2>
{current_tbl}
    <h2>{esc(WATCH['off_title'])}</h2>
    <p>{esc(WATCH['off_intro'])}</p>
{off_tbl}
    <h2>{esc(WATCH['owners_title'])}</h2>
    <p>{esc(WATCH['owners'])}</p>"""
    page('watch-list.html', 'The Watch List', body)


def build_law():
    secs = '\n'.join(f'    <h2>{esc(t)}</h2>\n    <p>{b}</p>' for t, b in LAW['sections'])
    body = f"""    <h1>Know the Law</h1>
    <p class="lede">{esc(LAW['intro'])}</p>
{secs}
    <div class="callout plain"><p>{esc(LAW['note'])}</p></div>"""
    page('know-the-law.html', 'Know the Law', body)


def build_health():
    pts = '\n'.join(f'      <li><strong>{esc(l)}</strong> {esc(b)}</li>' for l, b in HEALTH['points'])
    cites = '\n'.join(f'      <li><a href="{u}">{esc(t)}</a></li>' for t, u in HEALTH['citations'])
    body = f"""    <h1>Noise &amp; Health</h1>
    <p class="lede">{esc(HEALTH['intro'])}</p>
    <ul class="clean">
{pts}
    </ul>
    <div class="hero"><p>{esc(HEALTH['close'])}</p></div>
    <h2>Sources</h2>
    <ul class="clean">
{cites}
    </ul>"""
    page('health.html', 'Noise &amp; Health', body)


def build_asks():
    groups = []
    for gname, items in ASKS['groups']:
        rows = '\n'.join(
            f'      <div class="ask"><div class="body">{esc(text)}</div>'
            f'<div><span class="chip">{esc(status)}</span></div></div>'
            for text, status in items)
        groups.append(f'    <h2>{esc(gname)}</h2>\n    <div class="asks-group">\n{rows}\n    </div>')
    body = f"""    <h1>What We’re Asking For</h1>
    <p class="lede">{esc(ASKS['intro'])}</p>
    <div class="callout">
      <p><strong>{esc(ASKS['scope_title'])}.</strong> {esc(ASKS['scope'])}</p>
    </div>
    <div class="callout plain"><p>{fmt(ASKS['feedback'])}</p></div>
{chr(10).join(groups)}
    <p>{esc(ASKS['close'])}</p>"""
    page('asks.html', "What We're Asking For", body)


def build_residents():
    steps = '\n'.join(f'      <li>{fmt(s)}</li>' for s in RESIDENTS['steps'])
    body = f"""    <h1>For Residents</h1>
    <h2>{esc(RESIDENTS['title'])}</h2>
    <p class="lede">{esc(RESIDENTS['intro'])}</p>
    <ol class="steps">
{steps}
    </ol>
    <h2>{esc(RESIDENTS['join_title'])}</h2>
    <p>{esc(RESIDENTS['join'])}</p>
    <div class="callout"><p>Write to <a href="mailto:{SITE['email']}">{SITE['email']}</a> to join the list
      or report a chronic problem address.</p></div>"""
    page('residents.html', 'For Residents', body)


def build_about():
    how = '\n'.join(f'      <li><strong>{esc(l)}</strong> {esc(b)}</li>' for l, b in ABOUT['how'])
    gov = '\n'.join(f'      <li><strong>{esc(l)}</strong> {esc(b)}</li>' for l, b in ABOUT['governance'])
    body = f"""    <h1>About</h1>
    <h2>{esc(ABOUT['mission_title'])}</h2>
    <p class="lede">{esc(ABOUT['mission'])}</p>
    <h2>{esc(ABOUT['how_title'])}</h2>
    <ul class="clean">
{how}
    </ul>
    <h2>{esc(ABOUT['governance_title'])}</h2>
    <ul class="clean">
{gov}
    </ul>
    <h2>{esc(ABOUT['who_title'])}</h2>
    <p>{esc(ABOUT['who'])}</p>
    <div class="callout plain"><p>{esc(ABOUT['independence'])}</p></div>
    <h2>{esc(ABOUT['contact_title'])}</h2>
    <p>{fmt(ABOUT['contact'])}</p>
    <p>{fmt(ABOUT['donate'])}</p>
    <p>{esc(ABOUT['feedback'])}</p>"""
    page('about.html', 'About', body)


def build_data():
    live = '\n'.join(
        f'      <li><a href="{u}">{esc(t)}</a> — {esc(d)}</li>' for t, u, d in DATA['live'])
    groups = []
    for gname, items in DATA['files']:
        lis = []
        for label, url, desc in items:
            head = (f'<a href="{url}">{esc(label)}</a>' if url
                    else f'{esc(label)} <span class="chip">posted with the final report</span>')
            lis.append(f'      <li>{head} — {esc(desc)}</li>')
        groups.append(f'    <h3>{esc(gname)}</h3>\n    <ul class="clean">\n' + '\n'.join(lis) + '\n    </ul>')
    if SITE['source_data_link']:
        link = (f'    <div class="callout"><p><a href="{SITE["source_data_link"]}">'
                'Download the full source-data folder →</a> Includes a README data dictionary '
                'describing every file and field.</p></div>')
    else:
        link = ''
    body = f"""    <h1>Source Data</h1>
    <p class="lede">{esc(DATA['intro'])}</p>
{link}
    <h2>{esc(DATA['live_title'])}</h2>
    <ul class="clean">
{live}
    </ul>
    <h2>{esc(DATA['files_title'])}</h2>
{chr(10).join(groups)}
    <h2>{esc(DATA['notes_title'])}</h2>
    <p>{esc(DATA['notes'])}</p>"""
    page('data.html', 'Source Data', body)


PAGES = [fn for fn, _ in NAV]


def main():
    os.makedirs(ASSETS, exist_ok=True)
    # Remove only what we generate. Never touch the repo tree itself.
    for fn in PAGES:
        fp = os.path.join(OUT, fn)
        if os.path.exists(fp):
            os.remove(fp)
    if os.path.isdir(ASSETS):
        shutil.rmtree(ASSETS)
    copy_assets()
    build_home(); build_reports(); build_watch(); build_law()
    build_health(); build_asks(); build_residents(); build_about(); build_data()
    with open(os.path.join(OUT, 'CNAME'), 'w') as f:
        f.write(SITE['domain'] + '\n')
    open(os.path.join(OUT, '.nojekyll'), 'w').close()
    built = sorted(p for p in PAGES if os.path.exists(os.path.join(OUT, p)))
    print(f'built {len(built)} pages in {OUT}')
    for p_ in built:
        print('  ', p_, f'{os.path.getsize(os.path.join(OUT, p_))/1024:.1f} KB')


if __name__ == '__main__':
    main()
