from mp import *
from data import GLOSSARY, CHARACTERS
from reportlab.platypus import BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, PageBreak, Table, TableStyle, KeepTogether, Flowable
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_CENTER

OUT = out_path('Monoplatoon_Phase5_Rulebook.pdf')

H1 = ParagraphStyle('h1', fontName='HeadB', fontSize=16, leading=19, spaceBefore=14, spaceAfter=5, textColor=black)
H2 = ParagraphStyle('h2', fontName='HeadB', fontSize=11, leading=13, spaceBefore=9, spaceAfter=3, textColor=OLIVE)
BODY = ParagraphStyle('body', fontName=MONO, fontSize=8.2, leading=10.4, spaceAfter=4, textColor=black)
BOLD = ParagraphStyle('bold', parent=BODY, fontName=MONOB)
FLV = ParagraphStyle('flv', parent=BODY, textColor=GREY, leftIndent=10, spaceAfter=5)
BUL = ParagraphStyle('bul', parent=BODY, leftIndent=12, bulletIndent=2, spaceAfter=2)
NUM = ParagraphStyle('num', parent=BODY, leftIndent=16, bulletIndent=2, spaceAfter=2)
GLS = ParagraphStyle('gls', parent=BODY, fontSize=7.6, leading=9.4, textColor=GREY, spaceAfter=1.5)
CEN = ParagraphStyle('cen', parent=BODY, alignment=TA_CENTER)

class Art(Flowable):
    def __init__(self, fn, w, h): Flowable.__init__(self); self.fn, self.width, self.height = fn, w, h
    def draw(self): self.fn(self.canv, self.width, self.height)

def P(t, st=BODY): return Paragraph(t, st)
def B(items):
    return [Paragraph(t, BUL, bulletText='•') for t in items]
def N(items):
    return [Paragraph(t, NUM, bulletText='%d.' % (i + 1)) for i, t in enumerate(items)]

def on_page(c, doc):
    c.saveState(); c.setFont(MONO, 7); c.setFillColor(GREY)
    c.drawString(54, 30, 'MONOPLATOON v' + VERSION + '  |  Rulebook'); c.drawRightString(W - 54, 30, 'Page %d' % doc.page)
    c.setStrokeColor(OLIVE); c.setLineWidth(1.2); c.line(54, H - 44, W - 54, H - 44)
    c.setFont('HeadB', 8); c.setFillColor(OLIVE); c.drawString(54, H - 40, 'HURRY UP AND WAIT.'); c.restoreState()

def cover(c, w, h):
    c.setFillColor(OLIVE); c.setStrokeColor(black); c.setLineWidth(1.5); c.rect(0, h - 120, w, 110, fill=1, stroke=1)
    s = 60
    while sw('MONOPLATOON', 'HeadB', s) > w - 40: s -= 1
    c.setFont('HeadB', s); c.setFillColor(black); c.drawCentredString(w / 2 + 3, h - 88, 'MONOPLATOON'); c.setFillColor(white); c.drawCentredString(w / 2, h - 85, 'MONOPLATOON')
    c.setFont(MONOB, 16); c.setFillColor(black); c.drawCentredString(w / 2, h - 150, 'HURRY UP AND WAIT.')
    c.setFont(MONO, 9); c.setFillColor(GREY); c.drawCentredString(w / 2, h - 165, 'A property-trading game about the modern enlisted experience. Legally still Monopoly.')
    pennyless(c, w / 2 - 80, h - 420, 2.2, 'shrug')
    secretary(c, w / 2 + 120, h - 380, 1.0)
    phone_hand(c, w / 2 + 150, h - 280, 0.9)
    c.setFont(MONO, 7.5); c.setFillColor(GREY)
    c.drawCentredString(w / 2 - 80, h - 435, 'SPC Pennyless, who acts out the cards')
    c.drawCentredString(w / 2 + 130, h - 400, 'Secretary Brock Lethality')
    c.drawCentredString(w / 2 + 150, h - 292, 'The Commander-in-Chief, 0200')
    c.setFillColor(black); c.setFont(MONOB, 9)
    for i, ln in enumerate(['3 to 6 players  |  90 minutes  |  nobody is eliminated', 'One player is the First Sergeant. Everyone else is a soldier.', 'The joke is the machine. Never the soldier.']):
        c.drawCentredString(w / 2, h - 480 - i * 14, ln)
    c.setFont(MONO, 6.5); c.setFillColor(GREY); c.drawCentredString(w / 2, 20, 'Uses the board, money, houses, hotels, dice and tokens from a US classic Monopoly set. All characters are invented. No real people appear.')

