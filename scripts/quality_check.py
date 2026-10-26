#!/usr/bin/env python3
"""MONOPLATOON quality check: verifies the design rules that a script can check.

    python scripts/quality_check.py --source          # game text and specs only (no build needed)
    python scripts/quality_check.py --pdf dist        # built PDFs only
    python scripts/quality_check.py --source --pdf dist --report qa-report.md

Errors fail the run (exit 1). Warnings are printed but pass. Inside GitHub Actions every finding
becomes an annotation and the report is added to the job summary.

The checks map to the rules in CLAUDE.md and docs/DESIGN_BRIEF.md. Anything a script cannot judge
(is it funny, does it punch at the system and not the soldier) stays a human review item.
"""
import argparse
import os
import re
import sys
import unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, 'src'))

IN = 72.0
LETTER = (612.0, 792.0)
GH = os.environ.get('GITHUB_ACTIONS') == 'true'

FILES = {
    'stickers': 'Monoplatoon_Phase1_Board_Stickers.pdf',
    'decks': 'Monoplatoon_Phase2_Decks.pdf',
    'people': 'Monoplatoon_Phase3_Characters_and_Deeds.pdf',
    'table': 'Monoplatoon_Phase4_Table_Pieces.pdf',
    'rules': 'Monoplatoon_Phase5_Rulebook.pdf',
    'combined': 'Monoplatoon_Complete_Print_Set.pdf',
}
PAGES = {'stickers': 6, 'decks': 8, 'people': 10, 'table': 24, 'rules': 7, 'combined': 55}

# ---------------------------------------------------------------------------------------- results
RESULTS = []   # (level, area, message)


def ok(area, msg): RESULTS.append(('pass', area, msg))
def warn(area, msg): RESULTS.append(('warning', area, msg))
def err(area, msg): RESULTS.append(('error', area, msg))


def expect(cond, area, msg, level='error'):
    if cond:
        ok(area, msg)
    elif level == 'warning':
        warn(area, msg)
    else:
        err(area, msg)
    return cond


def close(a, b, tol=0.01):
    return abs(a - b) <= tol


# ---------------------------------------------------------------------------------------- reference data
# Standard US Monopoly: position -> price for every ownable space.
STD_PRICES = {2: 60, 4: 60, 6: 200, 7: 100, 9: 100, 10: 120, 12: 140, 13: 150, 14: 140, 15: 160, 16: 200,
              17: 180, 19: 180, 20: 200, 22: 220, 24: 220, 25: 240, 26: 200, 27: 260, 28: 260, 29: 150,
              30: 280, 32: 300, 33: 300, 35: 320, 36: 200, 38: 350, 40: 400}
STD_GROUPS = {'brown': [2, 4], 'lblue': [7, 9, 10], 'pink': [12, 14, 15], 'orange': [17, 19, 20], 'red': [22, 24, 25],
              'yellow': [27, 28, 30], 'green': [32, 33, 35], 'dblue': [38, 40], 'rr': [6, 16, 26, 36], 'util': [13, 29]}
STD_DECK_SPACES = {'guidance': [8, 23, 37], 'lawyer': [3, 18, 34]}
STD_CORNERS = [1, 11, 21, 31]
STD_TAX = {5: ('200', '10%'), 39: ('100',)}
# Standard rent ladders (base, 1-4 houses, hotel) keyed by price; Baltic is the one exception.
STD_RENT = {60: (2, 10, 30, 90, 160, 250), 100: (6, 30, 90, 270, 400, 550), 120: (8, 40, 100, 300, 450, 600),
            140: (10, 50, 150, 450, 625, 750), 160: (12, 60, 180, 500, 700, 900), 180: (14, 70, 200, 550, 750, 950),
            200: (16, 80, 220, 600, 800, 1000), 220: (18, 90, 250, 700, 875, 1050), 240: (20, 100, 300, 750, 925, 1100),
            260: (22, 110, 330, 800, 975, 1150), 280: (24, 120, 360, 850, 1025, 1200), 300: (26, 130, 390, 900, 1100, 1275),
            320: (28, 150, 450, 1000, 1200, 1400), 350: (35, 175, 500, 1100, 1300, 1500), 400: (50, 200, 600, 1400, 1700, 2000)}
STD_BALTIC = (4, 20, 60, 180, 320, 450)

RANKS = {'PVT', 'PV2', 'PFC', 'SPC', 'CPL', 'SGT', 'SSG', 'SFC', 'MSG', '1SG', 'SGM', 'CSM',
         'WO1', 'CW2', 'CW3', 'CW4', 'CW5', '2LT', '1LT', 'CPT', 'MAJ'}
POSES = {'shrug', 'salute', 'asleep', 'hawaiian', 'point', 'count', 'hammer', 'pin', 'stand'}
KEYWORDS = ('GUIDANCE', 'SMOKE', 'UNIFORM', 'PAPERWORK')

