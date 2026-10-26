from mp import *
from cards import *
from data import GUIDANCE, LAWYER, BUILDING

OUT = out_path('Monoplatoon_Phase2_Decks.pdf')
BROWN = HexColor('#7A5C2E'); SLATE = HexColor('#3A3F44')
TYPE_COL = {'DIRECTIVE': OLIVE, 'WALK-BACK': RED, 'PAPERWORK': SLATE, 'UNIFORM': HexColor('#2F6B3A'), 'POLICY LETTER': SLATE}

MONO_INK = [False]

def tag_color(tag):
    if tag.startswith('SMOKE'): return RED
    if tag.startswith('GUIDANCE'): return OLIVE
    if tag.startswith('UNIFORM'): return HexColor('#2F6B3A')
    if tag.startswith('PAPERWORK'): return SLATE
    return None

def body(c, x, y, title, rule, flavor, ic, gloss_or_tag, top, narrow=0):
    yy = top
    s = 11
    while len(wrap(title, 'HeadB', s, CW - 22)) > 2 and s > 7: s -= 0.5
    for ln in wrap(title, 'HeadB', s, CW - 22):
        yy -= s * 1.1; head(c, ln, x + CW / 2, yy, s)
    if ic: icon(c, ic, x + CW / 2, yy - 28, 1.6); yy -= 54
    tag = gloss_or_tag if tag_color(gloss_or_tag or '') else ''
    gloss = gloss_or_tag if not tag and gloss_or_tag else ''
    bottom = y + (24 if tag else 10)
    avail = yy - bottom
    # rule in black, flavor grey, gloss smaller grey; shrink together to fit
    rs, fs = 8.2, 7.0
    while True:
        h = len(wrap(rule, MONOB, rs, CW - 24)) * rs * 1.2 + 6 + len(wrap(flavor, MONO, fs, CW - 24 - narrow)) * fs * 1.2
        if gloss: h += 5 + len(wrap(gloss, MONO, fs - 0.6, CW - 24)) * (fs - 0.6) * 1.15
        if h <= avail or rs <= 5.2: break
        rs -= 0.2; fs -= 0.2
    yy = text_block(c, x + 12, yy - 2, CW - 24, rule, MONOB, rs, 1.2, black)
    yy = text_block(c, x + 12, yy - 6, CW - 24 - narrow, flavor, MONO, fs, 1.2, FLAV)
    if gloss:
        c.setStrokeColor(LGREY); c.setLineWidth(0.4); c.line(x + 12, yy - 3, x + CW - 12, yy - 3)
        yy = text_block(c, x + 12, yy - 5, CW - 24, gloss, MONO, fs - 0.6, 1.15, FLAV)
    if tag: tag_strip(c, x, y, tag, black if MONO_INK[0] else tag_color(tag))
    # Pennyless acts out the card if there's room
    room = yy - bottom
    if room > 44:
        sc = min(0.58, (room - 4) / 100.0)
        pennyless(c, x + CW / 2, bottom + 4, sc, POSE.get(title, 'shrug'))

POSE = {
    "Report to the Secretary's Office": 'salute', 'Payday': 'count', 'Battalion Conference Room, now': 'asleep', 'Weekend Pass': 'hawaiian',
    'Rotation': 'stand', 'Rotation, again': 'shrug', 'Account Overdrawn': 'count', 'Deployment Entitlement': 'salute', 'Sick Call Slip': 'stand',
    'Detail': 'point', 'Staff Duty': 'asleep', 'Barracks Inspection': 'stand', 'Reflective Belt Violation': 'pin', 'NTC Rotation': 'salute',
    'Hail and Farewell': 'hawaiian', 'Back Pay': 'count', 'Continuing Resolution Ends': 'count', 'DFAS Error in Your Favor': 'count',
    'Chow Hall Closed for Renovation': 'shrug', 'Sold Your TA-50 to Freedom Pawn': 'shrug', 'FRG Bake Sale': 'stand', 'The Printer Has Toner': 'point',
    'The General Gave You a Coin': 'salute', 'Bonus Installment': 'count', 'The Hammer': 'hammer', 'Mandatory Online Training': 'asleep',
    'You Briefed the General': 'point', 'Privatized Housing Assessment': 'shrug', 'Soldier of the Month': 'salute', 'Weapons Program Cancelled': 'shrug',
    'Department of War': 'shrug', 'Testosterone For Everyone': 'stand', 'Warrior Ethos Memo': 'stand', 'Mandatory Mustache': 'stand',
    'Rename the Base Again': 'point', 'Continuing Resolution': 'count', 'Sleeves Up': 'pin', 'Taken Out of Context': 'shrug', 'It Was Never Policy': 'shrug',
    'The Old Uniform Was Better': 'pin', 'The 2 a.m. Post': 'asleep', 'Memorandum for Record': 'salute', 'Form 4856-ish': 'stand', 'New Fitness Test': 'stand',
    'Safety Brief': 'asleep', 'New Service Uniform': 'pin', 'Reflective Belt Mandatory': 'pin', 'Pink Beret Era': 'shrug',
}

def guidance_front(c, x, y, card, n):
    title, rule, flavor, tag, ic = card
    frame(c, x, y); band(c, x, y, black, 'COMMAND GUIDANCE', '%d/16' % n)
    body(c, x, y, title, rule, flavor, ic, tag, y + CH - 30)

