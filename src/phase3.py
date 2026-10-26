from mp import *
from cards import *
from data import BOARD, CHARACTERS, FIRST_SERGEANT, READINESS, RENT, RENT_BALTIC, GROUP_NAME

OUT = out_path('Monoplatoon_Phase3_Characters_and_Deeds.pdf')
NAVY = HexColor('#1F2A44')

def rank_of(name):
    return name.split()[0]

def character_front(c, x, y, card, n):
    name, rule, flavor, gloss, pose = card
    frame(c, x, y); band(c, x, y, NAVY, 'PERSONNEL FILE', '%d/12' % n)
    # portrait box
    c.setFillColor(HexColor('#EEF1F5')); c.setStrokeColor(black); c.setLineWidth(0.8); c.rect(x + 12, y + CH - 32 - 70, CW - 24, 70, fill=1, stroke=1)
    pennyless(c, x + CW / 2, y + CH - 32 - 67, 0.56, pose)
    c.setFont(MONO, 4.5); c.setFillColor(GREY); c.drawString(x + 15, y + CH - 32 - 67, 'DA PHOTO'); c.drawRightString(x + CW - 15, y + CH - 32 - 67, 'NOT TO SCALE')
    yy = y + CH - 108
    s = 10
    while len(wrap(name, 'HeadB', s, CW - 22)) > 2 and s > 7: s -= 0.5
    for ln in wrap(name, 'HeadB', s, CW - 22):
        yy -= s * 1.1; head(c, ln, x + CW / 2, yy, s)
    rs, fs = 7.4, 6.4
    while True:
        h = len(wrap(rule, MONOB, rs, CW - 24)) * rs * 1.2 + 6 + len(wrap(flavor, MONO, fs, CW - 24)) * fs * 1.2 + 6 + len(wrap(gloss, MONO, fs - 0.6, CW - 24)) * (fs - 0.6) * 1.15
        if h <= yy - (y + 12) or rs <= 5: break
        rs -= 0.2; fs -= 0.2
    yy = text_block(c, x + 12, yy - 3, CW - 24, rule, MONOB, rs, 1.2, black)
    yy = text_block(c, x + 12, yy - 5, CW - 24, flavor, MONO, fs, 1.2, FLAV)
    c.setStrokeColor(LGREY); c.setLineWidth(0.4); c.line(x + 12, yy - 3, x + CW - 12, yy - 3)
    text_block(c, x + 12, yy - 5, CW - 24, gloss, MONO, fs - 0.6, 1.15, FLAV)

def first_sergeant_front(c, x, y):
    name, rule, flavor, gloss, pose = FIRST_SERGEANT
    frame(c, x, y); band(c, x, y, black, 'ROLE CARD', 'TOP')
    bt = y + CH - 32; bh = 46
    c.setFillColor(HexColor('#EEF1F5')); c.setStrokeColor(black); c.setLineWidth(0.8); c.rect(x + 12, bt - bh, CW - 24, bh, fill=1, stroke=1)
    pennyless(c, x + CW / 2 - 24, bt - bh + 2, 0.42, 'stand')
    c.setFillColor(white); c.setStrokeColor(black); c.rect(x + CW / 2 + 6, bt - bh + 6, 14, 15, fill=1, stroke=1); c.setFont('HeadB', 4.5); c.setFillColor(black); c.drawCentredString(x + CW / 2 + 13, bt - bh + 11, 'TOP')
    icon(c, 'stack', x + CW / 2 + 36, bt - bh + 14, 0.8)
    yy = bt - bh - 12
    head(c, 'FIRST SERGEANT', x + CW / 2, yy, 10.5); head(c, '("Top")', x + CW / 2, yy - 10, 7.5, font='HeadM'); yy -= 13
    rs, fs = 6.2, 5.6
    while True:
        h = len(wrap(rule, MONOB, rs, CW - 24)) * rs * 1.18 + 5 + len(wrap(flavor, MONO, fs, CW - 24)) * fs * 1.18 + 5 + len(wrap(gloss, MONO, fs - 0.5, CW - 24)) * (fs - 0.5) * 1.12
        if h <= yy - (y + 12) or rs <= 4.6: break
        rs -= 0.15; fs -= 0.15
    yy = text_block(c, x + 12, yy - 3, CW - 24, rule, MONOB, rs, 1.18, black)
    yy = text_block(c, x + 12, yy - 4, CW - 24, flavor, MONO, fs, 1.18, FLAV)
    c.setStrokeColor(LGREY); c.setLineWidth(0.4); c.line(x + 12, yy - 2, x + CW - 12, yy - 2)
    text_block(c, x + 12, yy - 4, CW - 24, gloss, MONO, fs - 0.5, 1.12, FLAV)

