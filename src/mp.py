"""MONOPLATOON shared helpers: fonts, colours, text fitting, mascot and spot art."""
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.colors import Color, black, white, HexColor
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
import math, os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DIR = os.environ.get('MONOPLATOON_OUT', os.path.join(ROOT, 'dist'))
os.makedirs(OUT_DIR, exist_ok=True)
try:
    VERSION = open(os.path.join(ROOT, 'VERSION')).read().strip()
except OSError:
    VERSION = 'dev'

def out_path(name):
    return os.path.join(OUT_DIR, name)

IN = 72.0
W, H = letter

# ---------------------------------------------------------------- fonts
FONT_DIR = os.path.join(ROOT, 'fonts')
pdfmetrics.registerFont(TTFont('HeadB', os.path.join(FONT_DIR, 'DejaVuSansCondensed-Bold.ttf')))
pdfmetrics.registerFont(TTFont('HeadM', os.path.join(FONT_DIR, 'DejaVuSansCondensed.ttf')))
MONO, MONOB = 'Courier', 'Courier-Bold'

# ---------------------------------------------------------------- colours
MINT = HexColor('#BFDDC8')          # chip G, matched to the real board
OLIVE = HexColor('#4B5320')
GREY = HexColor('#555555')
LGREY = HexColor('#9A9A9A')
RED = HexColor('#B3261E')
FLAV = GREY
GROUP = {
    'brown': HexColor('#955436'), 'lblue': HexColor('#AAE0FA'), 'pink': HexColor('#D93A96'),
    'orange': HexColor('#F7941D'), 'red': HexColor('#ED1B24'), 'yellow': HexColor('#FEF200'),
    'green': HexColor('#1FB25A'), 'dblue': HexColor('#0072BB'),
}
PAGE_CARD = {'guidance': HexColor('#DDEBD6'), 'lawyer': HexColor('#EFE0B8'), 'building': HexColor('#DCDCDC'),
             'white': white, 'gold': HexColor('#F2D37A')}

# ---------------------------------------------------------------- text
def sw(text, font, size):
    return pdfmetrics.stringWidth(text, font, size)

def wrap(text, font, size, width):
    words = text.split()
    lines, cur = [], ''
    for w in words:
        t = (cur + ' ' + w).strip()
        if sw(t, font, size) <= width or not cur:
            cur = t
        else:
            lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def fit_size(text, font, width, start, minimum=4):
    s = start
    while sw(text, font, s) > width and s > minimum:
        s -= 0.25
    return s

def text_block(c, x, y, width, text, font=MONO, size=7, lead=1.2, color=black, align='l', maxlines=None):
    """Draw wrapped text with top-left at (x, y). Returns y after the block."""
    lines = wrap(text, font, size, width)
    if maxlines: lines = lines[:maxlines]
    c.setFont(font, size); c.setFillColor(color)
    for ln in lines:
        y -= size * lead
        if align == 'c': c.drawCentredString(x + width / 2, y, ln)
        else: c.drawString(x, y, ln)
    return y

def fit_block(c, x, y, width, height, text, font=MONO, size=7, lead=1.2, color=black, align='l', minimum=4.5):
    """Shrink size until the wrapped block fits in height."""
    s = size
    while s > minimum:
        lines = wrap(text, font, s, width)
        if len(lines) * s * lead <= height: break
        s -= 0.25
    return text_block(c, x, y, width, text, font, s, lead, color, align)

def head(c, text, x, y, size, color=black, anchor='c', font='HeadB', maxw=None):
    if maxw: size = fit_size(text, font, maxw, size)
    c.setFont(font, size); c.setFillColor(color)
    if anchor == 'c': c.drawCentredString(x, y, text)
    elif anchor == 'r': c.drawRightString(x, y, text)
    else: c.drawString(x, y, text)
    return size

def heading(c, title, sub=''):
    head(c, title, 36, H - 50, 16, anchor='l')
    if sub:
        text_block(c, 36, H - 56, W - 72, sub, MONO, 8, color=GREY)

def footer(c, label):
    c.setFont(MONO, 7); c.setFillColor(GREY)
    c.drawCentredString(W / 2, 20, 'MONOPLATOON v' + VERSION + '  |  ' + label + '  |  Print at 100% / Actual size')

def cutmarks(c, x, y, w, h, l=6):
    c.setStrokeColor(LGREY); c.setLineWidth(0.3)
    for px, py, dx, dy in ((x, y, -1, -1), (x + w, y, 1, -1), (x, y + h, -1, 1), (x + w, y + h, 1, 1)):
        c.line(px + dx * 2, py, px + dx * (2 + l), py)
        c.line(px, py + dy * 2, px, py + dy * (2 + l))

