from mp import *
from data import BOARD, ORIGINAL

SW, SH, CS = 1.625 * IN, 2.5625 * IN, 2.5625 * IN
OUT = out_path('Monoplatoon_Phase1_Board_Stickers.pdf')

def base(c, x, y, w, h):
    c.setFillColor(MINT); c.setStrokeColor(black); c.setLineWidth(1.4); c.rect(x, y, w, h, fill=1, stroke=1)

def name_lines(c, text, x, y, w, size=8.6, maxlines=3):
    """Headline name, wrapped, centred; returns y after the lines."""
    s = size
    while True:
        lines = wrap(text, 'HeadB', s, w - 10)
        if len(lines) <= maxlines and all(sw(l, 'HeadB', s) <= w - 10 for l in lines): break
        s -= 0.3
    for ln in lines:
        y -= s * 1.08
        head(c, ln, x + w / 2, y, s)
    return y

def sticker(c, x, y, sp):
    n, name, grp, price, flavor, ic, gloss = sp
    base(c, x, y, SW, SH)
    top = y + SH
    if grp in GROUP:
        c.setFillColor(GROUP[grp]); c.setStrokeColor(black); c.setLineWidth(1.0)
        c.rect(x, top - 0.48 * IN, SW, 0.48 * IN, fill=1, stroke=1)
        yy = name_lines(c, name, x, top - 0.48 * IN - 4, SW, 9.6)
        if ic: icon(c, ic, x + SW / 2, yy - 28, 1.5); yy -= 52
        yy = fit_block(c, x + 5, yy - 2, SW - 10, yy - (y + 18), flavor, MONO, 6.0, 1.18, FLAV, 'c')
        head(c, 'PRICE $%d' % price, x + SW / 2, y + 6, 8, font='HeadM')
    elif grp in ('rr', 'util'):
        yy = name_lines(c, name, x, top - 10, SW, 10.5)
        if ic: icon(c, ic, x + SW / 2, yy - 34, 1.7); yy -= 64
        yy = fit_block(c, x + 5, yy - 2, SW - 10, yy - (y + 18), flavor, MONO, 6.0, 1.18, FLAV, 'c')
        head(c, 'PRICE $%d' % price, x + SW / 2, y + 6, 8, font='HeadM')
    elif grp == 'tax':
        yy = name_lines(c, name, x, top - 10, SW, 10.5)
        if ic: icon(c, ic, x + SW / 2, yy - 34, 1.7); yy -= 64
        yy = fit_block(c, x + 5, yy - 2, SW - 10, yy - (y + 20), flavor, MONO, 6.0, 1.18, FLAV, 'c')
        head(c, price, x + SW / 2, y + 6, 7.2, font='HeadM', maxw=SW - 6)
    elif grp == 'deck':
        yy = name_lines(c, name, x, top - 12, SW, 11)
        # original art: a memo with a star (Guidance) or a rumor bubble (Lawyer)
        cx, cy = x + SW / 2, yy - 56
        c.setStrokeColor(black); c.setLineWidth(1.3); c.setFillColor(white)
        if name.startswith('COMMAND'):
            c.rect(cx - 20, cy - 26, 40, 52, fill=1, stroke=1)
            c.setFillColor(OLIVE); c.rect(cx - 20, cy + 16, 40, 10, fill=1, stroke=1)
            c.setFillColor(white); c.setFont('HeadB', 6); c.drawCentredString(cx, cy + 18.5, 'FROM: ABOVE')
            c.setStrokeColor(GREY); c.setLineWidth(0.6)
            for i in range(5): c.line(cx - 15, cy + 8 - i * 6, cx + 15, cy + 8 - i * 6)
            c.setFillColor(black); c.setFont('HeadB', 18); c.drawCentredString(cx, cy - 22, '?')
        else:
            c.ellipse(cx - 26, cy - 14, cx + 26, cy + 22, fill=1, stroke=1)
            p = c.beginPath(); p.moveTo(cx - 10, cy - 12); p.lineTo(cx - 16, cy - 26); p.lineTo(cx + 2, cy - 13); p.close(); c.drawPath(p, fill=1, stroke=1)
            c.setFillColor(black); c.setFont(MONOB, 6.5); c.drawCentredString(cx, cy + 6, 'I HEARD'); c.drawCentredString(cx, cy - 2, 'FROM A GUY')
        flav = {3: BOARD[2][4], 8: BOARD[7][4]}
        f = flav[3] if name.startswith('BARRACKS') else flav[8]
        fit_block(c, x + 5, cy - 40, SW - 10, 40, f, MONO, 6.0, 1.18, FLAV, 'c')