def readiness_front(c, x, y, text, n):
    frame(c, x, y); band(c, x, y, black, 'READINESS', 'SECRET %d/6' % n)
    c.setFont(MONO, 5); c.setFillColor(GREY); c.drawCentredString(x + CW / 2, y + CH - 36, 'FOR THE FIRST SERGEANT ONLY. DO NOT SHOW.')
    c.setStrokeColor(RED); c.setLineWidth(1); c.rect(x + 16, y + CH - 60, CW - 32, 16, fill=0, stroke=1)
    head(c, 'CLASSIFIED: ANNOYING', x + CW / 2, y + CH - 55, 7, color=RED)
    head(c, 'YOU WIN AT ETS IF', x + CW / 2, y + CH - 86, 9)
    fit_block(c, x + 14, y + CH - 92, CW - 28, 60, text, MONOB, 8.4, 1.25, black, 'c')
    pennyless(c, x + CW / 2, y + 16, 0.55, 'point')
    c.setFont(MONO, 5); c.setFillColor(GREY); c.drawCentredString(x + CW / 2, y + 10, 'Readiness is a number. This is the number.')

def deed(c, x, y, sp):
    n, name, grp, price, flavor, ic, gloss = sp
    c.setStrokeColor(LGREY); c.setLineWidth(0.3); c.setFillColor(white); c.rect(x, y, CW, CH, fill=1, stroke=1)
    c.setStrokeColor(black); c.setLineWidth(1.0); c.rect(x + 6, y + 6, CW - 12, CH - 12, fill=0, stroke=1)
    if grp in GROUP:
        c.setFillColor(GROUP[grp]); c.rect(x + 6, y + CH - 6 - 40, CW - 12, 40, fill=1, stroke=1)
        tc = black if grp in ('lblue', 'yellow') else white
        c.setFont(MONO, 5); c.setFillColor(tc); c.drawCentredString(x + CW / 2, y + CH - 16, 'TITLE DEED  -  ' + GROUP_NAME[grp])
        s = 9
        while len(wrap(name, 'HeadB', s, CW - 20)) > 2 and s > 6: s -= 0.5
        lines = wrap(name, 'HeadB', s, CW - 20)
        for i, ln in enumerate(lines): head(c, ln, x + CW / 2, y + CH - 28 - i * (s + 1) - (0 if len(lines) == 2 else 4), s, color=tc)
        rents, house, mort = (RENT_BALTIC if n == 4 else RENT[price])
        yy = y + CH - 56
        head(c, 'PRICE $%d' % price, x + CW / 2, yy, 8.5); yy -= 12
        rows = [('RENT', '$%d' % rents[0]), ('With 1 Barracks Repair', '$%d' % rents[1]), ('With 2 Barracks Repairs', '$%d' % rents[2]),
                ('With 3 Barracks Repairs', '$%d' % rents[3]), ('With 4 Barracks Repairs', '$%d' % rents[4]), ('With PRIVATIZED HOUSING', '$%d' % rents[5])]
        c.setFont(MONO, 6)
        for lab, val in rows:
            c.setFillColor(black); c.setFont(MONOB if lab == 'RENT' else MONO, 6); c.drawString(x + 14, yy, lab); c.drawRightString(x + CW - 14, yy, val); yy -= 8.4
        c.setStrokeColor(LGREY); c.setLineWidth(0.4); c.line(x + 14, yy + 2, x + CW - 14, yy + 2); yy -= 2
        for lab, val in (('Mortgage value', '$%d' % mort), ('Barracks Repair, each', '$%d' % house), ('Privatized Housing', '$%d + 4 repairs' % house)):
            c.setFont(MONO, 5.6); c.setFillColor(black); c.drawString(x + 14, yy, lab); c.drawRightString(x + CW - 14, yy, val); yy -= 7.6
        text_block(c, x + 14, yy - 2, CW - 28, 'Rent doubles on an unimproved space if you own the whole group.', MONO, 4.8, 1.15, GREY)
    elif grp == 'rr':
        c.setFillColor(black); c.rect(x + 6, y + CH - 6 - 40, CW - 12, 40, fill=1, stroke=1)
        c.setFont(MONO, 5); c.setFillColor(white); c.drawCentredString(x + CW / 2, y + CH - 16, 'TITLE DEED  -  ROTATION')
        head(c, name, x + CW / 2, y + CH - 34, 11, color=white, maxw=CW - 20)
        icon(c, ic, x + CW / 2, y + CH - 72, 1.4)
        yy = y + CH - 96
        head(c, 'PRICE $200', x + CW / 2, yy, 8.5); yy -= 12
        for lab, val in (('RENT', '$25'), ('If 2 Rotations are owned', '$50'), ('If 3 Rotations are owned', '$100'), ('If 4 Rotations are owned', '$200'), ('Mortgage value', '$100')):
            c.setFont(MONOB if lab == 'RENT' else MONO, 6); c.setFillColor(black); c.drawString(x + 14, yy, lab); c.drawRightString(x + CW - 14, yy, val); yy -= 8.6
    elif grp == 'util':
        c.setFillColor(HexColor('#777777')); c.rect(x + 6, y + CH - 6 - 40, CW - 12, 40, fill=1, stroke=1)
        c.setFont(MONO, 5); c.setFillColor(white); c.drawCentredString(x + CW / 2, y + CH - 16, 'TITLE DEED  -  UTILITY')
        s = 9
        for i, ln in enumerate(wrap(name, 'HeadB', s, CW - 20)): head(c, ln, x + CW / 2, y + CH - 30 - i * 10, s, color=white)
        icon(c, ic, x + CW / 2, y + CH - 72, 1.4)
        yy = y + CH - 96
        head(c, 'PRICE $150', x + CW / 2, yy, 8.5); yy -= 12
        yy = text_block(c, x + 14, yy, CW - 28, 'If one utility is owned, rent is 4 times the amount shown on the dice.', MONO, 5.8, 1.2, black)
        yy = text_block(c, x + 14, yy - 3, CW - 28, 'If both are owned, rent is 10 times the amount shown on the dice.', MONO, 5.8, 1.2, black)
        c.setFont(MONO, 6); c.drawString(x + 14, yy - 8, 'Mortgage value'); c.drawRightString(x + CW - 14, yy - 8, '$75'); yy -= 10
    # flavor + gloss at the foot
    fl = flavor if len(flavor) < 110 else flavor[:flavor.rfind('.', 0, 110) + 1]
    gl = gloss
    fy = y + 10 + (len(wrap(gl, MONO, 4.8, CW - 28)) * 5.5 if gl else 0) + len(wrap(fl, MONO, 5.2, CW - 28)) * 6 + 2
    yy = text_block(c, x + 14, fy, CW - 28, fl, MONO, 5.2, 1.15, FLAV)
    if gl: text_block(c, x + 14, yy - 2, CW - 28, gl, MONO, 4.8, 1.15, FLAV)

