from mp import *
from cards import CW, CH

OUT = out_path('Monoplatoon_Phase4_Table_Pieces.pdf')
AW, AH = 6 * IN, 4 * IN
TW, TH = 5 * IN, 3 * IN
PW, PH = 2 * IN, 3 * IN

# ------------------------------------------------------------ player aids
def rich(c, x, y, w, text, size=7.6, lead=1.22, bullet=False, color=black):
    indent = 9 if bullet else 0
    pre = text[:text.index(':') + 1] if ':' in text[:34] else ''
    lines = wrap(text, MONO, size, w - indent)
    if bullet:
        c.setFillColor(OLIVE); c.rect(x + 1, y - size * lead + 1.6, 3.2, 3.2, fill=1, stroke=0)
    for i, ln in enumerate(lines):
        y -= size * lead
        c.setFillColor(color)
        if i == 0 and pre and ln.startswith(pre):
            c.setFont(MONOB, size); c.drawString(x + indent, y, pre)
            c.setFont(MONO, size); c.drawString(x + indent + sw(pre, MONO, size), y, ln[len(pre):])
        else:
            c.setFont(MONO, size); c.drawString(x + indent, y, ln)
    return y

def aid_frame(c, x, y, title, sub):
    c.setStrokeColor(LGREY); c.setLineWidth(0.3); c.rect(x, y, AW, AH)
    c.setFillColor(OLIVE); c.setStrokeColor(black); c.setLineWidth(0.8); c.rect(x + 8, y + AH - 40, AW - 16, 32, fill=1, stroke=1)
    head(c, title, x + 20, y + AH - 30, 15, color=white, anchor='l')
    c.setFillColor(white); c.setFont(MONOB, 7.2); c.drawRightString(x + AW - 16, y + AH - 27, sub)
    c.setStrokeColor(black); c.setLineWidth(0.8); c.rect(x + 8, y + 8, AW - 16, AH - 16)

def regular_aid(c, x, y):
    aid_frame(c, x, y, 'SOLDIER', 'PLAYER AID')
    lx, rx, cw = x + 18, x + AW / 2 + 6, AW / 2 - 26; top = y + AH - 48
    yy = rich(c, lx, top, cw, 'Your turn: roll, move, act, trade. Doubles = Staff Call first (1SG draws), then move.', 9.4)
    yy = rich(c, lx, yy - 4, cw, 'Unowned property: buy it, or it goes to auction. Opens at $10, anyone can bid.', 8.8, bullet=True)
    yy = rich(c, lx, yy - 2, cw, 'Smoke 6 = chaptered: new character, keep everything else.', 8.8, bullet=True)
    yy = rich(c, lx, yy - 2, cw, 'Broke: $500 stipend, new character, keep playing. Fill a Form 31 first.', 8.8, bullet=True)
    yy = rich(c, lx, yy - 2, cw, "It's the Law: you may always use the legal name. No fine, ever.", 8.8, bullet=True)
    yy = rich(c, rx, top, cw, 'The shelf: Directives stay. Walk-Backs contradict; 1SG picks which rules this round. Paperwork = do the step first. Uniform = match the shelf or pay $20 a piece.', 9.0)
    yy = rich(c, rx, yy - 4, cw, 'Your weapons: IG Complaint ($50, 1SG draws). Invoke an Archived card (once). Block Leave = swap character (once).', 8.8, bullet=True)
    yy = rich(c, rx, yy - 2, cw, 'ETS: at 0:00, highest net worth wins. Cash + deed prices + buildings.', 8.8, bullet=True)
    rich(c, x + 18, y + 34, AW - 110, "Remember: the 1SG doesn't know the regulation either. He's just holding the shelf.", 7.4, color=FLAV)
    pennyless(c, x + AW - 48, y + 14, 0.5, 'shrug')