def corner(c, x, y, sp):
    n, name, grp, price, flavor, ic, gloss = sp
    base(c, x, y, CS, CS)
    cx = x + CS / 2
    if name == 'PAYDAY':
        c.saveState(); c.translate(x + CS / 2, y + CS / 2); c.rotate(45)
        head(c, 'PAYDAY', 0, 2, 28)
        c.setFont(MONOB, 6.2); c.setFillColor(black); c.drawCentredString(0, -10, 'COLLECT $200 AS YOU PASS.')
        c.drawCentredString(0, -18, 'PROBABLY.')
        c.restoreState()
        pennyless(c, x + 34, y + 8, 0.5, 'count')
        # arrow, like a payday that never quite arrives
        c.setStrokeColor(OLIVE); c.setLineWidth(3); c.line(x + CS - 24, y + 24, x + CS - 24, y + 70)
        p = c.beginPath(); p.moveTo(x + CS - 32, y + 34); p.lineTo(x + CS - 24, y + 18); p.lineTo(x + CS - 16, y + 34); p.close(); c.setFillColor(OLIVE); c.drawPath(p, fill=1, stroke=0)
        fit_block(c, x + 8, y + CS - 8, CS - 16, 30, flavor, MONO, 5.4, 1.15, FLAV, 'c')
    elif name == 'CQ DESK':
        # the desk box, with a "JUST VISITING" strip on two sides like the original jail
        c.setFillColor(HexColor('#E9E2C9')); c.setStrokeColor(black); c.setLineWidth(1.2)
        c.rect(x + 42, y + 42, CS - 42, CS - 42, fill=1, stroke=1)
        head(c, 'CQ DESK', x + 42 + (CS - 42) / 2, y + CS - 22, 15)
        pennyless(c, x + 42 + (CS - 42) / 2 + 2, y + 92, 0.55, 'asleep')
        icon(c, 'desk', x + 42 + (CS - 42) / 2, y + 100, 1.4)
        fit_block(c, x + 48, y + 86, CS - 54, 36, flavor, MONO, 5.2, 1.15, FLAV, 'c')
        c.setFont('HeadB', 8); c.setFillColor(black)
        c.saveState(); c.translate(x + 20, y + 42 + (CS - 42) / 2); c.rotate(90); c.drawCentredString(0, -3, 'JUST VISITING'); c.restoreState()
        c.drawCentredString(x + 42 + (CS - 42) / 2, y + 18, '(BROUGHT COFFEE)')
        pennyless(c, x + 20, y + 4, 0.38, 'stand')
    elif name == 'BLOCK LEAVE':
        head(c, 'BLOCK', cx, y + CS - 26, 20); head(c, 'LEAVE', cx, y + CS - 48, 20)
        pennyless(c, cx, y + 36, 0.78, 'hawaiian')
        # a sun
        c.setStrokeColor(OLIVE); c.setLineWidth(1); c.setFillColor(HexColor('#F7E08A')); c.circle(x + CS - 28, y + CS - 28, 12, fill=1, stroke=1)
        fit_block(c, x + 8, y + 32, CS - 16, 26, flavor, MONO, 5.2, 1.15, FLAV, 'c')
    elif name == 'STAFF DUTY':
        head(c, 'STAFF', cx, y + CS - 26, 20); head(c, 'DUTY', cx, y + CS - 48, 20)
        pennyless(c, cx - 18, y + 54, 0.7, 'point')
        c.setFont(MONOB, 6.2); c.setFillColor(black); c.drawCentredString(cx, y + 42, 'GO DIRECTLY TO THE CQ DESK')
        fit_block(c, x + 8, y + 36, CS - 16, 30, flavor, MONO, 5.4, 1.15, FLAV, 'c')

