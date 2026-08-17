#!/usr/bin/env python3
"""Refresh the data behind the site: fetch → archive → analyse.

    python3 pipeline/update.py     # then: python3 pipeline/build.py

Pulls the two City of Boulder open-data feeds, archives an immutable monthly
snapshot of the rolling rental feed (whose 365-day window otherwise discards
older exact-address records permanently), and writes the analysis files the
site build consumes. No credentials needed — both feeds are public.
"""
import csv, datetime, json, os, re, urllib.parse, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ARCHIVE = os.path.join(HERE, 'archive')
OUT = os.path.join(HERE, 'build-input')
os.makedirs(ARCHIVE, exist_ok=True)
os.makedirs(OUT, exist_ok=True)

ARCGIS = 'https://services.arcgis.com/ePKBjXrBZ2vEEgWd/arcgis/rest/services'
NOISEB = f'{ARCGIS}/Boulder_PD_Calls_For_Service/FeatureServer/0/query'
RENTAL = f'{ARCGIS}/Rental_Property_Calls_for_Service_Past_365_Days/FeatureServer/0/query'

SUFFIXES = {'st', 'street', 'ave', 'avenue', 'dr', 'drive', 'pl', 'place', 'ct', 'court',
            'blvd', 'boulevard', 'way', 'rd', 'road', 'ln', 'lane', 'cir', 'circle',
            'ter', 'terrace'}


def fetch_all(base, where):
    out, offset = [], 0
    while True:
        url = base + '?' + urllib.parse.urlencode({
            'where': where, 'outFields': '*', 'returnGeometry': 'false',
            'resultOffset': str(offset), 'resultRecordCount': '2000', 'f': 'json'})
        with urllib.request.urlopen(url, timeout=180) as r:
            data = json.loads(r.read())
        if 'error' in data:
            raise SystemExit(f'ArcGIS error: {data["error"]}')
        batch = data.get('features', [])
        out.extend(batch)
        if not data.get('exceededTransferLimit') and len(batch) < 2000:
            return out
        offset += len(batch)


def norm(a):
    a = re.sub(r'[.,#]', ' ', str(a or '').lower().strip())
    a = re.sub(r'\s+', ' ', a)
    toks = [t for t in a.split(' ') if t]
    while toks and toks[-1] in SUFFIXES:
        toks = toks[:-1]
    return ' '.join(toks)


def block(addr):
    n = norm(addr)
    parts = n.split(' ', 1)
    if len(parts) != 2:
        return None
    num, street = parts
    if re.match(r'^\d+$', num):
        return (f'{int(num)//100}xx', street)
    m = re.match(r'^(\d*)x+$', num)
    return ((m.group(1) or '0') + 'xx', street) if m else None


def ts(ms):
    return datetime.datetime(1970, 1, 1) + datetime.timedelta(milliseconds=ms) if ms else None


def load_zone():
    exact, blocks = set(), set()
    with open(os.path.join(HERE, 'hill-addresses.csv'), newline='', encoding='utf-8-sig') as f:
        r = csv.reader(f)
        next(r, None)
        for row in r:
            if row and row[0].strip():
                exact.add(norm(row[0]))
                b = block(row[0])
                if b:
                    blocks.add(b)
    return exact, blocks


THRESHOLD = 6   # complaints in the trailing 12 months required to appear publicly


def main():
    today = datetime.date.today()
    exact, blocks = load_zone()
    print(f'zone: {len(exact)} addresses, {len(blocks)} blocks')

    noiseb = fetch_all(NOISEB, "Problem='NOISEB-Noise Complaint'")
    print(f'citywide noise calls: {len(noiseb)}')

    rental = fetch_all(RENTAL, "call_type='NOISE COMPLAINT'")
    print(f'rental noise calls (rolling 365d): {len(rental)}')
    snap = os.path.join(ARCHIVE, f'rental-noise-{today:%Y-%m}.json')
    if os.path.exists(snap):
        print(f'snapshot for {today:%Y-%m} already archived')
    else:
        with open(snap, 'w') as f:
            json.dump(rental, f)
        print(f'archived -> {os.path.relpath(snap, ROOT)}')

    # Merge every archived snapshot so exact-address history outlives the window
    merged = {}
    for fn in sorted(os.listdir(ARCHIVE)):
        if fn.endswith('.json'):
            for feat in json.load(open(os.path.join(ARCHIVE, fn))):
                a = feat['attributes']
                k = a.get('call_number') or f'{a.get("start_time")}|{a.get("address")}'
                merged[k] = a
    print(f'exact-address history after merge: {len(merged)} calls')

    # Anchor to the last COMPLETE calendar month. The data below refreshes as
    # often as this runs, but the published watch list only moves when a month
    # closes — so an address near the threshold cannot flicker on and off.
    first_of_this_month = datetime.datetime(today.year, today.month, 1)
    window_end = first_of_this_month
    window_start = datetime.datetime(window_end.year - 1, window_end.month, 1)
    cutoff = window_start
    recent, prior = {}, {}
    for a in merged.values():
        d, key = ts(a.get('start_time')), norm(a.get('address'))
        if not d or key not in exact:
            continue
        if window_start <= d < window_end:
            recent[key] = recent.get(key, 0) + 1
        elif d < window_start:
            prior[key] = prior.get(key, 0) + 1

    rows = sorted(({'addr': k, 'recent': v, 'prior': prior.get(k, 0)}
                   for k, v in recent.items() if v >= THRESHOLD),
                  key=lambda r: -r['recent'])
    print(f'watch-list window: {window_start:%Y-%m} .. {window_end - datetime.timedelta(days=1):%Y-%m} '
          f'(complete months only)')
    print(f'watch list: {len(rows)} addresses with {THRESHOLD}+ complaints in that window')
    json.dump({'as_of': str(today),
               'window': f'{window_start:%B %Y} through {window_end - datetime.timedelta(days=1):%B %Y}',
               'rows': rows},
              open(os.path.join(OUT, 'watch-list.json'), 'w'), indent=1)

    monthly, enf = {}, {}
    for feat in noiseb:
        a = feat['attributes']
        d, b = ts(a.get('Response_Date')), block(a.get('Address'))
        if not (d and b and b in blocks):
            continue
        monthly[f'{d:%Y-%m}'] = monthly.get(f'{d:%Y-%m}', 0) + 1
        e = enf.setdefault(str(d.year), {'calls': 0, 'tickets': 0})
        e['calls'] += 1
        disp = a.get('Call_Disposition') or ''
        if 'SB' in disp or 'Summons' in disp:
            e['tickets'] += 1
    json.dump(monthly, open(os.path.join(OUT, 'monthly.json'), 'w'), indent=1)
    json.dump(enf, open(os.path.join(OUT, 'enforcement.json'), 'w'), indent=1)
    for y in sorted(enf):
        print(f'  {y}: {enf[y]["tickets"]} tickets / {enf[y]["calls"]} calls')
    print('data refresh complete')


if __name__ == '__main__':
    main()