def sergeant_aid(c, x, y):
    aid_frame(c, x, y, 'FIRST SERGEANT', 'PLAYER AID')
    lx, rx, cw = x + 18, x + AW / 2 + 6, AW / 2 - 26; top = y + AH - 48
    yy = rich(c, lx, top, cw, 'You are the bank. Every fine, tax and fee comes to it. You own nothing.', 9.4)
    yy = rich(c, lx, yy - 4, cw, 'Once per lap: call Inspection ($20 per piece missing or extra). Write one Policy Letter (MFR pad; enforceable, applies to all; +1 Complaint).', 8.4, bullet=True)
    yy = rich(c, lx, yy - 2, cw, 'Any dispute: rule, or Request Guidance (draw from the Building; +1 Complaint).', 8.4, bullet=True)
    yy = rich(c, lx, yy - 2, cw, 'Payday: roll a die. A 1 freezes the $500s until the next Directive.', 8.4, bullet=True)
    yy = rich(c, rx, top, cw, 'Every Building draw: +1 Complaint. At 8 you are relieved; the player with the most Smoke takes the chair and your shelf.', 9.0)
    yy = rich(c, rx, yy - 4, cw, 'Auctions: open at $10, count it down, stays with the bank if no bids.', 8.4, bullet=True)
    yy = rich(c, rx, yy - 2, cw, '10:00 on the clock: spend $500 of bank money or your Readiness card is void.', 8.4, bullet=True)
    yy = rich(c, rx, yy - 2, cw, 'Win: your secret Readiness card at ETS.', 8.4, bullet=True)
    rich(c, x + 18, y + 34, AW - 110, "Remember: everything that lands on the shelf is your fault. You didn't write it. It's still your fault.", 7.4, color=FLAV)
    pennyless(c, x + AW - 48, y + 14, 0.5, 'point'); icon(c, 'coin', x + AW - 20, y + 60, 0.7)

# ------------------------------------------------------------ trackers
def track(c, x, y, title, sub, n, caps, last, note):
    c.setStrokeColor(LGREY); c.setLineWidth(0.3); c.setFillColor(white); c.rect(x, y, TW, TH, fill=1, stroke=1)
    c.setStrokeColor(black); c.setLineWidth(0.8); c.rect(x + 8, y + 8, TW - 16, TH - 16)
    head(c, title, x + 16, y + TH - 26, 12, anchor='l')
    c.setFont(MONO, 6.5); c.setFillColor(GREY); c.drawRightString(x + TW - 16, y + TH - 24, sub)
    bw = (TW - 40) / (n + 1); bh = 40; by = y + TH - 44 - bh
    for i in range(n + 1):
        bx = x + 20 + i * bw
        c.setFillColor(black if i == n else white); c.setStrokeColor(black); c.setLineWidth(1); c.rect(bx, by, bw, bh, fill=1, stroke=1)
        head(c, str(i), bx + bw / 2, by + bh - 18, 14, color=white if i == n else black)
        c.setFont(MONO, 5); c.setFillColor(white if i == n else GREY)
        for k, ln in enumerate(wrap(caps[i], MONO, 5, bw - 4)[:2]): c.drawCentredString(bx + bw / 2, by + 10 - k * 6, ln)
    c.setFont(MONO, 5.5); c.setFillColor(GREY); c.drawString(x + 20, by - 9, 'Clip a paperclip on the top edge, or park a spare house in the box.')
    yy = text_block(c, x + 20, by - 14, TW - 40, last, MONOB, 6.8, 1.2, black)
    text_block(c, x + 20, yy - 3, TW - 40, note, MONO, 6, 1.2, FLAV)
    # character / readiness slot
    c.setStrokeColor(LGREY); c.setLineWidth(0.5); c.setDash(2, 2); c.rect(x + TW - 96, y + 14, 80, 36, fill=0, stroke=1); c.setDash()
    c.setFont(MONO, 5); c.setFillColor(GREY); c.drawCentredString(x + TW - 56, y + 30, 'CHARACTER CARD' if n == 6 else 'READINESS CARD'); c.drawCentredString(x + TW - 56, y + 22, 'goes here')

def smoke_tracker(c, x, y):
    track(c, x, y, 'SMOKE', 'Corrective Training Log', 6,
          ['Squared away', 'Noticed', 'On the list', 'Counseled', 'Extra duty', 'Pending', 'CHAPTERED'],
          '6 = CHAPTERED: set to 0, discard your character, draw a new one blind. Keep all money and property.',
          '"+1 Smoke" raises yours. "Push +1" raises someone else\'s. Immunity blocks pushes, not your own.')