def sheets(c, items, draw, label, stock, back_fn=None):
    pages = [items[i:i + 9] for i in range(0, len(items), 9)]
    for pi, pg in enumerate(pages):
        heading(c, label + ', sheet %d of %d' % (pi + 1, len(pages)), stock)
        sheet_marks(c)
        for i, it in enumerate(pg):
            x, y = slot(i); draw(c, x, y, it, pi * 9 + i)
        footer(c, 'Phase 3: ' + label + ' ' + str(pi + 1)); c.showPage()
        if back_fn:
            heading(c, label + ', backs, sheet %d of %d (mirrored for a long-edge flip)' % (pi + 1, len(pages)))
            sheet_marks(c)
            for i in range(len(pg)):
                x, y = slot(i, back=True); back_fn(c, x, y)
            footer(c, 'Phase 3: ' + label + ' backs ' + str(pi + 1)); c.showPage()

def draw_person(c, x, y, it, i):
    if it == '1SG': first_sergeant_front(c, x, y)
    elif isinstance(it, str): readiness_front(c, x, y, it, READINESS.index(it) + 1)
    else: character_front(c, x, y, it, CHARACTERS.index(it) + 1)

def person_back(c, x, y):
    back(c, x, y, NAVY, 'PERSONNEL FILE', 'Do not remove. Someone will.', 'shrug', 'file')

if __name__ == '__main__':
    c = canvas.Canvas(OUT, pagesize=letter); c.setTitle('MONOPLATOON - Phase 3: characters and deeds')
    people = CHARACTERS + ['1SG'] + READINESS
    sheets(c, people, draw_person, 'Characters, role card, Readiness', 'White 65 lb cardstock, 2 1/8 x 3 3/16 in. All share one back so the draw pile gives nothing away.', person_back)
    deeds = [sp for sp in BOARD if sp[2] in GROUP or sp[2] in ('rr', 'util')]
    sheets(c, deeds, lambda c, x, y, it, i: deed(c, x, y, it), 'Title deeds', 'White 65 lb cardstock, single-sided, 2 1/8 x 3 3/16 in. Purchase price on every deed for net worth at ETS.')
    c.save(); print('ok', len(people), len(deeds))