# ------------------------------------------------------------ deck labels, marks, bar, mascot piece
def deck_label(c, x, y, which):
    w, h = 3.45 * IN, 2.3 * IN
    base(c, x, y, w, h)
    c.setFillColor(OLIVE); c.setStrokeColor(black); c.rect(x + 8, y + h - 34, w - 16, 26, fill=1, stroke=1)
    head(c, which, x + w / 2, y + h - 26, 15, color=white)
    if which == 'COMMAND GUIDANCE':
        pennyless(c, x + 50, y + 12, 0.7, 'salute')
        c.setFillColor(white); c.setStrokeColor(black); c.setLineWidth(1.2); c.rect(x + 110, y + 30, 90, 64, fill=1, stroke=1)
        c.setFillColor(OLIVE); c.rect(x + 110, y + 82, 90, 12, fill=1, stroke=1)
        c.setFillColor(white); c.setFont('HeadB', 7); c.drawCentredString(x + 155, y + 85, 'MEMORANDUM FOR: ALL')
        c.setFont(MONO, 6); c.setFillColor(black)
        for i, ln in enumerate(['SUBJECT: New guidance', '1. Effective now.', '2. Supersedes para 1.', '3. See para 2.']):
            c.drawString(x + 115, y + 70 - i * 10, ln)
        text_block(c, x + 100, y + 22, w - 108, '"Somebody above you had an idea."', MONO, 6.5, color=FLAV, align='c')
    else:
        pennyless(c, x + 60, y + 12, 0.7, 'shrug')
        c.setFillColor(white); c.setStrokeColor(black); c.setLineWidth(1.2)
        c.ellipse(x + 110, y + 40, x + 215, y + 96, fill=1, stroke=1)
        p = c.beginPath(); p.moveTo(x + 125, y + 46); p.lineTo(x + 100, y + 30); p.lineTo(x + 140, y + 42); p.close(); c.drawPath(p, fill=1, stroke=1)
        c.setFont(MONOB, 7); c.setFillColor(black); c.drawCentredString(x + 162, y + 74, 'MY BUDDY SAID'); c.drawCentredString(x + 162, y + 64, "WE'RE GETTING"); c.drawCentredString(x + 162, y + 54, 'A FOUR-DAY')
        text_block(c, x + 100, y + 22, w - 108, '"Somebody beside you heard a rumor."', MONO, 6.5, color=FLAV, align='c')

def makers_mark(c, x, y, rounded=True):
    w, h = 1.7 * IN, 1.0 * IN
    c.setFillColor(black); c.setStrokeColor(black)
    if rounded: c.roundRect(x, y, w, h, 10, fill=1, stroke=1)
    else: c.ellipse(x, y, x + w, y + h, fill=1, stroke=1)
    head(c, 'MADE BY THE', x + w / 2, y + h - 24, 11, color=white)
    head(c, 'LOWEST BIDDER', x + w / 2, y + h - 40, 13, color=white, maxw=w - 10)
    c.setFont(MONO, 5.5); c.setFillColor(white); c.drawCentredString(x + w / 2, y + 14, 'CONTRACT NO. PENDING')
    c.drawCentredString(x + w / 2, y + 6, 'DELIVERY: NEXT FY')

BAR_L, BAR_T, BELOW, ABOVE = 11.6 * IN, 2.5 * IN, 0.65 * IN, 0.5 * IN
MASC_W, MASC_H = 4.15 * IN, 2.4 * IN

def title_size():
    s = 96
    while sw('MONOPLATOON', 'HeadB', s) > BAR_L * 0.80: s -= 0.5
    return s