def complaint_tracker(c, x, y):
    track(c, x, y, 'COMMAND CLIMATE', 'Open Complaints, 1SG', 8,
          ['Green', 'A rumor', 'A survey', 'An email', 'A meeting', 'A memo', 'An inquiry', 'A phone call', 'RELIEVED'],
          '8 = RELIEF FOR CAUSE: the player with the most Smoke takes the chair, the bank, the decks and the shelf as it stands.',
          '+1 on every Building draw, Policy Letter, IG Complaint, or Walk-Back ruled against you. Resets to 0 for the new 1SG.')

# ------------------------------------------------------------ pads
def form_frame(c, x, y, w, h, num, title):
    c.setStrokeColor(LGREY); c.setLineWidth(0.3); c.setFillColor(white); c.rect(x, y, w, h, fill=1, stroke=1)
    c.setStrokeColor(black); c.setLineWidth(0.6); c.rect(x + 5, y + 5, w - 10, h - 10)
    c.setFillColor(white); c.rect(x + 5, y + h - 17, 44, 12, fill=1, stroke=1)
    c.setFont(MONOB, 4.5); c.setFillColor(black); c.drawCentredString(x + 27, y + h - 13, num)
    c.setFont(MONO, 3.8); c.setFillColor(GREY); c.drawRightString(x + w - 7, y + h - 13, 'For use of this form, see nobody.')
    c.setStrokeColor(black); c.setLineWidth(0.6); c.line(x + 5, y + h - 17, x + w - 5, y + h - 17)
    head(c, title, x + w / 2, y + h - 28, 7.2, maxw=w - 16)
    c.line(x + 5, y + h - 33, x + w - 5, y + h - 33)
    c.setFont(MONO, 3.8); c.setFillColor(GREY); c.drawRightString(x + w - 7, y + 7, 'Page 1 of 1')
    c.drawString(x + 7, y + 7, 'MONOPLATOON')

def field(c, x, y, w, label, boxh=0):
    c.setFont(MONO, 4.6); c.setFillColor(GREY); c.drawString(x, y, label)
    c.setStrokeColor(LGREY); c.setLineWidth(0.4)
    if boxh:
        c.rect(x, y - 3 - boxh, w, boxh, fill=0, stroke=1)
        return y - 3 - boxh - 7
    c.line(x + sw(label, MONO, 4.6) + 3, y - 1, x + w, y - 1)
    return y - 13

def f4856(c, x, y):
    form_frame(c, x, y, PW, PH, 'FORM 4856-ish', 'DEVELOPMENTAL COUNSELING')
    yy = y + PH - 44; w = PW - 20; lx = x + 10
    yy = field(c, lx, yy, w, 'Name / Rank:'); yy = field(c, lx, yy, w, 'Date:')
    yy = field(c, lx, yy, w, 'Purpose of counseling:', 26)
    yy = field(c, lx, yy, w, 'Key points:', 30)
    yy = field(c, lx, yy, w, 'Plan of action:', 16)
    yy = field(c, lx, yy, w, "Soldier's remarks:", 8)
    c.setFont(MONO, 4.4); c.setFillColor(GREY); c.drawString(lx, yy, 'I agree / disagree with this counseling.')
    c.drawString(lx, yy - 9, 'Initials: ____   1SG: ____')

def f31(c, x, y):
    form_frame(c, x, y, PW, PH, 'FORM 31-ish', 'REQUEST FOR LEAVE')
    yy = y + PH - 44; w = PW - 20; lx = x + 10
    yy = field(c, lx, yy, w, 'Name / Rank:')
    c.setFont(MONO, 4.6); c.setFillColor(GREY); c.drawString(lx, yy, 'Type of leave:')
    for i, t in enumerate(('Ordinary', 'Emergency', 'Whatever')):
        c.setStrokeColor(black); c.setLineWidth(0.5); c.rect(lx + i * 42, yy - 11, 5, 5, fill=0, stroke=1); c.drawString(lx + 8 + i * 42, yy - 10, t)
    yy -= 22
    yy = field(c, lx, yy, w, 'From:'); yy = field(c, lx, yy, w, 'To:'); yy = field(c, lx, yy, w, 'Reason:', 30)
    yy = field(c, lx, yy, w, 'Address while on leave:', 18)
    yy = field(c, lx, yy, w, 'Approving authority:')
    c.setFont(MONO, 4.4); c.setFillColor(GREY); c.drawString(lx, yy, 'Status: not available. Try next week.')
    c.drawString(lx, yy - 9, 'Charged days: all of them')

