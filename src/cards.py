"""Card-sheet helpers shared by phases 2 and 3: 2 1/8 x 3 3/16 in cards, 9 per letter page, mirrored backs."""
from mp import *

CW, CH = 2.125 * IN, 3.1875 * IN
COLS, ROWS = 3, 3
GX = (W - COLS * CW) / 2
GY = (H - ROWS * CH) / 2

def slot(i, back=False):
    r, k = divmod(i, COLS)
    if back: k = COLS - 1 - k
    return GX + k * CW, H - GY - (r + 1) * CH

def frame(c, x, y):
    c.setStrokeColor(LGREY); c.setLineWidth(0.3); c.setFillColor(white); c.rect(x, y, CW, CH, fill=1, stroke=1)
    c.setStrokeColor(black); c.setLineWidth(1.0); c.rect(x + 6, y + 6, CW - 12, CH - 12, fill=0, stroke=1)

def sheet_marks(c):
    c.setStrokeColor(LGREY); c.setLineWidth(0.3)
    for k in range(COLS + 1):
        x = GX + k * CW; c.line(x, H - GY + 4, x, H - GY + 16); c.line(x, GY - 4, x, GY - 16)
    for r in range(ROWS + 1):
        y = H - GY - r * CH; c.line(GX - 4, y, GX - 16, y); c.line(W - GX + 4, y, W - GX + 16, y)

def band(c, x, y, color, label, sub=''):
    c.setFillColor(color); c.setStrokeColor(black); c.setLineWidth(0.8)
    c.rect(x + 6, y + CH - 6 - 20, CW - 12, 20, fill=1, stroke=1)
    head(c, label, x + CW / 2, y + CH - 6 - 14.5, 8.5, color=white, maxw=CW - 20)
    if sub:
        c.setFont(MONO, 5); c.setFillColor(white); c.drawRightString(x + CW - 10, y + CH - 6 - 18.5, sub)

def tag_strip(c, x, y, text, color):
    c.setFillColor(color); c.setStrokeColor(black); c.setLineWidth(0.6)
    c.rect(x + 6, y + 6, CW - 12, 13, fill=1, stroke=1)
    s = fit_size(text.upper(), 'HeadB', CW - 20, 6)
    head(c, text.upper(), x + CW / 2, y + 10, s, color=white)

def back(c, x, y, color, title, line2, pose='shrug', pattern='memo'):
    c.setStrokeColor(LGREY); c.setLineWidth(0.3); c.setFillColor(white); c.rect(x, y, CW, CH, fill=1, stroke=1)
    c.setFillColor(color); c.setStrokeColor(black); c.setLineWidth(1.2); c.rect(x + 6, y + 6, CW - 12, CH - 12, fill=1, stroke=1)
    # repeat pattern: faint small icons
    c.saveState(); p = c.beginPath(); p.rect(x + 8, y + 8, CW - 16, CH - 16); c.clipPath(p, stroke=0, fill=0)
    c.setFillColor(white); c.setStrokeColor(white)
    for r in range(7):
        for k in range(4):
            c.saveState(); c.translate(x + 20 + k * 38 + (r % 2) * 19, y + 18 + r * 34); c.setFillAlpha(0.18); c.setStrokeAlpha(0.18)
            if pattern == 'memo': c.rect(-5, -7, 10, 14, fill=1, stroke=0)
            elif pattern == 'bubble': c.ellipse(-7, -4, 7, 4, fill=1, stroke=0)
            elif pattern == 'star':
                pth = c.beginPath()
                for i in range(5):
                    a = math.pi / 2 + i * 4 * math.pi / 5; (pth.moveTo if i == 0 else pth.lineTo)(6 * math.cos(a), 6 * math.sin(a))
                pth.close(); c.drawPath(pth, fill=1, stroke=0)
            elif pattern == 'file': c.rect(-6, -6, 12, 9, fill=1, stroke=0); c.rect(-6, 3, 5, 3, fill=1, stroke=0)
            c.restoreState()
    c.restoreState()
    c.setFillColor(white); c.setStrokeColor(black); c.setLineWidth(1.0); c.rect(x + 16, y + CH / 2 - 26, CW - 32, 52, fill=1, stroke=1)
    head(c, title, x + CW / 2, y + CH / 2 + 6, 11, maxw=CW - 40)
    c.setFont(MONO, 5.6); c.setFillColor(GREY)
    for i, ln in enumerate(wrap(line2, MONO, 5.6, CW - 40)[:2]):
        c.drawCentredString(x + CW / 2, y + CH / 2 - 6 - i * 7, ln)
    pennyless(c, x + CW / 2, y + 16, 0.42, pose)