# ---------------------------------------------------------------- black-ink mode
INK = [False]   # when True, art is drawn in greys so it prints cleanly in black on coloured stock

def _grey(col):
    try:
        r, g, b = col.red, col.green, col.blue
    except AttributeError:
        return col
    l = 0.3 * r + 0.59 * g + 0.11 * b
    return Color(l, l, l)

class _InkCanvas:
    def __init__(self, c): self._c = c
    def setFillColor(self, col, *a, **k): self._c.setFillColor(_grey(col), *a, **k)
    def setStrokeColor(self, col, *a, **k): self._c.setStrokeColor(_grey(col), *a, **k)
    def __getattr__(self, n): return getattr(self._c, n)

def ink(c):
    return _InkCanvas(c) if INK[0] else c

# ---------------------------------------------------------------- mascot
def _stroke(c, lw=1.4):
    c.setStrokeColor(black); c.setLineWidth(lw); c.setLineCap(1); c.setLineJoin(1)

def pennyless(c, cx, cy, s=1.0, pose='shrug'):
    """Specialist Pennyless, original line art. (cx, cy) = feet centre. s = scale, 1.0 ~ 1.1 in tall."""
    c = ink(c); c.saveState(); c.translate(cx, cy); c.scale(s, s); _stroke(c)
    # legs + shorts
    c.setFillColor(white)
    c.line(-9, 0, -9, 22); c.line(9, 0, 9, 22)
    c.ellipse(-14, -2, -4, 3, fill=1, stroke=1); c.ellipse(4, -2, 14, 3, fill=1, stroke=1)   # shoes
    p = c.beginPath(); p.moveTo(-14, 22); p.lineTo(14, 22); p.lineTo(13, 36); p.lineTo(-13, 36); p.close()
    c.setFillColor(HexColor('#DADADA')); c.drawPath(p, fill=1, stroke=1)
    # torso: oversized grey PT shirt
    p = c.beginPath(); p.moveTo(-17, 35); p.lineTo(17, 35); p.lineTo(19, 62); p.lineTo(13, 66); p.lineTo(-13, 66); p.lineTo(-19, 62); p.close()
    c.setFillColor(HexColor('#C8C8C8')); c.drawPath(p, fill=1, stroke=1)
    c.setFont('HeadB', 5.2); c.setFillColor(black); c.drawCentredString(0, 48, 'ARMY')
    # arms
    if pose == 'shrug':
        c.line(-18, 60, -30, 50); c.line(-30, 50, -32, 58)
        c.line(18, 60, 30, 50); c.line(30, 50, 32, 58)
        c.setFillColor(white); c.circle(-33, 59, 3.2, fill=1, stroke=1); c.circle(33, 59, 3.2, fill=1, stroke=1)
        # the form, in the right hand
        c.setFillColor(white); c.rect(30, 56, 12, 15, fill=1, stroke=1)
        c.setLineWidth(0.5)
        for i in range(4): c.line(32, 58 + i * 3, 40, 58 + i * 3)
        _stroke(c)
    elif pose == 'salute':
        c.line(-18, 60, -26, 42); c.setFillColor(white); c.circle(-27, 40, 3.2, fill=1, stroke=1)
        c.line(18, 60, 30, 72); c.line(30, 72, 20, 80)   # wrong hand, over the eye
        c.setFillColor(white); c.circle(19, 81, 3.2, fill=1, stroke=1)
    elif pose == 'asleep':
        c.line(-18, 60, -26, 42); c.line(18, 60, 26, 42)
        c.setFillColor(white); c.circle(-27, 40, 3.2, fill=1, stroke=1); c.circle(27, 40, 3.2, fill=1, stroke=1)
    elif pose == 'hawaiian':
        c.setFillColor(HexColor('#F2A6A6')); p = c.beginPath(); p.moveTo(-17, 35); p.lineTo(17, 35); p.lineTo(19, 62); p.lineTo(13, 66); p.lineTo(-13, 66); p.lineTo(-19, 62); p.close()
        c.drawPath(p, fill=1, stroke=1)
        c.setFillColor(HexColor('#4B8F3A'))
        for fx, fy in ((-9, 44), (6, 55), (10, 40), (-4, 58)):
            for a in range(5):
                c.ellipse(fx - 2 + 2.5 * math.cos(a * 1.257), fy - 1 + 2.5 * math.sin(a * 1.257), fx + 2 + 2.5 * math.cos(a * 1.257), fy + 1 + 2.5 * math.sin(a * 1.257), fill=1, stroke=0)
        c.line(-18, 60, -30, 46); c.line(18, 60, 30, 46)
        c.setFillColor(white); c.circle(-31, 44, 3.2, fill=1, stroke=1); c.circle(31, 44, 3.2, fill=1, stroke=1)
        c.setFillColor(HexColor('#F7E08A')); c.rect(28, 46, 7, 8, fill=1, stroke=1)   # a drink
    elif pose == 'point':
        c.line(-18, 60, -26, 42); c.setFillColor(white); c.circle(-27, 40, 3.2, fill=1, stroke=1)
        c.line(18, 60, 40, 66); c.setFillColor(white); c.circle(41, 66, 3.2, fill=1, stroke=1); c.line(43, 66, 50, 67)
    elif pose == 'count':
        c.line(-18, 60, -24, 44); c.line(18, 60, 24, 44)
        c.setFillColor(white); c.circle(-25, 42, 3.2, fill=1, stroke=1); c.circle(25, 42, 3.2, fill=1, stroke=1)
        c.setFillColor(HexColor('#D8E8C8'))
        for i in range(3): c.rect(-14 + i * 3, 34 + i * 2, 24, 11, fill=1, stroke=1)
        c.setFont(MONOB, 5); c.setFillColor(black); c.drawCentredString(4, 41, '$1')
    elif pose == 'hammer':
        c.line(-18, 60, -26, 42); c.setFillColor(white); c.circle(-27, 40, 3.2, fill=1, stroke=1)
        c.line(18, 60, 30, 48); c.setFillColor(white); c.circle(31, 46, 3.2, fill=1, stroke=1)
        c.setFillColor(HexColor('#8A8A8A')); c.rect(27, 49, 11, 6, fill=1, stroke=1)   # head, no handle
    elif pose == 'pin':
        c.line(-18, 60, -26, 42); c.setFillColor(white); c.circle(-27, 40, 3.2, fill=1, stroke=1)
        c.line(18, 60, 8, 56); c.setFillColor(white); c.circle(6, 55, 3.2, fill=1, stroke=1)
        c.setFillColor(HexColor('#F2C14E'))
        for px, py in ((-8, 50), (2, 44), (-3, 58), (7, 51)):
            c.circle(px, py, 3, fill=1, stroke=1)
    elif pose == 'stand':
        c.line(-18, 60, -26, 42); c.line(18, 60, 26, 42)
        c.setFillColor(white); c.circle(-27, 40, 3.2, fill=1, stroke=1); c.circle(27, 40, 3.2, fill=1, stroke=1)
    # head
    c.setFillColor(white); c.circle(0, 78, 12, fill=1, stroke=1)
    # patrol cap
    c.setFillColor(HexColor('#B9B59A'))
    p = c.beginPath(); p.moveTo(-12, 84); p.lineTo(12, 84); p.lineTo(11, 92); p.lineTo(-11, 92); p.close(); c.drawPath(p, fill=1, stroke=1)
    c.rect(-12, 82, 27, 3, fill=1, stroke=1)
    # face
    c.setFillColor(black)
    if pose == 'asleep':
        c.setLineWidth(1.2); c.line(-6, 77, -2, 77); c.line(2, 77, 6, 77)
        c.setFont(MONO, 6); c.drawString(13, 88, 'z'); c.setFont(MONO, 8); c.drawString(17, 94, 'z')
        c.setLineWidth(1.0); c.line(-3, 71, 3, 71)
    else:
        c.circle(-4, 78, 1.3, fill=1, stroke=0); c.circle(4, 78, 1.3, fill=1, stroke=0)
        c.setLineWidth(1.0)
        if pose == 'hawaiian':
            c.arc(-4, 68, 4, 74, startAng=200, extent=140)
        else:
            c.line(-4, 71, 4, 70.5)   # flat mouth
    # stubble (the regulation says shave; the mirror says no)
    c.setLineWidth(0.5); c.line(-7, 72, -5, 73); c.line(7, 72, 5, 73)
    c.restoreState()