def bar_art(c):
    """Full bar with lower-left of the keyline box at (0,0)."""
    c.setFillColor(MINT); c.setStrokeColor(LGREY); c.setLineWidth(0.4); c.rect(0, -BELOW, BAR_L, BAR_T + BELOW + ABOVE, fill=1, stroke=1)
    c.setFillColor(white); c.setStrokeColor(black); c.setLineWidth(1.4); c.rect(0, 0, BAR_L, BAR_T, fill=1, stroke=1)
    ins = 0.10 * IN; c.setFillColor(OLIVE); c.rect(ins, ins, BAR_L - 2 * ins, BAR_T - 2 * ins, fill=1, stroke=0)
    s = title_size(); ty = BAR_T / 2 - s * 0.36
    c.setFont('HeadB', s); c.setFillColor(black); c.drawCentredString(BAR_L / 2 + 3, ty - 3, 'MONOPLATOON')
    c.setFillColor(white); c.drawCentredString(BAR_L / 2, ty, 'MONOPLATOON')
    # chevrons at the ends (an E-4's three stripes in gold)
    for ex in (BAR_L * 0.06, BAR_L * 0.94):
        c.setStrokeColor(HexColor('#D9B44A')); c.setLineWidth(3.5)
        for i in range(3):
            yy = BAR_T / 2 + 18 - i * 11
            c.line(ex - 16, yy + 8, ex, yy); c.line(ex, yy, ex + 16, yy + 8)
    sx = split_x()
    c.setFillColor(black); c.setFont(MONOB, 17); c.drawCentredString(sx / 2, -BELOW + 14, 'HURRY UP AND WAIT.')
    c.setFont(MONOB, 9); c.setFillColor(GREY); c.drawCentredString(sx + (BAR_L - sx) / 2, -BELOW + 18, 'LEGALLY STILL MONOPOLY.')

def split_x():
    s = title_size(); x = BAR_L / 2 - sw('MONOPLATOON', 'HeadB', s) / 2; gaps = []
    for ch in 'MONOPLATOON':
        x += sw(ch, 'HeadB', s); gaps.append(x)
    return min(gaps, key=lambda g: abs(g - BAR_L / 2))

def bar_piece(c, x, y, which):
    """Draw piece A (left of the split) or B (right) with its lower-left at (x, y) (y = bottom of green backing)."""
    sx = split_x(); x0, x1 = (0, sx) if which == 'A' else (sx, BAR_L)
    c.saveState(); p = c.beginPath(); p.rect(x + x0 - (0 if which == 'A' else x0), y, x1 - x0, BAR_T + BELOW + ABOVE); c.clipPath(p, stroke=0, fill=0)
    c.translate(x - x0, y + BELOW); bar_art(c); c.restoreState()
    return x1 - x0

def mascot_piece(c, x, y):
    c.setFillColor(MINT); c.setStrokeColor(LGREY); c.setLineWidth(0.4); c.rect(x, y, MASC_W, MASC_H, fill=1, stroke=1)
    pennyless(c, x + MASC_W / 2, y + 2, 1.55, 'shrug')
    c.setFont(MONO, 6); c.setFillColor(GREY); c.drawString(x + 6, y + 6, 'SPC PENNYLESS'); c.drawRightString(x + MASC_W - 6, y + 6, 'E-4, 3 YRS TIS')

# ------------------------------------------------------------ pages
STD = [sp for sp in BOARD if sp[2] != 'corner']
CORNERS = [sp for sp in BOARD if sp[2] == 'corner']

def page_std(c, items, label):
    heading(c, 'Board stickers, true size: ' + label, 'Property, Rotation, utility, tax and card spaces at 1 5/8 x 2 9/16 in. Cut on the black line. Side-of-board spaces: rotate so the colour band faces the centre.')
    gx, gy = 0.42 * IN, H - 1.15 * IN
    gapx, gapy = (W - 2 * gx - 4 * SW) / 3, 14
    for i, sp in enumerate(items):
        r, k = divmod(i, 4)
        x = gx + k * (SW + gapx); y = gy - (r + 1) * SH - r * gapy
        sticker(c, x, y, sp); cutmarks(c, x, y, SW, SH)
    footer(c, 'Phase 1: board stickers, ' + label)