# Real people must never be depicted. Names of recent officials and Hasbro's own characters.
REAL_PEOPLE = ['Trump', 'Hegseth', 'Biden', 'Obama', 'Harris', 'Vance', 'Pence', 'Milley', 'Esper', 'Mattis',
               'Lloyd Austin', 'Driscoll', 'Caine', 'Bush', 'Clinton', 'Rumsfeld', 'Gates']
HASBRO = ['Pennybags', 'Mr. Monopoly', 'Rich Uncle', 'Hasbro', 'Parker Brothers']


# ---------------------------------------------------------------------------------------- source checks
def all_text_fields():
    """Every string players will read, with a label saying where it lives."""
    import data
    out = []
    for sp in data.BOARD:
        for k, v in (('name', sp[1]), ('flavor', sp[4]), ('gloss', sp[6])):
            if v:
                out.append(('board %d %s' % (sp[0], k), str(v)))
    for deck, cards in (('guidance', data.GUIDANCE), ('lawyer', data.LAWYER)):
        for c in cards:
            for v in c[:4]:
                if v:
                    out.append(('%s "%s"' % (deck, c[0]), v))
    for c in data.BUILDING:
        for v in (c[1], c[3], c[4]):
            out.append(('building "%s"' % c[1], v))
    for c in data.CHARACTERS + [data.FIRST_SERGEANT]:
        for v in c[:4]:
            out.append(('character "%s"' % c[0], v))
    for r in data.READINESS:
        out.append(('readiness', r))
    for k, v in data.GLOSSARY:
        out.append(('glossary "%s"' % k, k + ' ' + v))
    return out


def gloss_term(s):
    m = re.match(r"^([A-Za-z0-9'\- ]{1,30}):\s", s or '')
    return m.group(1).strip() if m else None