def build():
    doc = BaseDocTemplate(OUT, pagesize=letter, leftMargin=54, rightMargin=54, topMargin=60, bottomMargin=48, title='MONOPLATOON - Rulebook')
    frame = Frame(54, 48, W - 108, H - 108, id='f', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    cols = [Frame(54, 48, (W - 108 - 18) / 2, H - 108, id='c1', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0),
            Frame(54 + (W - 108 - 18) / 2 + 18, 48, (W - 108 - 18) / 2, H - 108, id='c2', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)]
    doc.addPageTemplates([PageTemplate(id='cover', frames=[Frame(54, 40, W - 108, H - 80, id='cv', leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)]),
                          PageTemplate(id='one', frames=[frame], onPage=on_page),
                          PageTemplate(id='two', frames=cols, onPage=on_page)])
    from reportlab.platypus import NextPageTemplate
    s = []
    s += [Art(cover, W - 108, H - 80), NextPageTemplate('one'), PageBreak()]

    s += [P('What this is', H1),
          P('MONOPLATOON is Monopoly as the modern enlisted US Army. You climb from a moldy barracks to the Pentagon while the pay system, the chain of command and Congress change the rules faster than the game can print them. Everything not covered here plays exactly as printed in the Monopoly rulebook.'),
          P('The joke is always the machine: pay, barracks, policy, budgets, the chain of command. Never the soldier, their family, or anyone a soldier would be ashamed to laugh at.', FLV),
          P('1. What you need', H1),
          P('From the Monopoly box: the board, money, houses (now Barracks Repairs), hotels (now Privatized Housing), dice and tokens.'),
          P('From this kit: board stickers, 12 character cards, the First Sergeant role card, 6 Readiness cards, three decks (Command Guidance, Barracks Lawyer, The Building), 28 deeds, 2 kinds of player aid, Smoke and Complaint trackers, five paperwork pads and the Policy Letter pad, Step tokens, a timer, and the Uniform Box.'),
          P('The Uniform Box: any box of random uniform bits. Patches, a beret, a reflective belt, a lanyard, one glove, rank tabs, and a card that says HAWAIIAN SHIRT. Players pin pieces to their shirts. This is not optional in spirit.', FLV),
          P('2. Setup, in order', H1)]
    s += N(['<b>Pick the First Sergeant.</b> Volunteer, or highest roll. The 1SG takes the role card, the bank, all three decks, the pads and a pen. He draws one Readiness card and keeps it secret.',
            '<b>Deal characters.</b> Shuffle the 12 character cards. Each regular player draws one, face up. The rest form the Character Deck, face down.',
            '<b>Hand out money.</b> The 1SG gives each regular player $1,500: two $500s, two $100s, two $50s, six $20s, five $10s, five $5s, five $1s. The 1SG holds no personal money; the bank is his.',
            '<b>Deal properties.</b> Shuffle all 28 deeds. Deal two to each regular player, face up; they are owned, not paid for. SPC Jones gets one. Return the rest to the bank.',
            '<b>Uniforms.</b> Each regular player pulls one piece from the Uniform Box, blind, and pins it on. This is their starting piece. The Hawaiian shirt card goes back in the Box.',
            '<b>Trackers.</b> Each regular player takes a Smoke tracker (clip at 0). The 1SG takes the Complaint tracker (clip at 0).',
            '<b>Shelf and timer.</b> Set the Policy Shelf empty. Set the timer to 90:00 and start it when the first player rolls.'])
    s += [P('3. Turn', H1),
          P('Roll two dice, move, act on the space, trade if you want, end turn. Doubles roll again; three doubles in a row sends you to Staff Duty. <b>Before you move on a doubles roll</b>, the 1SG draws one Building card (Staff Call) and resolves it.'),
          P('Doubles are good news. Good news attracts attention.', FLV),
          P('4. Payday', H1),
          P('Passing or landing on Payday pays $200, unless Continuing Resolution is on the shelf. At each Payday the 1SG rolls one die: on a 1, all $500 bills in the bank are frozen until the next Directive is drawn. Frozen means the bank pays and makes change only in smaller bills.'),
          P('5. Buying property and auctions', H1),
          P('Land on an unowned property and you may buy it at the printed price. If you don\'t, it must be auctioned:')]
    s += B(['The 1SG runs it. Bidding opens at $10. Anyone may bid, including the player who declined. Bids rise by any amount.',
            'After the last bid the 1SG counts "going once, going twice, sold." The winner pays the bank and takes the deed.',
            'If nobody bids, the property stays with the bank.',
            'CPT Fitzpatrick may open at $0; the count still starts at $10 for everyone else.'])
    s += [P('6. Rent, buildings, mortgages', H1),
          P('Standard. Houses are Barracks Repairs, hotels are Privatized Housing. Build evenly across a colour group. Mortgage values are printed on deeds. Rent is owed on landing; an owner at the CQ Desk still collects.'),
          P('Privatized Housing raises the rent. The card notes nothing was fixed.', FLV),
          P('7. CQ Desk (Jail)', H1),
          P('Standard jail rules: wait three turns, roll doubles, pay $50, or play a Sick Call Slip. You collect rent and may trade while there.'),
          P('8. Block Leave (Free Parking)', H1),
          P('Nothing is paid or collected here. Once per game, a player who lands here may swap characters by choice: discard theirs and draw blind from the Character Deck. SFC Fobbit may not land here; a roll that would stops him one space short.'),
          P('9. Smoke', H1),
          P('Each regular player has a Smoke tracker, 0 to 6. Cards and rules say "+1 Smoke" (yours rises) or "push +1 Smoke" (you raise another player\'s). At 6 you are chaptered: set the tracker to 0, discard your character, draw a new one blind, keep all money and property. Smoke immunity blocks pushes, not your own +1s.'),
          P('Smoke: corrective training. Push-ups, mostly. Here, a number.', FLV),
          P('10. Going broke', H1),
          P('If you can\'t pay a debt after mortgaging and selling buildings, you are broke. Hand your remaining money and unmortgaged deeds to the creditor; if the creditor is the bank, those deeds are auctioned at once. Then collect a $500 stipend from the bank, draw a new character blind, set Smoke to 0, and continue from your current space. Nobody is ever out. The stipend costs one Paperwork step: fill a Form 31 slip before taking it.'),
          P('Re-enlistment bonus. Paid in full, once, with a form.', FLV)]
    s += [P('11. The Policy Shelf', H1),
          P('Six slots, oldest on the left, newest on the right. When a seventh card arrives, the leftmost moves to the Archive pile, face up. Archived cards are not in effect. Policy Letters go to the Archive before any printed card when room is needed.'),
          P('Once per game, any player on their turn may invoke one Archived card: it returns to the shelf (pushing out the oldest) and that player immediately performs one Paperwork step from any shelf card.'),
          P('Card types', H2)]
    s += B(['<b>Directive:</b> in effect while on the shelf.',
            '<b>Walk-Back:</b> does what its text says to another card, then stays on the shelf as a reminder. If a Walk-Back and the card it contradicts are both on the shelf, the 1SG rules at the start of each round which one applies that round. A player who acted on the other one that round takes +1 Smoke.',
            '<b>Paperwork:</b> place its Step token on the named action. Every time any player takes that action, they do the step first. Steps cost nothing but time. Skipping a step: +1 Smoke, and you do it anyway.',
            '<b>Uniform Change:</b> as printed. Pieces come from the Box; pulls are blind unless the card says otherwise.'])
    s += [P('How cards reach the shelf', H2)]
    s += B(['<b>Staff Call:</b> any doubles roll, before moving.',
            '<b>Guidance:</b> a Command Guidance or Barracks Lawyer card tagged GUIDANCE. The 1SG draws one Building card after that card resolves.',
            '<b>Policy Letter:</b> once per lap (a lap ends each time the player to the 1SG\'s left passes Payday), the 1SG may write one rule on a Policy Letter sheet and place it on the shelf. It must be enforceable, specific, and apply to everyone. +1 Complaint.',
            '<b>Request Guidance:</b> on any dispute, the 1SG may draw a Building card instead of ruling. The card settles the dispute in whatever way the table agrees it does. +1 Complaint.',
            '<b>IG Complaint:</b> any player, on their turn, pays $50 to the bank; the 1SG draws a Building card. +1 Complaint.'])
    s += [P('Every Building draw adds +1 Complaint, including all of the above.', BOLD),
          P('The Inspector General exists so that complaints have somewhere to go.', FLV),
          P('12. Inspection', H1),
          P('Once per lap, at the start of any player\'s turn, the 1SG may call Inspection. Each regular player compares their uniform to every Uniform card on the shelf. Pay $20 per required piece missing and $20 per piece worn that no shelf card requires. The starting piece always counts as required. The 1SG\'s call is final; Request Guidance is allowed.'),
          P('<b>Hawaiian shirt:</b> on their turn a player may swap all uniform pieces for the Hawaiian shirt card. They are exempt from Inspection but collect no Payday while wearing it. Swapping back costs one blind pull.'),
          P('The 1SG doesn\'t know the regulation either. He\'s holding the shelf, so he\'s right.', FLV),
          P('13. "It\'s the Law"', H1),
          P('Any player may refer to anything by its original, legal name (Payday, the bank, the Department of Defense, a base) regardless of any Directive. No fine, no Smoke. The 1SG may not rule against this.'),
          P('This is the one place the game lets the soldier win. It should feel like it.', FLV),
          P('14. The First Sergeant', H1)]
    s += B(['Runs the bank and holds no money or property of his own.',
            'Collects all fines, taxes and Inspection fees into the bank.',
            'May write Policy Letters, call Inspections, Request Guidance, and initial Form 4856 slips.',
            '<b>Complaint tracker 0 to 8.</b> At 8: Relief for Cause. The regular player with the most Smoke (ties: most uniform pieces) becomes 1SG and takes the role card, bank, decks, pads and the shelf as it stands. Their character returns to the deck; their money and property go to the bank and are auctioned over the next lap. The old 1SG draws a character, takes $500, pins one piece, and starts at Payday. The new 1SG draws a fresh Readiness card; Complaints reset to 0.',
            '<b>Use It Or Lose It:</b> when the timer shows 10:00, the 1SG must spend at least $500 of bank money before 0:00, by buying anything any player offers at whatever price they ask. Failing this voids his Readiness card.'])
    s += [P('The only time the Army is generous, and for the dumbest possible reason.', FLV),
          P('15. End of game: ETS', H1),
          P('When the timer hits 0:00, finish the current turn. If the 1SG has met his Readiness card, he wins. Otherwise the regular player with the highest net worth wins: cash + deed purchase prices (mortgaged deeds at half) + building costs paid. Ties go to the player wearing the most uniform pieces.'),
          P('16. Paperwork pads', H1),
          P('Form 4856-ish for trades and Smoke pushes; Form 31-ish for Block Leave entry and stipends; Memorandum for Record for anything the 1SG wants on record; Sworn Statement for disputes before Request Guidance; Policy Letter sheets for the shelf. Fill in at least one line. Legibility is not required. It never is.'),
          P('17. Characters at a glance', H1)]
    rows = [[P('<b>%s</b>' % n, GLS), P(r, GLS)] for n, r, f, g, pz in CHARACTERS]
    t = Table(rows, colWidths=[130, W - 108 - 130]); t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LINEBELOW', (0, 0), (-1, -1), 0.3, LGREY), ('BOTTOMPADDING', (0, 0), (-1, -1), 2), ('TOPPADDING', (0, 0), (-1, -1), 2)]))
    s += [t]
    s += [P('18. Suggested add-ons', H1), P('None are required; the kit prints everything that must exist. By payoff:')]
    s += B(['<b>Uniform Box</b> (thrift store, surplus bin): the physical gag that makes Directives land.',
            '<b>Kitchen timer:</b> the clock has to be visible or Paperwork has no cost. A phone face-up works.',
            '<b>Policy Shelf:</b> six slots, cards readable. Binder clips on a ruler; tape on the table edge.',
            '<b>Pen on a string</b>, taped to the 1SG\'s seat.',
            '<b>Step tokens:</b> paperclips or plastic army men. Don\'t use houses.',
            '<b>Bank-cup die:</b> a spare d6 in a mug, for the $500 freeze.',
            '<b>A "TOP" nameplate</b> and an Archive tray (the box lid). Theatre.'])
    s += [NextPageTemplate('two'), PageBreak(), P('Glossary', H1), P('Every straight-faced one-liner from the board and cards, in one place.', FLV)]
    s += [P('<b>%s.</b> %s' % (k, v), GLS) for k, v in GLOSSARY]
    s += [NextPageTemplate('one'), PageBreak(), P('Print checklist', H1), P('Everything prints on ordinary portrait letter pages at 100% scale. Mirrored back sheets assume you flip on the long edge.')]
    rows = [[P('<b>File</b>', GLS), P('<b>Paper</b>', GLS), P('<b>Pages</b>', GLS), P('<b>Notes</b>', GLS)],
            [P('Phase 1: Board stickers', GLS), P('Matte sticker paper', GLS), P('6', GLS), P('Mint #BFDDC8 backing. Cut on the black line. Apply bar A, then B, then the mascot piece. Badge covers the maker\'s oval.', GLS)],
            [P('Phase 2: Command Guidance', GLS), P('Pale green 65 lb', GLS), P('2', GLS), P('Single-sided, black ink.', GLS)],
            [P('Phase 2: Barracks Lawyer', GLS), P('Buff / manila 65 lb', GLS), P('2', GLS), P('Single-sided, black ink.', GLS)],
            [P('Phase 2: The Building', GLS), P('Grey 65 lb', GLS), P('4', GLS), P('Colour. Front sheet, flip, back sheet, twice.', GLS)],
            [P('Phase 3: Characters, 1SG, Readiness', GLS), P('White 65 lb', GLS), P('6', GLS), P('Front, flip, back, three times.', GLS)],
            [P('Phase 3: Deeds', GLS), P('White 65 lb', GLS), P('4', GLS), P('Single-sided.', GLS)],
            [P('Phase 4: Player aids', GLS), P('Goldenrod 65 lb', GLS), P('3', GLS), P('Single-sided, 6 x 4 in.', GLS)],
            [P('Phase 4: Trackers', GLS), P('Goldenrod 65 lb', GLS), P('3', GLS), P('Single-sided, 5 x 3 in. Paperclip markers.', GLS)],
            [P('Phase 4: Pads', GLS), P('Plain 20 lb', GLS), P('18', GLS), P('Cut, stack 36, clamp, brush pad glue or PVA on the top edge, let dry.', GLS)],
            [P('Phase 5: Rulebook', GLS), P('Plain 20 lb', GLS), P('this file', GLS), P('Duplex if you like; staple the long edge.', GLS)]]
    t = Table(rows, colWidths=[150, 95, 40, W - 108 - 285]); t.setStyle(TableStyle([('VALIGN', (0, 0), (-1, -1), 'TOP'), ('LINEBELOW', (0, 0), (-1, -1), 0.3, LGREY), ('BACKGROUND', (0, 0), (-1, 0), MINT), ('BOTTOMPADDING', (0, 0), (-1, -1), 3), ('TOPPADDING', (0, 0), (-1, -1), 3)]))
    s += [t, Spacer(1, 10), P('Cardstock colours: pale green, buff, grey, white, goldenrod. Any 65 lb (176 gsm) pack will do; heavier jams home printers.', FLV),
          P('Uniform Box shopping list', H2)]
    s += B(['A reflective belt (the real thing, if you can find one; a yellow sash otherwise).', 'A beret, any colour. Pink is funnier.', 'One glove.', 'A lanyard with an empty badge holder.', 'A handful of patches, pins or rank tabs.', 'Safety pins, a dozen.', 'One index card reading HAWAIIAN SHIRT, or an actual Hawaiian shirt.'])
    doc.build(s)

if __name__ == '__main__':
    build(); print('ok')