def lawyer_front(c, x, y, card, n):
    title, rule, flavor, tag, ic = card
    frame(c, x, y); band(c, x, y, black, 'BARRACKS LAWYER', '%d/16' % n)
    body(c, x, y, title, rule, flavor, ic, tag, y + CH - 30)

def issuer(c, x, y, who):
    c.setFont(MONO, 4.2); c.setFillColor(GREY)
    if who == 'watch': secretary(c, x + CW - 36, y + 34, 0.30); c.drawRightString(x + CW - 12, y + 30, 'SECWAR')
    elif who == 'phone': phone_hand(c, x + CW - 26, y + 32, 0.40); c.drawRightString(x + CW - 12, y + 30, 'CINC, 0200')

def building_front(c, x, y, card, n):
    typ, title, who, rule, flavor, ic = card
    frame(c, x, y); band(c, x, y, TYPE_COL[typ], typ, '%d/18' % n)
    c.setFont(MONO, 5); c.setFillColor(GREY); c.drawString(x + 10, y + CH - 34, 'THE BUILDING')
    issuer(c, x, y, who)
    body(c, x + 0, y + 20, title, rule, flavor, ic, '', y + CH - 40, narrow=30)
    # red stamp
    c.saveState(); c.translate(x + CW / 2, y + 18); c.rotate(-6); c.setStrokeColor(RED); c.setLineWidth(0.8); c.setFillColor(RED)
    c.setStrokeAlpha(0.7); c.setFillAlpha(0.7); c.rect(-46, -5, 92, 11, fill=0, stroke=1); c.setFont('HeadB', 6.5); c.drawCentredString(0, -2, 'EFFECTIVE IMMEDIATELY'); c.restoreState()

def policy_letter_front(c, x, y, n):
    frame(c, x, y); band(c, x, y, SLATE, 'POLICY LETTER', 'blank %d' % n)
    c.setFont(MONO, 5); c.setFillColor(GREY); c.drawString(x + 10, y + CH - 34, 'LOCAL POLICY, 1SG')
    c.setFont(MONOB, 6.5); c.setFillColor(black); c.drawString(x + 12, y + CH - 48, 'MEMORANDUM FOR: Everyone')
    c.setFont(MONO, 6.5); c.drawString(x + 12, y + CH - 60, 'SUBJECT: ____________________')
    c.setStrokeColor(LGREY); c.setLineWidth(0.5)
    for i in range(9): c.line(x + 12, y + CH - 78 - i * 13, x + CW - 12, y + CH - 78 - i * 13)
    c.setFont(MONO, 5.5); c.setFillColor(GREY); c.drawString(x + 12, y + 34, 'POC: the undersigned, who is leaving.')
    c.drawString(x + 12, y + 24, 'Signed: ________________  1SG')
    c.setFont(MONO, 4.8); c.drawCentredString(x + CW / 2, y + 12, 'Archives first. Walk-Backs hit this first. Enjoy.')

def fronts(c, cards, draw, label, backs=True, stock=''):
    pages = [cards[i:i + 9] for i in range(0, len(cards), 9)]
    for pi, pg in enumerate(pages):
        heading(c, label + ', sheet %d of %d' % (pi + 1, len(pages)), stock or 'Cards 2 1/8 x 3 3/16 in. Print this sheet, flip on the long edge, print the next sheet for the backs.')
        sheet_marks(c)
        for i, card in enumerate(pg):
            x, y = slot(i); draw(c, x, y, card, pi * 9 + i + 1)
        footer(c, 'Phase 2: ' + label + ' ' + str(pi + 1)); c.showPage()
        if not backs: continue
        heading(c, label + ', backs, sheet %d of %d (mirrored for a long-edge flip)' % (pi + 1, len(pages)))
        sheet_marks(c)
        for i in range(len(pg)):
            x, y = slot(i, back=True); BACKS[label](c, x, y)
        footer(c, 'Phase 2: ' + label + ' backs ' + str(pi + 1)); c.showPage()

BACKS = {
    'Command Guidance': lambda c, x, y: back(c, x, y, OLIVE, 'COMMAND GUIDANCE', 'Read. Acknowledge. Comply.', 'salute', 'memo'),
    'Barracks Lawyer': lambda c, x, y: back(c, x, y, BROWN, 'BARRACKS LAWYER', 'I heard from a guy.', 'shrug', 'bubble'),
    'The Building': lambda c, x, y: back(c, x, y, SLATE, 'THE BUILDING', 'Effective immediately, until further notice.', 'stand', 'star'),
}

def building_draw(c, x, y, card, n):
    if card == 'BLANK': policy_letter_front(c, x, y, n - 18)
    else: building_front(c, x, y, card, n)

if __name__ == '__main__':
    c = canvas.Canvas(OUT, pagesize=letter); c.setTitle('MONOPLATOON - Phase 2: decks')
    MONO_INK[0] = True; INK[0] = True
    fronts(c, GUIDANCE, guidance_front, 'Command Guidance', backs=False, stock='Single-sided, black ink, on pale green 65 lb cardstock. Cards 2 1/8 x 3 3/16 in; the stock colour is the back.')
    fronts(c, LAWYER, lawyer_front, 'Barracks Lawyer', backs=False, stock='Single-sided, black ink, on buff 65 lb cardstock. Cards 2 1/8 x 3 3/16 in; the stock colour is the back.')
    MONO_INK[0] = False; INK[0] = False
    fronts(c, BUILDING, building_draw, 'The Building')
    c.save(); print('ok')