def fmfr(c, x, y):
    form_frame(c, x, y, PW, PH, 'MFR', 'MEMORANDUM FOR RECORD')
    yy = y + PH - 44; w = PW - 20; lx = x + 10
    c.setFont(MONOB, 4.8); c.setFillColor(black); c.drawString(lx, yy, 'MEMORANDUM FOR: Whoever'); yy -= 10
    yy = field(c, lx, yy, w, 'SUBJECT:')
    c.setStrokeColor(LGREY); c.setLineWidth(0.4)
    for i in range(10): c.line(lx, yy - i * 10, lx + w, yy - i * 10)
    yy -= 10 * 10 + 2
    c.setFont(MONO, 4.4); c.setFillColor(GREY); c.drawString(lx, yy, 'POC: the undersigned, who is leaving.')
    c.drawString(lx, yy - 9, 'Signed: ____________  1SG')
    c.setFont(MONO, 4); c.drawString(lx, yy - 18, 'Policy Letter: put this sheet on the shelf.')

def f2823(c, x, y):
    form_frame(c, x, y, PW, PH, 'FORM 2823-ish', 'SWORN STATEMENT')
    yy = y + PH - 44; w = PW - 20; lx = x + 10
    c.setFont(MONO, 4.6); c.setFillColor(GREY); c.drawString(lx, yy, 'I, ______________, want to make the'); c.drawString(lx, yy - 8, 'following statement under oath:'); yy -= 16
    c.setStrokeColor(LGREY); c.setLineWidth(0.4)
    for i in range(11): c.line(lx, yy - i * 10, lx + w, yy - i * 10)
    yy -= 11 * 10
    c.setFont(MONO, 4.4); c.drawString(lx, yy, 'I have read this statement.')
    c.line(lx, yy - 9, lx + w, yy - 9); c.drawString(lx, yy - 16, 'Witness (optional, also leaving): ______')

def frisk(c, x, y):
    form_frame(c, x, y, PW, PH, 'DRAW-WHATEVER', 'RISK ASSESSMENT')
    yy = y + PH - 46; lx = x + 10; w = PW - 20
    yy = field(c, lx, yy, w, 'Activity:')
    c.setStrokeColor(black); c.setLineWidth(0.8); c.rect(lx, yy - 20, 12, 12, fill=0, stroke=1)
    c.setFont(MONOB, 7); c.setFillColor(black); c.drawString(lx + 18, yy - 17, 'Risk: accepted')
    yy -= 36
    c.setFont(MONO, 4.6); c.setFillColor(GREY)
    for i, t in enumerate(('Hazard identified: yes', 'Hazard mitigated: see above', 'Residual risk: ambient')):
        c.drawString(lx, yy - i * 10, t)
    yy -= 40
    yy = field(c, lx, yy, w, 'Approved by:'); yy = field(c, lx, yy, w, 'Date:')
    c.setFont(MONO, 4.6); c.setFillColor(GREY); c.drawString(lx, yy, 'Reviewed: annually, by nobody')
    icon(c, 'belt', lx + w / 2, yy - 28, 1.3)

def pad_pages(c, draw, name, note):
    per = 12
    for pi in range(3):
        heading(c, 'Pad: ' + name + ', sheet %d of 3' % (pi + 1), note)
        for i in range(per):
            r, k = divmod(i, 4)
            x = (W - 4 * PW) / 2 + k * PW; y = H - 1.1 * IN - (r + 1) * PH
            draw(c, x, y); cutmarks(c, x, y, PW, PH)
        footer(c, 'Phase 4: pads, ' + name); c.showPage()