def check_source():
    import data
    A = 'board'
    B = data.BOARD
    expect([sp[0] for sp in B] == list(range(1, 41)), A, '40 spaces numbered 1-40 in order')
    by = {sp[0]: sp for sp in B}
    for n, price in STD_PRICES.items():
        expect(by[n][3] == price, A, 'space %d "%s" costs $%s (standard is $%d)' % (n, by[n][1], by[n][3], price))
    for grp, spaces in STD_GROUPS.items():
        got = sorted(n for n, sp in by.items() if sp[2] == grp)
        expect(got == spaces, A, 'group %s sits on spaces %s' % (grp, spaces))
    expect(sorted(n for n, sp in by.items() if sp[2] == 'corner') == STD_CORNERS, A, 'corners on 1, 11, 21, 31')
    for deck, spaces in STD_DECK_SPACES.items():
        want = 'COMMAND GUIDANCE' if deck == 'guidance' else 'BARRACKS LAWYER'
        expect(all(by[n][1] == want for n in spaces), A, '%s on spaces %s' % (want, spaces))
    for n, parts in STD_TAX.items():
        expect(by[n][2] == 'tax' and all(p in str(by[n][3]) for p in parts), A, 'tax space %d charges %s' % (n, ' or '.join('$' + p if p[-1] != '%' else p for p in parts)))
    names = [sp[1] for sp in B if sp[2] not in ('deck',)]
    expect(len(names) == len(set(names)), A, 'every non-card space has a unique name')
    for sp in B:
        if sp[2] in data.GROUP_NAME or sp[2] in ('corner', 'tax'):
            expect(bool(sp[4]), A, 'space %d "%s" has a joke (flavor line)' % (sp[0], sp[1]))
    # the ladder: price never drops as the colour groups climb
    ladder = [max(by[n][3] for n in STD_GROUPS[g]) for g in ('brown', 'lblue', 'pink', 'orange', 'red', 'yellow', 'green', 'dblue')]
    expect(ladder == sorted(ladder), A, 'property groups climb in price from Reception to The Building')

    A = 'deeds'
    for price, (rents, house, mort) in data.RENT.items():
        expect(rents == STD_RENT[price], A, 'rent ladder for $%d matches standard Monopoly' % price)
        expect(mort == price // 2, A, 'mortgage for $%d is half price' % price)
    expect(data.RENT_BALTIC[0] == STD_BALTIC, A, 'Baltic-position rent ladder matches standard Monopoly')
    deeds = [sp for sp in B if sp[2] in data.GROUP_NAME]
    expect(len(deeds) == 28, A, '28 ownable spaces, so 28 deeds')

    # ---- Command Guidance = Chance, one for one
    A = 'command guidance'
    G = data.GUIDANCE
    expect(len(G) == 16, A, '16 cards')
    rules = [c[1] for c in G]
    def count(pat, src): return sum(1 for r in src if re.search(pat, r, re.I))
    chance = [
        (r'nearest Rotation.*twice', 2, 'advance to nearest railroad, pay double'),
        (r'nearest (Lender|Help Desk|utility).*10x', 1, 'advance to nearest utility, pay 10x'),
        (r'^Advance to Payday\. Collect \$200', 1, 'advance to GO'),
        (r'Go directly to the CQ Desk', 1, 'go to jail'),
        (r'Go back 3 spaces', 1, 'go back 3 spaces'),
        (r'Leave the CQ Desk free', 1, 'get out of jail free'),
        (r'\$25 per Barracks Repair and \$100 per Privatized', 1, 'repairs $25 / $100'),
        (r'^Pay \$15', 1, 'pay $15'),
        (r'Pay each player \$50', 1, 'pay each player $50'),
        (r'Bank pays you \$50', 1, 'collect $50'),
        (r'^Collect \$150\b', 1, 'collect $150'),
        (r'^Advance to (?!the nearest)(The|Hooah|NTC)', 4, 'four named advances'),
    ]
    for pat, n, label in chance:
        got = count(pat, rules)
        expect(got == n, A, 'deck math: %s x%d (found %d)' % (label, n, got))
    tags = [c[3] for c in G]
    for kw, n in (('GUIDANCE', 4), ('SMOKE', 3), ('UNIFORM', 1)):
        got = sum(1 for t in tags if t.startswith(kw))
        expect(got == n, A, '%d %s-tagged cards (found %d)' % (n, kw, got))

    # ---- Barracks Lawyer = Community Chest, one for one
    A = 'barracks lawyer'
    L = data.LAWYER
    expect(len(L) == 16, A, '16 cards')
    rules = [c[1] for c in L]
    chest = [
        (r'^Advance to Payday\. Collect \$200', 1, 'advance to GO'),
        (r'^Collect \$200\b', 1, 'bank error, collect $200'),
        (r'^Collect \$100\b', 3, 'collect $100 three times'),
        (r'^Collect \$50\b', 1, 'collect $50'),
        (r'^Collect \$25\b', 1, 'collect $25'),
        (r'^Collect \$20\b', 1, 'collect $20'),
        (r'^Collect \$10 from every player', 1, 'collect $10 from every player'),
        (r'^Collect \$10\b(?! from)', 1, 'collect $10'),
        (r'^Pay \$50\b', 2, 'pay $50 twice'),
        (r'^Pay \$100\b', 1, 'pay $100'),
        (r'\$40 per Barracks Repair and \$115 per Privatized', 1, 'repairs $40 / $115'),
        (r'Go directly to the CQ Desk', 1, 'go to jail'),
        (r'Leave the CQ Desk free', 1, 'get out of jail free'),
    ]
    for pat, n, label in chest:
        got = count(pat, rules)
        expect(got == n, A, 'deck math: %s x%d (found %d)' % (label, n, got))
    tags = [c[3] for c in L]
    for kw, n in (('GUIDANCE', 2), ('UNIFORM', 2), ('PAPERWORK', 1)):
        got = sum(1 for t in tags if t.startswith(kw))
        expect(got == n, A, '%d %s-tagged cards (found %d)' % (n, kw, got))

    # ---- The Building
    A = 'the building'
    D = data.BUILDING
    expect(len(D) == 18, A, '18 cards')
    for typ, n in (('DIRECTIVE', 7), ('WALK-BACK', 4), ('PAPERWORK', 4), ('UNIFORM', 3)):
        got = sum(1 for c in D if c[0] == typ)
        expect(got == n, A, '%d %s cards (found %d)' % (n, typ, got))
    expect(all(c[2] in ('watch', 'phone', 'none') for c in D), A, 'every issuer is the Secretary (watch), the Commander-in-Chief (phone) or none')
    expect(all(c[2] == 'none' for c in D if c[0] == 'PAPERWORK'), A, 'Paperwork cards have no issuer')
    expect(all(c[2] != 'none' for c in D if c[0] != 'PAPERWORK'), A, 'Directives, Walk-Backs and Uniform cards name an issuer')
    for c in D:
        if c[0] == 'PAPERWORK':
            expect(c[3].startswith('Step token on'), A, 'Paperwork "%s" names the action its Step token goes on' % c[1])
    expect(all(c[3] and c[4] for c in D), A, 'every Building card has a rule and a joke')

    # ---- characters
    A = 'characters'
    C = data.CHARACTERS
    expect(10 <= len(C) <= 12, A, '10 to 12 characters (found %d)' % len(C))
    expect(len({c[0] for c in C}) == len(C), A, 'character names are unique')
    for c in C:
        rank = c[0].split()[0]
        expect(rank in RANKS, A, '"%s" starts with a real Army rank abbreviation' % c[0])
        expect(all(c[:4]), A, '"%s" has a rule, a joke and a gloss' % c[0])
        expect(c[4] in POSES, A, '"%s" uses a drawn mascot pose (%s)' % (c[0], c[4]))
        expect(len(c[1]) <= 140, A, '"%s" rule fits on the card (%d of 140 characters)' % (c[0], len(c[1])))
    expect(len(data.READINESS) == 6, A, '6 Readiness cards')

    # ---- glossary
    A = 'glossary'
    keys = [k for k, _ in data.GLOSSARY]
    expect(keys == sorted(keys, key=str.lower), A, 'glossary is alphabetized')
    expect(len(keys) == len({k.lower() for k in keys}), A, 'glossary has no duplicate terms')
    lower = {k.lower() for k in keys}
    glosses = [sp[6] for sp in B if sp[6]] + [c[3] for c in data.CHARACTERS + [data.FIRST_SERGEANT]]
    glosses += [c[3] for c in data.GUIDANCE + data.LAWYER if c[3] and not c[3].startswith(KEYWORDS)]
    for g in glosses:
        t = gloss_term(g)
        if t:
            expect(t.lower() in lower, A, 'gloss term "%s" is in the glossary' % t)
    for k, v in data.GLOSSARY:
        expect(len(v) <= 160, A, 'glossary entry "%s" is one line (%d of 160 characters)' % (k, len(v)), 'warning')

    # ---- tone and legal
    A = 'tone and legal'
    fields = all_text_fields()
    for where, text in fields:
        for name in REAL_PEOPLE:
            if re.search(r'\b%s\b' % re.escape(name), text):
                err(A, '%s names a real person "%s": "%s"' % (where, name, text[:80]))
        for name in HASBRO:
            if name.lower() in text.lower():
                err(A, '%s uses Hasbro\'s name or character "%s"' % (where, name))
        bad = [ch for ch in text if unicodedata.category(ch) == 'So' or ord(ch) > 0x2600]
        if bad:
            err(A, '%s contains an emoji or symbol %r' % (where, ''.join(bad)))
    if not any(r[0] != 'pass' and r[1] == A for r in RESULTS):
        ok(A, 'no real people, no Hasbro characters, no emoji in %d text fields' % len(fields))

    # ---- production specs (docs/DESIGN_BRIEF.md)
    A = 'specs'
    import mp, cards, phase1, phase4
    expect(mp.MINT.hexval().lower() == '0xbfddc8', A, 'sticker green is #BFDDC8 (chip G)')
    expect(mp.FLAV.hexval().lower() == '0x555555', A, 'flavor and gloss text is dark grey #555555')
    expect(close(cards.CW, 2.125 * IN) and close(cards.CH, 3.1875 * IN), A, 'cards are 2 1/8 x 3 3/16 in')
    expect(cards.COLS * cards.ROWS == 9, A, 'nine cards per sheet')
    expect(close(phase1.SW, 1.625 * IN) and close(phase1.SH, 2.5625 * IN), A, 'property stickers are 1 5/8 x 2 9/16 in')
    expect(close(phase1.CS, 2.5625 * IN), A, 'corner stickers are 2 9/16 in square')
    expect(close(phase1.BAR_L, 11.6 * IN) and close(phase1.BAR_T, 2.5 * IN), A, 'centre bar is 11.6 x 2.5 in')
    expect(close(phase1.ABOVE, 0.5 * IN) and close(phase1.BELOW, 0.65 * IN), A, 'centre bar has 0.5 in green above and 0.65 in below')
    expect(close(phase1.MASC_W, 4.15 * IN) and close(phase1.MASC_H, 2.4 * IN), A, 'mascot piece is 4.15 x 2.4 in')
    src1 = open(os.path.join(ROOT, 'src', 'phase1.py')).read()
    expect('w, h = 3.45 * IN, 2.3 * IN' in src1, A, 'deck labels are 3.45 x 2.3 in')
    expect('w, h = 1.7 * IN, 1.0 * IN' in src1, A, "maker's mark is 1.7 x 1 in")
    expect(close(phase4.AW, 6 * IN) and close(phase4.AH, 4 * IN), A, 'player aids are 6 x 4 in')
    expect(close(phase4.TW, 5 * IN) and close(phase4.TH, 3 * IN), A, 'trackers are 5 x 3 in')
    expect(close(phase4.PW, 2 * IN) and close(phase4.PH, 3 * IN), A, 'form pads are 2 x 3 in')
    reqs = open(os.path.join(ROOT, 'requirements.txt')).read()
    expect(all(re.search(r'^%s==' % p, reqs, re.M) for p in ('reportlab', 'pypdf')), A, 'build libraries are pinned to exact versions')
    v = open(os.path.join(ROOT, 'VERSION')).read().strip()
    expect(bool(re.fullmatch(r'\d+\.\d+\.\d+', v)), A, 'VERSION is semantic (%s)' % v)
    cl = open(os.path.join(ROOT, 'CHANGELOG.md')).read()
    expect(re.search(r'^## \[%s\]' % re.escape(v), cl, re.M) is not None, A, 'CHANGELOG.md has an entry for %s' % v)


# ---------------------------------------------------------------------------------------- PDF checks
def page_texts(path):
    from pypdf import PdfReader
    return [re.sub(r'\s+', ' ', p.extract_text() or '') for p in PdfReader(path).pages]


def render(path, dpi=30):
    import pypdfium2 as pdfium
    doc = pdfium.PdfDocument(path)
    imgs = [doc[i].render(scale=dpi / 72).to_pil().convert('RGB') for i in range(len(doc))]
    doc.close()
    return imgs


def slot_occupancy(img, dpi):
    """Which of the nine card slots hold ink. Returns a 3x3 list of booleans."""
    import cards
    s = dpi / 72.0
    grid = [[False] * cards.COLS for _ in range(cards.ROWS)]
    g = img.convert('L')
    for i in range(cards.COLS * cards.ROWS):
        r, k = divmod(i, cards.COLS)
        x, y = cards.slot(i)
        box = (int((x + 12) * s), int((LETTER[1] - (y + cards.CH) + 12) * s), int((x + cards.CW - 12) * s), int((LETTER[1] - y - 12) * s))
        crop = g.crop(box)
        dark = sum(crop.histogram()[:200])
        grid[r][k] = dark / max(1, crop.width * crop.height) > 0.02
    return grid


def char_problems(path, pages=None, slot_pages=None, clipped_pages=()):
    """Text that leaves the page, overlaps other text, or spills out of its card."""
    import pdfplumber
    import cards
    out = []
    with pdfplumber.open(path) as pdf:
        for pi, page in enumerate(pdf.pages):
            if pages and pi + 1 not in pages:
                continue
            chars = [c for c in page.chars if c['text'].strip() and abs(c['matrix'][1]) < 0.01 and abs(c['matrix'][2]) < 0.01]  # skip rotated lettering
            if pi + 1 in clipped_pages:
                continue  # artwork deliberately drawn past a clip edge (the two-piece title bar)
            for c in chars:
                if c['x0'] < 0.15 * IN or c['x1'] > page.width - 0.15 * IN or c['top'] < 0.15 * IN or c['bottom'] > page.height - 0.15 * IN:
                    out.append((pi + 1, 'text off the printable area: "%s" at %.2f, %.2f in' % (c['text'], c['x0'] / IN, c['top'] / IN)))
                    break
            # overlap: different glyphs whose boxes intersect a lot (shadows of the same glyph are allowed)
            cells = {}
            for c in chars:
                cells.setdefault((int(c['x0'] // 20), int(c['top'] // 20)), []).append(c)
            seen = set()
            hits = 0
            for (cx, cy), group in cells.items():
                neigh = []
                for dx in (-1, 0, 1):
                    for dy in (-1, 0, 1):
                        neigh += cells.get((cx + dx, cy + dy), [])
                for a in group:
                    for b in neigh:
                        if a is b or id(b) < id(a):
                            continue
                        ix = min(a['x1'], b['x1']) - max(a['x0'], b['x0'])
                        iy = min(a['bottom'], b['bottom']) - max(a['top'], b['top'])
                        if ix <= 0 or iy <= 0:
                            continue
                        small = min((a['x1'] - a['x0']) * (a['bottom'] - a['top']), (b['x1'] - b['x0']) * (b['bottom'] - b['top']))
                        if small <= 0 or ix * iy < 0.35 * small:
                            continue
                        if a['text'] == b['text'] and abs(a['x0'] - b['x0']) < 5 and abs(a['top'] - b['top']) < 5:
                            continue  # drop shadow
                        key = (round(a['top']), round(b['top']))
                        if key in seen:
                            continue
                        seen.add(key)
                        hits += 1
                        if hits <= 2:
                            out.append((pi + 1, 'text overlaps text near %.2f, %.2f in ("%s" on "%s")' % (a['x0'] / IN, a['top'] / IN, a['text'], b['text'])))
            if slot_pages and pi + 1 in slot_pages:
                for c in chars:
                    cx, cy = (c['x0'] + c['x1']) / 2, (c['top'] + c['bottom']) / 2
                    for i in range(cards.COLS * cards.ROWS):
                        x, y = cards.slot(i)
                        top = page.height - (y + cards.CH)
                        if x < cx < x + cards.CW and top < cy < top + cards.CH:
                            if c['x0'] < x + 5 or c['x1'] > x + cards.CW - 5 or c['top'] < top + 5 or c['bottom'] > top + cards.CH - 5:
                                out.append((pi + 1, 'text spills past a card border: "%s" in slot %d' % (c['text'], i + 1)))
                            break
    return out


def check_pdfs(dist):
    import data
    v = open(os.path.join(ROOT, 'VERSION')).read().strip()
    A = 'files'
    paths = {k: os.path.join(dist, f) for k, f in FILES.items()}
    missing = [f for k, f in FILES.items() if not os.path.exists(paths[k])]
    if missing:
        err(A, 'missing build output: %s (run python build.py)' % ', '.join(missing))
        return
    from pypdf import PdfReader
    texts = {}
    for k, p in paths.items():
        r = PdfReader(p)
        expect(len(r.pages) == PAGES[k], A, '%s has %d pages (found %d)' % (FILES[k], PAGES[k], len(r.pages)))
        sizes = {(round(float(pg.mediabox.width)), round(float(pg.mediabox.height))) for pg in r.pages}
        expect(sizes == {(612, 792)}, A, '%s is all portrait US letter' % FILES[k])
        texts[k] = page_texts(p)
    zipf = os.path.join(dist, 'Monoplatoon-v%s-print.zip' % v)
    if expect(os.path.exists(zipf), A, 'print package Monoplatoon-v%s-print.zip exists' % v):
        import zipfile
        names = {os.path.basename(n) for n in zipfile.ZipFile(zipf).namelist()}
        expect(set(FILES.values()) | {'README-PRINT.txt'} <= names, A, 'zip holds every PDF and README-PRINT.txt')

    # version stamp on every page footer (the rulebook cover has no footer)
    A = 'footers'
    for k in ('stickers', 'decks', 'people', 'table', 'rules'):
        pages = texts[k][1:] if k == 'rules' else texts[k]
        bad = [i + 1 for i, t in enumerate(pages) if 'MONOPLATOON v%s' % v not in t]
        expect(not bad, A, '%s: every page footer says MONOPLATOON v%s%s' % (FILES[k], v, ' (missing on %s)' % bad if bad else ''))

    # fonts: the bundled headline faces are embedded so print shops see what you see
    A = 'fonts'
    for k in ('stickers', 'decks', 'people', 'table', 'rules'):
        r = PdfReader(paths[k])
        found = set()
        for pg in r.pages:
            fonts = (pg.get('/Resources') or {}).get('/Font') or {}
            for f in fonts.values():
                f = f.get_object()
                name = str(f.get('/BaseFont', ''))
                desc = f.get('/FontDescriptor')
                if 'DejaVu' in name and desc is not None:
                    desc = desc.get_object()
                    if any(x in desc for x in ('/FontFile', '/FontFile2', '/FontFile3')):
                        found.add('embedded')
                    else:
                        found.add('not embedded')
        expect(found == {'embedded'}, A, '%s embeds the DejaVu headline font' % FILES[k])

    # content made it onto the page
    A = 'content'
    allt = lambda k: ' '.join(texts[k])
    st = allt('stickers')
    missing = [sp[1] for sp in data.BOARD if sp[2] != 'deck' and sp[1].split(',')[0].split()[0] not in st]
    expect(not missing, A, 'every board space name is on the sticker sheets%s' % (': missing ' + ', '.join(missing) if missing else ''))
    prices = [sp[3] for sp in data.BOARD if isinstance(sp[3], int)]
    got = len(re.findall(r'PRICE \$\d+', st))
    expect(got == len(prices), A, '%d priced stickers carry PRICE $ (found %d)' % (len(prices), got))
    dk = allt('decks')
    for deck, cards_ in (('Command Guidance', data.GUIDANCE), ('Barracks Lawyer', data.LAWYER)):
        miss = [c[0] for c in cards_ if c[1][:24] not in dk]
        expect(not miss, A, 'every %s rule is printed%s' % (deck, ': missing ' + ', '.join(miss) if miss else ''))
    miss = [c[1] for c in data.BUILDING if c[3][:24] not in dk]
    expect(not miss, A, 'every Building rule is printed%s' % (': missing ' + ', '.join(miss) if miss else ''))
    pp = allt('people')
    miss = [c[0] for c in data.CHARACTERS if c[1][:24] not in pp]
    expect(not miss, A, 'every character rule is printed%s' % (': missing ' + ', '.join(miss) if miss else ''))
    miss = [r for r in data.READINESS if r[:20] not in pp]
    expect(not miss, A, 'every Readiness card is printed')
    deed_prices = sorted(int(x) for x in re.findall(r'PRICE \$(\d+)', pp))
    want = sorted(sp[3] for sp in data.BOARD if sp[2] in data.GROUP_NAME)
    expect(deed_prices == want, A, 'all 28 deeds print their purchase price (for net worth at ETS)')
    rb = allt('rules')
    miss = [k for k, _ in data.GLOSSARY if k not in rb]
    expect(not miss, A, 'every glossary term is in the rulebook%s' % (': missing ' + ', '.join(miss) if miss else ''))
    tb = allt('table')
    for form in ('DEVELOPMENTAL COUNSELING', 'REQUEST FOR LEAVE', 'MEMORANDUM FOR RECORD', 'SWORN STATEMENT', 'RISK ASSESSMENT', 'POLICY LETTER'):
        expect(form in tb, A, 'pad "%s" is printed' % form)

    # rule facts that must agree between the rulebook and the player aids
    A = 'rules consistency'
    m = re.search(r'\$1,500: two \$500s, two \$100s, two \$50s, six \$20s, five \$10s, five \$5s, five \$1s', rb)
    if expect(m is not None, A, 'rulebook lists the starting money bill by bill'):
        expect(2 * 500 + 2 * 100 + 2 * 50 + 6 * 20 + 5 * 10 + 5 * 5 + 5 * 1 == 1500, A, 'starting bills add up to $1,500')
    aids = ' '.join(texts['table'][:3])
    facts = [
        ('auctions open at $10', r'(opens|open) at \$10', ('rules', 'aids')),
        ('IG Complaint costs $50', r'IG Complaint.{0,20}\$50|pays \$50 to the bank; the 1SG draws', ('rules', 'aids')),
        ('Inspection fines $20 a piece', r'\$20 per', ('rules', 'aids')),
        ('broke = $500 stipend', r'\$500 stipend', ('rules', 'aids')),
        ('Smoke 6 = chaptered', r'(At 6 you are chaptered|Smoke 6 = chaptered)', ('rules', 'aids')),
        ('relieved at 8 Complaints', r'(At 8|At 8 you are relieved)', ('rules', 'aids')),
        ('spend $500 at 10:00', r'10:00.{0,80}\$500|\$500 of bank money', ('rules', 'aids')),
        ('90-minute clock', r'90:00|90 minutes', ('rules',)),
        ('3 to 6 players', r'3 to 6 players', ('rules',)),
        ("It's the Law", r"It's the Law", ('rules', 'aids')),
        ('two properties dealt at setup', r'Deal two to each regular player', ('rules',)),
        ('mandatory auction on declined purchases', r"If you don't, it must be auctioned", ('rules',)),
        ('nobody is eliminated', r'Nobody is ever out|nobody is eliminated', ('rules',)),
        ('Policy Shelf holds six', r'Six slots', ('rules',)),
    ]
    for label, pat, where in facts:
        for w in where:
            src = rb if w == 'rules' else aids
            expect(re.search(pat, src, re.I) is not None, A, '%s: %s' % ('rulebook' if w == 'rules' else 'player aids', label))
    expect('JRTC' in rb and 'Charge of Quarters' in rb, A, 'glossary glosses are printed in the rulebook')

    # black ink: Command Guidance and Barracks Lawyer print in black only on coloured stock
    A = 'black-ink decks'
    imgs = render(paths['decks'], 30)
    for i in range(4):
        img = imgs[i]
        coloured = sum(img.convert('HSV').split()[1].histogram()[70:])
        expect(coloured == 0, A, 'decks page %d is greyscale only (%d coloured pixels)' % (i + 1, coloured))

    # mirrored backs: every back sheet mirrors its front sheet left-to-right
    A = 'mirrored backs'
    for k, pairs in (('decks', [(5, 6), (7, 8)]), ('people', [(1, 2), (3, 4), (5, 6)])):
        imgs = render(paths[k], 30)
        for f, b in pairs:
            expect('backs' in texts[k][b - 1] and 'mirrored' in texts[k][b - 1], A, '%s page %d is labelled as the mirrored back of page %d' % (FILES[k], b, f))
            fo, bo = slot_occupancy(imgs[f - 1], 30), slot_occupancy(imgs[b - 1], 30)
            mirrored = all(bo[r][kk] == fo[r][len(fo[r]) - 1 - kk] for r in range(len(fo)) for kk in range(len(fo[r])))
            expect(mirrored, A, '%s page %d backs line up with page %d fronts after a long-edge flip' % (FILES[k], b, f))
    # single-sided: deeds and the two drawn decks have no back pages
    expect(not any('backs' in t for t in texts['decks'][:4]), A, 'Command Guidance and Barracks Lawyer are single-sided')
    expect(not any('backs' in t for t in texts['people'][6:]), A, 'deeds are single-sided')

    # layout: no text off the page, overlapping, or spilling out of a card
    A = 'layout'
    for k, slots in (('stickers', None), ('decks', set(range(1, 9))), ('people', set(range(1, 11))), ('table', None), ('rules', None)):
        probs = char_problems(paths[k], slot_pages=slots, clipped_pages=(6,) if k == 'stickers' else ())
        if probs:
            for pg, msg in probs[:12]:
                err(A, '%s page %d: %s' % (FILES[k], pg, msg))
        else:
            ok(A, '%s: no text off the page, overlapping, or outside its card' % FILES[k])


def self_test():
    """Plant known faults in a scratch PDF and make sure the layout checks catch every one."""
    import tempfile
    from reportlab.pdfgen import canvas
    import cards
    A = 'self-test'
    path = os.path.join(tempfile.mkdtemp(), 'planted.pdf')
    c = canvas.Canvas(path, pagesize=LETTER)
    c.setFont('Courier', 9)
    c.drawString(300, 400, 'OVERLAP'); c.drawString(302, 401, 'COLLIDE')        # two different words on top of each other
    c.drawString(300, 300, 'SHADOW'); c.drawString(301.5, 298.5, 'SHADOW')     # a drop shadow: must NOT be flagged
    c.drawString(LETTER[0] - 20, 200, 'OFFPAGE')                               # runs off the right edge
    x, y = cards.slot(4)
    c.rect(x, y, cards.CW, cards.CH)
    c.drawString(x + cards.CW - 30, y + cards.CH / 2, 'SPILLING OVER')         # starts in a card, runs past its border
    c.save()
    probs = [m for _, m in char_problems(path, slot_pages={1})]
    expect(any('overlaps' in m for m in probs), A, 'overlapping text is detected')
    expect(not any('"S" on "S"' in m or '"H" on "H"' in m for m in probs), A, 'drop shadows are not mistaken for overlaps')
    expect(any('off the printable area' in m for m in probs), A, 'text off the page is detected')
    expect(any('spills past a card border' in m for m in probs), A, 'text spilling out of a card is detected')


# ---------------------------------------------------------------------------------------- report
def report(path=None):
    errs = [r for r in RESULTS if r[0] == 'error']
    warns = [r for r in RESULTS if r[0] == 'warning']
    passes = [r for r in RESULTS if r[0] == 'pass']
    lines = ['# MONOPLATOON quality check', '',
             '**%s**: %d checks passed, %d warnings, %d errors.' % ('FAIL' if errs else 'PASS', len(passes), len(warns), len(errs)), '']
    if errs or warns:
        lines += ['| Level | Area | Finding |', '| --- | --- | --- |']
        lines += ['| %s | %s | %s |' % (lvl, area, msg.replace('|', '/')) for lvl, area, msg in errs + warns]
        lines.append('')
    areas = []
    for _, a, _ in RESULTS:
        if a not in areas:
            areas.append(a)
    lines += ['<details><summary>All checks by area</summary>', '', '| Area | Passed | Warnings | Errors |', '| --- | --- | --- | --- |']
    for a in areas:
        lines.append('| %s | %d | %d | %d |' % (a, sum(1 for r in passes if r[1] == a), sum(1 for r in warns if r[1] == a), sum(1 for r in errs if r[1] == a)))
    lines += ['', '</details>', '', 'Not checkable by script, so review by eye: the joke lands on the system and never the soldier; art reads at arm\'s length; stickers fit the board.']
    text = '\n'.join(lines)
    for lvl, area, msg in errs + warns:
        if GH:
            print('::%s title=QA %s::%s' % ('error' if lvl == 'error' else 'warning', area, msg))
        else:
            print('%-7s %-18s %s' % (lvl.upper(), area, msg))
    print('\n%s: %d passed, %d warnings, %d errors' % ('FAIL' if errs else 'PASS', len(passes), len(warns), len(errs)))
    if path:
        open(path, 'w').write(text + '\n')
    summ = os.environ.get('GITHUB_STEP_SUMMARY')
    if summ:
        open(summ, 'a').write(text + '\n')
    return 1 if errs else 0


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('--source', action='store_true', help='check game text and specs')
    ap.add_argument('--pdf', metavar='DIST', help='check the built PDFs in this folder')
    ap.add_argument('--report', help='write a markdown report here')
    ap.add_argument('--self-test', action='store_true', help='prove the layout checks catch planted faults')
    ap.add_argument('--verbose', '-v', action='store_true', help='also list passing checks')
    a = ap.parse_args()
    if not a.source and not a.pdf and not a.self_test:
        a.source, a.pdf, a.self_test = True, os.path.join(ROOT, 'dist'), True
    if a.self_test:
        self_test()
    if a.source:
        check_source()
    if a.pdf:
        check_pdfs(a.pdf)
    if a.verbose:
        for lvl, area, msg in RESULTS:
            if lvl == 'pass':
                print('pass    %-18s %s' % (area, msg))
    sys.exit(report(a.report))


if __name__ == '__main__':
    main()