def secretary(c, cx, cy, s=1.0):
    """Secretary Brock Lethality, mid-push-up, in a suit, stopwatch on the floor."""
    c.saveState(); c.translate(cx, cy); c.scale(s, s); _stroke(c)
    c.setFillColor(HexColor('#2B2B3A'))
    p = c.beginPath(); p.moveTo(-40, 14); p.lineTo(20, 20); p.lineTo(22, 30); p.lineTo(-38, 24); p.close(); c.drawPath(p, fill=1, stroke=1)   # body
    c.line(-40, 14, -52, 2); c.line(20, 20, 16, 2); c.line(10, 18, 6, 2)   # legs/arms
    c.setFillColor(white); c.ellipse(-56, 0, -48, 3, fill=1, stroke=1)
    c.circle(16, 0, 3, fill=1, stroke=1); c.circle(6, 0, 3, fill=1, stroke=1)
    c.setFillColor(white); c.circle(32, 32, 11, fill=1, stroke=1)   # head
    c.setFillColor(black); c.circle(30, 34, 1.3, fill=1, stroke=0); c.circle(37, 34, 1.3, fill=1, stroke=0)
    c.setLineWidth(1.6); c.line(30, 27, 38, 27)   # determined mouth
    c.setFillColor(HexColor('#2B2B3A')); p = c.beginPath(); p.moveTo(22, 38); p.lineTo(43, 40); p.lineTo(40, 45); p.lineTo(24, 44); p.close(); c.drawPath(p, fill=1, stroke=1)   # hair
    c.setFillColor(RED); c.rect(20, 22, 4, 9, fill=1, stroke=1)   # tie
    c.setFillColor(white); c.circle(-20, 6, 6, fill=1, stroke=1); c.line(-20, 12, -20, 15); c.line(-20, 6, -17, 9)   # stopwatch
    c.restoreState()