def policy_pad_page(c, pi):
    heading(c, 'Pad: Policy Letter, sheet %d of 3' % (pi + 1), 'Card size, 2 1/8 x 3 3/16 in, so it sits on the Policy Shelf. 27 sheets; pad-glue the top edge.')
    for i in range(9):
        r, k = divmod(i, 3)
        x = (W - 3 * CW) / 2 + k * CW; y = H - 1.1 * IN - (r + 1) * CH
        c.setStrokeColor(LGREY); c.setLineWidth(0.3); c.setFillColor(white); c.rect(x, y, CW, CH, fill=1, stroke=1)
        c.setStrokeColor(black); c.setLineWidth(0.8); c.rect(x + 6, y + 6, CW - 12, CH - 12)
        c.setFillColor(black); c.rect(x + 6, y + CH - 26, CW - 12, 20, fill=1, stroke=1)
        head(c, 'POLICY LETTER', x + CW / 2, y + CH - 20.5, 8.5, color=white)
        c.setFont(MONO, 5); c.setFillColor(GREY); c.drawString(x + 10, y + CH - 34, 'LOCAL POLICY, 1SG. Archives first.')
        c.setFont(MONOB, 6.5); c.setFillColor(black); c.drawString(x + 12, y + CH - 48, 'MEMORANDUM FOR: Everyone')
        c.setFont(MONO, 6.5); c.drawString(x + 12, y + CH - 60, 'SUBJECT: ____________________')
        c.setStrokeColor(LGREY); c.setLineWidth(0.5)
        for i2 in range(9): c.line(x + 12, y + CH - 78 - i2 * 13, x + CW - 12, y + CH - 78 - i2 * 13)
        c.setFont(MONO, 5.5); c.setFillColor(GREY); c.drawString(x + 12, y + 34, 'POC: the undersigned, who is leaving.')
        c.drawString(x + 12, y + 24, 'Signed: ________________  1SG')
        c.setFont(MONO, 4.8); c.drawCentredString(x + CW / 2, y + 12, 'Walk-Backs hit this first. Enjoy.')
        cutmarks(c, x, y, CW, CH)
    footer(c, 'Phase 4: pads, Policy Letter'); c.showPage()

if __name__ == '__main__':
    c = canvas.Canvas(OUT, pagesize=letter); c.setTitle('MONOPLATOON - Phase 4: table pieces')
    # aids: 1 sergeant + 5 soldier, two per page
    aids = [sergeant_aid] + [regular_aid] * 5
    for pi in range(0, 6, 2):
        heading(c, 'Player aids, true size (6 x 4 in postcards), sheet %d of 3' % (pi // 2 + 1), 'Goldenrod 65 lb cardstock, single-sided. One First Sergeant aid, five Soldier aids.')
        for j, fn in enumerate(aids[pi:pi + 2]):
            x = (W - AW) / 2; y = H - 1.1 * IN - (j + 1) * AH - j * 14
            fn(c, x, y); cutmarks(c, x, y, AW, AH)
        footer(c, 'Phase 4: player aids'); c.showPage()
    # trackers: 6 smoke + 1 complaint, three per page
    trackers = [smoke_tracker] * 6 + [complaint_tracker]
    for pi in range(0, 7, 3):
        heading(c, 'Trackers, true size (5 x 3 in), sheet %d of 3' % (pi // 3 + 1), 'Goldenrod 65 lb cardstock, single-sided. Six Smoke trackers and one Command Climate tracker for the 1SG.')
        for j, fn in enumerate(trackers[pi:pi + 3]):
            x = (W - TW) / 2; y = H - 1.1 * IN - (j + 1) * TH - j * 10
            fn(c, x, y); cutmarks(c, x, y, TW, TH)
        footer(c, 'Phase 4: trackers'); c.showPage()
    # pads
    note = '2 x 3 in sheets on plain 20 lb paper, 36 per pad. Stack, clamp, and brush pad glue (or PVA) on the top edge.'
    pad_pages(c, f4856, 'Form 4856-ish, Developmental Counseling', note)
    pad_pages(c, f31, 'Form 31-ish, Leave Request', note)
    pad_pages(c, fmfr, 'Memorandum for Record', note)
    pad_pages(c, f2823, 'Form 2823-ish, Sworn Statement', note)
    pad_pages(c, frisk, 'Risk Assessment (optional)', note)
    for pi in range(3): policy_pad_page(c, pi)
    c.save(); print('ok')