def page3(c):
    heading(c, 'Deck labels, mascot piece, maker\'s mark, true size',
            'Deck labels 3.45 x 2.3 in cover the two card outlines in the centre. The mascot piece goes on last, above the title bar (page 6). The black badge covers the maker\'s oval under the bar; two shapes, use the one that cuts easier.')
    gx, top = 0.42 * IN, H - 1.15 * IN
    dx = gx
    deck_label(c, dx, top - 2.3 * IN, 'COMMAND GUIDANCE'); cutmarks(c, dx, top - 2.3 * IN, 3.45 * IN, 2.3 * IN)
    deck_label(c, dx, top - 4.6 * IN - 10, 'BARRACKS LAWYER'); cutmarks(c, dx, top - 4.6 * IN - 10, 3.45 * IN, 2.3 * IN)
    my = top - 4.6 * IN - 10 - 24 - MASC_H
    mascot_piece(c, gx, my); cutmarks(c, gx, my, MASC_W, MASC_H)
    c.setFont(MONO, 6.5); c.setFillColor(GREY); c.drawString(gx, my - 10, 'Mascot piece, 4.15 x 2.4 in. Bottom edge sits on the bar\'s top black line, centred.')
    makers_mark(c, gx + MASC_W + 24, my + MASC_H - 1.0 * IN, True)
    makers_mark(c, gx + MASC_W + 24, my + 2, False)
    pennyless(c, dx + 3.45 * IN + 60, top - 1.6 * IN, 1.0, 'salute'); pennyless(c, dx + 3.45 * IN + 60, top - 4.0 * IN, 1.0, 'hammer')
    c.setFont(MONO, 6); c.setFillColor(GREY); c.drawCentredString(dx + 3.45 * IN + 60, top - 4.15 * IN, 'spare mascot poses')
    footer(c, 'Phase 1: deck labels, mascot piece, maker\'s mark')

def page_corners(c):
    heading(c, 'Corner stickers, true size', 'Four corners at 2 9/16 in square. Right: the placement key, old name to new.')
    gx, top = 0.42 * IN, H - 1.15 * IN
    for i, sp in enumerate(CORNERS):
        r, k = divmod(i, 2)
        x = gx + k * (CS + 8); y = top - (r + 1) * CS - r * 8
        corner(c, x, y, sp); cutmarks(c, x, y, CS, CS)
    kx = gx + 2 * CS + 30; ky = top - 4
    head(c, 'PLACEMENT KEY', kx, ky, 9, anchor='l'); ky -= 12
    c.setFont(MONO, 5.6)
    for sp in BOARD:
        c.setFillColor(GREY); c.drawString(kx, ky, '%2d %s' % (sp[0], ORIGINAL[sp[0]]))
        c.setFillColor(black); c.drawString(kx + 92, ky, sp[1][:30])
        ky -= 7.6
    footer(c, 'Phase 1: corners')

def page_bar(c):
    heading(c, 'Centre title bar, true size, two pieces', 'The bar is 11.6 x 2.5 in with 0.5 in of green above and 0.65 in below, longer than a page, so it is two stickers that butt together between two letters. Apply A then B, then the mascot piece (page 3) above.')
    tot = BAR_T + BELOW + ABOVE
    y1 = H - 1.1 * IN - tot
    wa = bar_piece(c, 0.3 * IN, y1, 'A'); cutmarks(c, 0.3 * IN, y1, wa, tot)
    c.setFont(MONOB, 8); c.setFillColor(black); c.drawString(0.3 * IN, y1 - 11, 'PIECE A (left). Cut the right edge exactly on the letter gap.')
    y2 = y1 - 0.5 * IN - tot
    wb = bar_piece(c, 0.3 * IN, y2, 'B'); cutmarks(c, 0.3 * IN, y2, wb, tot)
    c.drawString(0.3 * IN, y2 - 11, 'PIECE B (right). Butt its left edge against piece A.')
    footer(c, 'Phase 1: centre title bar')

if __name__ == '__main__':
    c = canvas.Canvas(OUT, pagesize=letter); c.setTitle('MONOPLATOON - Phase 1: board stickers')
    page_std(c, STD[:12], 'sheet 1'); c.showPage()
    page_std(c, STD[12:24], 'sheet 2'); c.showPage()
    page_std(c, STD[24:36], 'sheet 3'); c.showPage()
    page3(c); c.showPage()
    page_corners(c); c.showPage()
    page_bar(c); c.showPage()
    c.save(); print('ok', len(STD), 'standard stickers')