def phone_hand(c, cx, cy, s=1.0):
    """The Commander-in-Chief: a hand, a phone, 2:00 a.m."""
    c.saveState(); c.translate(cx, cy); c.scale(s, s); _stroke(c)
    c.setFillColor(white)
    p = c.beginPath(); p.moveTo(-18, 0); p.lineTo(18, 0); p.lineTo(16, 30); p.lineTo(-16, 30); p.close(); c.drawPath(p, fill=1, stroke=1)   # hand
    for i in range(4): c.line(-14 + i * 9, 30, -14 + i * 9, 40)
    c.setFillColor(HexColor('#1A1A1A')); c.roundRect(-11, 20, 22, 44, 3, fill=1, stroke=1)   # phone
    c.setFillColor(HexColor('#DCE9FF')); c.rect(-9, 24, 18, 36, fill=1, stroke=0)
    c.setFont(MONOB, 7); c.setFillColor(black); c.drawCentredString(0, 50, '2:00'); c.setFont(MONO, 4.5); c.drawCentredString(0, 44, 'AM')
    c.setFont(MONO, 3.5)
    for i in range(3): c.drawCentredString(0, 36 - i * 4.5, 'ALL CAPS')
    c.restoreState()

# ---------------------------------------------------------------- spot art
def icon(c, name, cx, cy, s=1.0):
    c = ink(c); c.saveState(); c.translate(cx, cy); c.scale(s, s); _stroke(c, 1.1); c.setFillColor(white)
    if name == 'mold':
        for dx, dy, r in ((0, 0, 7), (-7, 4, 5), (6, 5, 4), (-3, -6, 4), (5, -4, 3)):
            c.setFillColor(HexColor('#7A9A5A')); c.circle(dx, dy, r, fill=1, stroke=1)
        c.setFillColor(black)
        for dx, dy in ((-2, 2), (4, -1), (-6, 5), (2, 6)): c.circle(dx, dy, 0.9, fill=1, stroke=0)
    elif name == 'dryer':
        c.rect(-10, -10, 20, 22, fill=1, stroke=1); c.circle(0, 0, 6, fill=1, stroke=1); c.circle(0, 0, 3.5, fill=0, stroke=1); c.circle(-6, 9, 1.2, fill=1, stroke=0)
        c.setFont(MONO, 4); c.setFillColor(black); c.drawCentredString(0, -14, 'OUT OF ORDER')
    elif name == 'stairs':
        p = c.beginPath(); p.moveTo(-12, -10)
        for i in range(5): p.lineTo(-12 + i * 5, -10 + i * 4); p.lineTo(-12 + (i + 1) * 5, -10 + i * 4)
        p.lineTo(13, 10); p.lineTo(13, -10); p.close(); c.drawPath(p, fill=1, stroke=1)
    elif name == 'bus':
        c.roundRect(-14, -6, 28, 14, 2, fill=1, stroke=1)
        for i in range(4): c.rect(-11 + i * 6.5, 0, 4.5, 5, fill=0, stroke=1)
        c.setFillColor(black); c.circle(-8, -7, 2.5, fill=1, stroke=1); c.circle(8, -7, 2.5, fill=1, stroke=1)
        c.setFont('HeadB', 9); c.drawString(15, 2, '!!!')
    elif name == 'duffel':
        c.roundRect(-12, -6, 24, 13, 5, fill=1, stroke=1); c.line(-6, 7, -2, 11); c.line(2, 11, 6, 7); c.line(-2, 11, 2, 11)
        c.setFont(MONO, 4); c.setFillColor(black); c.drawCentredString(0, -2, 'x2')
    elif name == 'tattoo':
        c.line(-10, -8, 8, 10); c.line(5, 7, 11, 13); c.rect(-4, -2, 6, 6, fill=1, stroke=1)
        c.setFont(MONO, 4); c.setFillColor(black); c.drawString(-12, -14, 'MOM?')
    elif name == 'pawn':
        for dx, dy in ((-6, 0), (6, 0), (0, -9)): c.circle(dx, dy, 4, fill=1, stroke=1)
        c.line(-8, 8, 8, 8); c.line(0, 8, 0, 4)
    elif name == 'car':
        p = c.beginPath(); p.moveTo(-15, -4); p.lineTo(-10, 4); p.lineTo(6, 4); p.lineTo(14, -4); p.close(); c.drawPath(p, fill=1, stroke=1)
        c.rect(-15, -8, 30, 5, fill=1, stroke=1); c.setFillColor(black); c.circle(-8, -9, 3, fill=1, stroke=1); c.circle(8, -9, 3, fill=1, stroke=1)
        c.setFont(MONO, 4); c.drawCentredString(0, 7, '29% APR')
    elif name == 'truck':
        c.rect(-14, -6, 18, 10, fill=1, stroke=1); c.rect(4, -6, 10, 7, fill=1, stroke=1)
        c.setFillColor(HexColor('#8A8A8A')); c.rect(-11, -10, 5, 4, fill=1, stroke=1); c.rect(6, -10, 5, 4, fill=1, stroke=1)   # on blocks
    elif name == 'smoke':
        c.setFillColor(HexColor('#E0E0E0')); c.circle(-5, 4, 5, fill=1, stroke=1); c.circle(3, 7, 6, fill=1, stroke=1); c.circle(8, 1, 4, fill=1, stroke=1)
        c.setFillColor(white); c.rect(-2, -10, 3, 8, fill=1, stroke=1); c.setFillColor(HexColor('#E8743B')); c.rect(-2, -3, 3, 1.5, fill=1, stroke=0)
    elif name == 'cage':
        c.rect(-12, -10, 24, 20, fill=1, stroke=1)
        for i in range(5): c.line(-12 + i * 6, -10, -12 + i * 6, 10)
        c.setFillColor(black); c.setFont(MONO, 4); c.drawCentredString(0, -15, 'CLOSED')
    elif name == 'inbox':
        for i in range(3): c.rect(-11, -8 + i * 6, 22, 5, fill=1, stroke=1)
        c.setFillColor(black); c.setFont(MONO, 4); c.drawCentredString(0, 11, 'IN  IN  IN')
    elif name == 'pallet':
        c.rect(-12, -8, 24, 4, fill=1, stroke=1); c.rect(-10, -4, 20, 12, fill=1, stroke=1); c.line(-10, 2, 10, 2)
        c.setFillColor(black); c.setFont(MONO, 4); c.drawCentredString(0, -13, 'ON THE TRUCK')
    elif name == 'projector':
        c.rect(-14, -8, 28, 18, fill=1, stroke=1); c.setFillColor(HexColor('#DCE9FF')); c.rect(-12, -6, 24, 14, fill=1, stroke=0)
        c.setFillColor(black); c.setFont(MONO, 3.5); c.drawCentredString(0, 2, 'SLIDE 1/312'); c.drawCentredString(0, -3, 'AGENDA')
    elif name == 'knife':
        c.line(-12, -6, 6, 8); c.setFillColor(black); c.rect(5, 6, 8, 5, fill=1, stroke=1)
        c.setFont(MONO, 4); c.drawString(-13, -13, '$400')
    elif name == 'cart':
        c.rect(-10, -2, 18, 10, fill=1, stroke=1); c.line(8, 8, 12, 12); c.setFillColor(black); c.circle(-7, -5, 2, fill=1, stroke=1); c.circle(5, -5, 2, fill=1, stroke=1)
        c.setFont(MONO, 4); c.drawCentredString(0, 11, '+5%')
    elif name == 'bowling':
        c.setFillColor(white)
        for dx in (-7, 0, 7): c.ellipse(dx - 2.5, -8, dx + 2.5, 6, fill=1, stroke=1); c.circle(dx, 7, 2, fill=1, stroke=1)
        c.setFillColor(black); c.circle(-12, -4, 4, fill=1, stroke=1)
    elif name == 'slides':
        for i in range(3): c.rect(-12 + i * 4, -8 + i * 3, 18, 12, fill=1, stroke=1)
        c.setFont(MONO, 4); c.setFillColor(black); c.drawString(-6, 0, 'PPT')
    elif name == 'fork':
        c.line(-8, -10, -8, 10); c.line(-11, 10, -11, 4); c.line(-5, 10, -5, 4); c.line(-11, 4, -5, 4)
        c.line(6, -10, 6, 10); c.ellipse(3, 4, 9, 11, fill=1, stroke=1)
    elif name == 'parking':
        c.rect(-10, -4, 20, 16, fill=1, stroke=1); c.line(0, -4, 0, -12); c.setFont('HeadB', 11); c.setFillColor(black); c.drawCentredString(0, 1, 'P')
        c.setFont(MONO, 3.5); c.drawCentredString(0, -16, 'RESERVED')
    elif name == 'pentagon':
        p = c.beginPath()
        for i in range(5):
            a = math.pi / 2 + i * 2 * math.pi / 5; x, y = 12 * math.cos(a), 12 * math.sin(a)
            (p.moveTo if i == 0 else p.lineTo)(x, y)
        p.close(); c.drawPath(p, fill=1, stroke=1)
        p = c.beginPath()
        for i in range(5):
            a = math.pi / 2 + i * 2 * math.pi / 5; x, y = 6 * math.cos(a), 6 * math.sin(a)
            (p.moveTo if i == 0 else p.lineTo)(x, y)
        p.close(); c.drawPath(p, fill=0, stroke=1)
    elif name == 'desk':
        c.rect(-14, -2, 28, 4, fill=1, stroke=1); c.line(-12, -2, -12, -10); c.line(12, -2, 12, -10)
        c.rect(-6, 2, 8, 6, fill=1, stroke=1); c.line(-2, 8, -2, 12); c.line(-5, 12, 1, 12)   # a phone
        c.setFillColor(HexColor('#F7E08A')); c.rect(4, 2, 5, 7, fill=1, stroke=1)   # coffee
    elif name == 'humvee':
        c.rect(-15, -5, 30, 9, fill=1, stroke=1); c.rect(-6, 4, 14, 6, fill=1, stroke=1)
        c.setFillColor(black); c.circle(-9, -7, 3, fill=1, stroke=1); c.circle(9, -7, 3, fill=1, stroke=1)
    elif name == 'swamp':
        c.setFillColor(HexColor('#6E8B5A')); c.ellipse(-16, -5, 16, 3, fill=1, stroke=1)
        for dx in (-9, -3, 4, 10): c.line(dx, 0, dx, 10)
    elif name == 'desert':
        c.setFillColor(HexColor('#E8D59A')); p = c.beginPath(); p.moveTo(-16, -4); p.curveTo(-8, 6, 0, 6, 16, -4); p.close(); c.drawPath(p, fill=1, stroke=1)
        c.circle(10, 10, 4, fill=0, stroke=1)
    elif name == 'plane':
        p = c.beginPath(); p.moveTo(-14, 0); p.lineTo(10, 0); p.lineTo(14, 3); p.lineTo(10, 4); p.lineTo(-14, 2); p.close(); c.drawPath(p, fill=1, stroke=1)
        c.line(-2, 2, -6, 10); c.line(-6, 10, 2, 10); c.line(2, 10, 4, 3); c.line(-12, 2, -14, 8)
        c.setFont(MONO, 4); c.setFillColor(black); c.drawCentredString(0, -8, 'GATE B41')
    elif name == 'tent':
        p = c.beginPath(); p.moveTo(-16, -6); p.lineTo(0, 10); p.lineTo(16, -6); p.close(); c.setFillColor(HexColor('#D8CFA8')); c.drawPath(p, fill=1, stroke=1)
        c.line(0, 10, 0, -6); c.setFont(MONO, 4); c.setFillColor(black); c.drawCentredString(0, -12, 'WEEK 6')
    elif name == 'loan':
        c.rect(-12, -8, 24, 16, fill=1, stroke=1); c.setFont('HeadB', 11); c.setFillColor(black); c.drawCentredString(0, -4, '$'); c.setFont(MONO, 3.5); c.drawCentredString(0, 10, 'EASY TERMS*')
    elif name == 'headset':
        c.arc(-10, -6, 10, 14, startAng=0, extent=180); c.rect(-12, -6, 4, 8, fill=1, stroke=1); c.rect(8, -6, 4, 8, fill=1, stroke=1)
        c.setFont(MONO, 3.5); c.setFillColor(black); c.drawCentredString(0, -12, 'TICKET CLOSED')
    elif name == 'calc':
        c.rect(-8, -10, 16, 22, fill=1, stroke=1); c.rect(-6, 5, 12, 5, fill=0, stroke=1)
        for r in range(3):
            for k in range(3): c.rect(-6 + k * 4.3, -8 + r * 4, 3, 2.5, fill=0, stroke=1)
        c.setFont(MONO, 4); c.setFillColor(black); c.drawCentredString(0, 6.5, '-$4')
    elif name == 'chicken':
        c.ellipse(-12, -6, 12, 6, fill=1, stroke=1); c.line(10, 2, 16, 6); c.line(16, 6, 18, 4)
        c.setFont(MONO, 4); c.setFillColor(black); c.drawCentredString(0, -12, 'MANDATORY')
    elif name == 'belt':
        c.setFillColor(HexColor('#D4F542')); c.roundRect(-16, -3, 32, 6, 3, fill=1, stroke=1)
        c.setFillColor(HexColor('#8A8A8A')); c.rect(-3, -3, 6, 6, fill=1, stroke=1)
    elif name == 'glove':
        c.setFillColor(HexColor('#5B6B3A')); c.roundRect(-8, -10, 16, 16, 3, fill=1, stroke=1)
        for i in range(4): c.roundRect(-8 + i * 4, 4, 3.4, 8, 1.5, fill=1, stroke=1)
        c.roundRect(-13, -4, 5, 8, 2, fill=1, stroke=1)
    elif name == 'beret':
        c.setFillColor(HexColor('#2F6B3A')); c.ellipse(-14, -4, 14, 6, fill=1, stroke=1); c.line(-4, 6, -2, 9)
    elif name == 'hammer':
        c.setFillColor(HexColor('#8A8A8A')); c.rect(-10, -4, 20, 8, fill=1, stroke=1)
        c.setStrokeColor(GREY); c.setDash(2, 2); c.line(0, -4, 0, -18); c.setDash()
        c.setFont(MONO, 3.5); c.setFillColor(black); c.drawCentredString(0, -22, 'HANDLE: N/A')
    elif name == 'mre':
        c.setFillColor(HexColor('#B5A97A')); c.rect(-10, -12, 20, 24, fill=1, stroke=1)
        c.setFont(MONO, 3.5); c.setFillColor(black); c.drawCentredString(0, 3, 'MENU 4'); c.drawCentredString(0, -2, 'VEG'); c.drawCentredString(0, -7, 'OMELET')
    elif name == 'coin':
        c.setFillColor(HexColor('#D9B44A')); c.circle(0, 0, 11, fill=1, stroke=1); c.circle(0, 0, 8, fill=0, stroke=1)
        c.setFont('HeadB', 6); c.setFillColor(black); c.drawCentredString(0, -2, '1SG')
    elif name == 'shelf':
        c.rect(-16, -2, 32, 3, fill=1, stroke=1)
        for i in range(4): c.rect(-14 + i * 8, 1, 6, 9, fill=1, stroke=1)
    elif name == 'memo':
        c.rect(-9, -12, 18, 24, fill=1, stroke=1); c.setLineWidth(0.5)
        for i in range(6): c.line(-6, -8 + i * 3.5, 6, -8 + i * 3.5)
        c.setFont(MONOB, 4); c.setFillColor(black); c.drawCentredString(0, 8, 'MFR')
    elif name == 'mustache':
        c.setFillColor(black); p = c.beginPath(); p.moveTo(0, 0); p.curveTo(-6, 6, -14, 4, -14, -2); p.curveTo(-8, -1, -3, -3, 0, -4); p.curveTo(3, -3, 8, -1, 14, -2); p.curveTo(14, 4, 6, 6, 0, 0); p.close(); c.drawPath(p, fill=1, stroke=0)
    elif name == 'syringe':
        c.rect(-12, -3, 18, 6, fill=1, stroke=1); c.line(6, 0, 14, 0); c.line(-12, 0, -16, 0); c.rect(-18, -4, 2, 8, fill=1, stroke=1)
        c.setFont(MONO, 3.5); c.setFillColor(black); c.drawCentredString(0, -10, 'LAB FEE $50')
    elif name == 'sign':
        c.rect(-14, 2, 28, 10, fill=1, stroke=1); c.line(0, 2, 0, -10)
        c.setFont('HeadB', 4.5); c.setFillColor(black); c.drawCentredString(0, 5.5, 'FORT ______')
    elif name == 'stopwatch':
        c.circle(0, 0, 10, fill=1, stroke=1); c.line(0, 10, 0, 14); c.line(-3, 14, 3, 14); c.line(0, 0, 0, 6); c.line(0, 0, 4, -2)
    elif name == 'sleeve':
        c.rect(-6, -12, 12, 20, fill=1, stroke=1); c.rect(-7, 4, 14, 5, fill=1, stroke=1); c.setFillColor(HexColor('#B9B59A')); c.rect(-7, 4, 14, 5, fill=1, stroke=1)
    elif name == 'cliff':
        c.rect(-16, -10, 14, 16, fill=1, stroke=1); c.setFont(MONO, 4); c.setFillColor(black); c.drawString(0, -2, 'CR'); c.drawString(0, -7, '11 wk')
    elif name == 'stack':
        for i in range(5): c.rect(-10 + (i % 2) * 2, -10 + i * 4, 20, 3.5, fill=1, stroke=1)
    elif name == 'printer':
        c.rect(-12, -6, 24, 10, fill=1, stroke=1); c.rect(-8, 4, 16, 6, fill=1, stroke=1); c.setFillColor(black); c.circle(8, -2, 1.2, fill=1, stroke=0)
        c.setFont(MONO, 3.5); c.drawCentredString(0, -11, 'TONER LOW')
    elif name == 'bake':
        c.setFillColor(HexColor('#E8B86A')); c.ellipse(-10, -2, 10, 8, fill=1, stroke=1); c.rect(-12, -6, 24, 4, fill=1, stroke=1)
        c.setFont(MONO, 3.5); c.setFillColor(black); c.drawCentredString(0, -11, 'FRG  $2 EA')
    elif name == 'trophy':
        c.rect(-6, -10, 12, 3, fill=1, stroke=1); c.rect(-2, -7, 4, 4, fill=1, stroke=1); c.ellipse(-8, -3, 8, 10, fill=1, stroke=1)
        c.setFont(MONO, 3.5); c.setFillColor(black); c.drawCentredString(0, -15, 'SOLDIER OF MONTH')
    elif name == 'rocket':
        c.setFillColor(white); p = c.beginPath(); p.moveTo(0, 14); p.lineTo(6, 0); p.lineTo(6, -8); p.lineTo(-6, -8); p.lineTo(-6, 0); p.close(); c.drawPath(p, fill=1, stroke=1)
        c.setStrokeColor(RED); c.setLineWidth(1.6); c.line(-10, -10, 10, 12); c.line(-10, 12, 10, -10)
    elif name == 'slip':
        c.rect(-9, -12, 18, 24, fill=1, stroke=1); c.setFont(MONOB, 4); c.setFillColor(black); c.drawCentredString(0, 6, 'SICK'); c.drawCentredString(0, 1, 'CALL'); c.setFont(MONO, 3.2); c.drawCentredString(0, -5, 'MOTRIN'); c.drawCentredString(0, -9, 'WATER')
    elif name == 'xbox':
        c.rect(-12, -6, 24, 12, fill=1, stroke=1); c.circle(0, 0, 3, fill=0, stroke=1); c.setFont(MONO, 3.5); c.setFillColor(black); c.drawCentredString(0, -11, '+40%')
    elif name == 'grass':
        for dx in range(-14, 16, 4): c.line(dx, -6, dx + 1, 6)
        c.line(-16, -6, 16, -6)
    elif name == 'glove_beret':
        c.setFillColor(HexColor('#5B6B3A')); c.roundRect(-8, -4, 16, 10, 3, fill=1, stroke=1)
        for i in range(4): c.roundRect(-8 + i * 4, 5, 3.4, 7, 1.5, fill=1, stroke=1)
        c.circle(0, -12, 7, fill=0, stroke=1)   # a head under it
    elif name == 'patches':
        c.setFillColor(HexColor('#F2C14E'))
        for dx, dy in ((-8, 4), (4, 6), (-2, -6), (9, -4)): c.circle(dx, dy, 4.5, fill=1, stroke=1)
    elif name == 'parade':
        for dx in (-12, -4, 4, 12): c.line(dx, -8, dx, 4); c.circle(dx, 7, 2.5, fill=1, stroke=1)
        c.setFont(MONO, 3.5); c.setFillColor(black); c.drawCentredString(0, -13, '$40M')
    elif name == 'phone_ring':
        c.rect(-6, -8, 12, 10, fill=1, stroke=1); c.ellipse(-9, 2, 9, 7, fill=1, stroke=1)
        c.setLineWidth(0.7); c.arc(-14, -4, -8, 10, startAng=60, extent=60); c.arc(8, -4, 14, 10, startAng=60, extent=60)
    c.restoreState()
