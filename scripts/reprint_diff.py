#!/usr/bin/env python3
"""Work out the minimum reprint between two releases.

    python scripts/reprint_diff.py OLD_DIR NEW_DIR --old-version 0.1.0 --new-version 0.1.1 [--zip PACKAGE.zip]

Compares every print file page by page (pixels and text, ignoring the version stamp in the
footer) and writes into NEW_DIR:

    REPRINT-since-v<old>.md                       which pages to reprint, on which paper
    Monoplatoon-v<new>-reprint-since-v<old>.pdf   only those pages, in print order

Rules:
  * The rulebook is one object: any change means reprint the whole rulebook.
  * Double-sided sheets reprint as a pair: if a front or its back changed, both come along.
  * The combined print set is skipped (it is the other files glued together).
  * A file that is new, or whose page count changed, is reprinted in full.

With --zip, both outputs are also added to the print package.
Exit code is always 0; "nothing changed" is a valid answer.
"""
import argparse
import os
import sys
import zipfile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(os.path.dirname(HERE), 'src'))
from compare_builds import norm_text, render, footer_mask  # noqa: E402

from PIL import Image, ImageChops, ImageDraw  # noqa: E402
from pypdf import PdfReader, PdfWriter  # noqa: E402

IN = 72.0
PAGE_W, PAGE_H = 612.0, 792.0


CARD_SHEETS = ('Monoplatoon_Phase2_Decks.pdf', 'Monoplatoon_Phase3_Characters_and_Deeds.pdf')


def card_layout(name):
    """(cards on the sheet, is it a back) for every page of a card file, in page order."""
    import data
    if name == 'Monoplatoon_Phase2_Decks.pdf':
        decks = [(len(data.GUIDANCE), False), (len(data.LAWYER), False), (len(data.BUILDING), True)]
    else:
        people = len(data.CHARACTERS) + 1 + len(data.READINESS)
        deeds = sum(1 for sp in data.BOARD if sp[2] in data.GROUP_NAME)
        decks = [(people, True), (deeds, False)]
    pages = []
    for n, double in decks:
        while n > 0:
            here = min(9, n)
            pages.append((here, False))
            if double:
                pages.append((here, True))
            n -= here
    return pages


def piece_regions(name, page):
    """Where the cut-out pieces sit on a page, as (left, top, right, bottom) in points from the top-left.
    Titles, paper notes, the sticker placement key and footers live outside these and are trimmed
    off, so changes there never trigger a reprint."""
    if name in CARD_SHEETS:
        import cards
        count, back = card_layout(name)[page - 1]
        out = []
        for i in range(count):   # only slots that hold a card; empty slots are scrap
            r, k = divmod(i, cards.COLS)
            if back:
                k = cards.COLS - 1 - k
            x, y = cards.slot(r * cards.COLS + k)
            top = PAGE_H - (y + cards.CH)
            out.append((x + 3, top + 3, x + cards.CW - 3, top + cards.CH - 3))   # inside the cut line
        return out
    if name == 'Monoplatoon_Phase1_Board_Stickers.pdf' and page <= 3:
        import phase1
        n = min(phase1.STD_PER_SHEET, len(phase1.STD) - (page - 1) * phase1.STD_PER_SHEET)
        out = []
        for i in range(n):
            x, y = phase1.std_cell(i)
            top = PAGE_H - (y + phase1.SH)
            out.append((x + 3, top + 3, x + phase1.SW - 3, top + phase1.SH - 3))
        return out
    if name == 'Monoplatoon_Phase1_Board_Stickers.pdf' and page == 5:
        import phase1
        return [(0.42 * IN - 4, 1.15 * IN - 4, 0.42 * IN + 2 * phase1.CS + 12, 1.15 * IN + 2 * phase1.CS + 12)]   # corners, not the key
    if name == 'Monoplatoon_Phase5_Rulebook.pdf':
        return [(0, 0, PAGE_W, PAGE_H - 0.5 * IN)]
    return [(0, 0.75 * IN, PAGE_W, PAGE_H - 0.5 * IN)]   # below the page title, above the footer


def keep_regions(img, regions):
    """White out everything outside the piece regions."""
    s = img.width / PAGE_W
    mask = Image.new('L', img.size, 0)
    d = ImageDraw.Draw(mask)
    for l, t, r, b in regions:
        d.rectangle([int(l * s), int(t * s), int(r * s), int(b * s)], fill=255)
    white = Image.new(img.mode, img.size, 255)
    return Image.composite(img, white, mask)

# Print order, the paper for each page range, and which pages are the two sides of one sheet.
PRINT_FILES = [
    ('Monoplatoon_Phase5_Rulebook.pdf', 'Rulebook', [((1, 99), 'plain 20 lb')], [], True),
    ('Monoplatoon_Phase1_Board_Stickers.pdf', 'Board stickers', [((1, 99), 'matte sticker paper')], [], False),
    ('Monoplatoon_Phase2_Decks.pdf', 'Decks', [((1, 2), 'pale green 65 lb, single-sided'), ((3, 4), 'buff 65 lb, single-sided'),
                                              ((5, 99), 'grey 65 lb, double-sided (flip on long edge)')], [(5, 6), (7, 8)], False),
    ('Monoplatoon_Phase3_Characters_and_Deeds.pdf', 'Characters and deeds', [((1, 6), 'white 65 lb, double-sided (flip on long edge)'),
                                                                             ((7, 99), 'white 65 lb, single-sided')], [(1, 2), (3, 4), (5, 6)], False),
    ('Monoplatoon_Phase4_Table_Pieces.pdf', 'Table pieces', [((1, 6), 'goldenrod 65 lb, single-sided'), ((7, 99), 'plain 20 lb (pads)')], [], False),
]


def paper_for(ranges, page):
    for (a, b), paper in ranges:
        if a <= page <= b:
            return paper
    return ranges[-1][1]


def page_title(text):
    for line in (text or '').splitlines():
        line = line.strip()
        if line:
            return line[:70]
    return ''


def changed_pages(old, new, dpi=100):
    """Pages of NEW whose printed pieces look different from OLD. None means the whole file
    (new, or its page count changed). Judged on rendered pixels inside the piece regions, because
    what matters is what lands on the paper you keep."""
    if not os.path.exists(old):
        return None
    ro, rn = PdfReader(old), PdfReader(new)
    if len(ro.pages) != len(rn.pages):
        return None
    name = os.path.basename(new)
    out = {}
    io, inn = render(old, dpi), render(new, dpi)
    for i in range(len(rn.pages)):
        hit = []
        for reg in piece_regions(name, i + 1):
            a, b = keep_regions(io[i], [reg]), keep_regions(inn[i], [reg])
            if a.size != b.size or ImageChops.difference(a, b).point(lambda v: 255 if v > 40 else 0).getbbox():
                hit.append(reg)
        if hit:
            out[i + 1] = hit
    return out


def known_names():
    import data
    names = [sp[1] for sp in data.BOARD if sp[2] != 'deck']
    names += [c[0] for c in data.GUIDANCE + data.LAWYER] + [c[1] for c in data.BUILDING]
    names += [c[0] for c in data.CHARACTERS] + ['FIRST SERGEANT'] + data.READINESS
    return sorted(set(names), key=len, reverse=True)


def name_pieces(path, page, regions):
    """Name what sits in each changed region, from the text printed there."""
    import re
    import pdfplumber
    names = known_names()
    found = []
    with pdfplumber.open(path) as pdf:
        pg = pdf.pages[page - 1]
        for l, t, r, b in regions:
            txt = re.sub(r'\s+', ' ', pg.crop((max(0, l), max(0, t), min(pg.width, r), min(pg.height, b))).extract_text() or '').lower()
            hit = next((n for n in names if re.sub(r'\s+', ' ', n).lower()[:40] in txt), None)
            found.append(hit or 'card back' if not txt.strip() or 'personnel file' in txt or 'effective immediately, until' in txt else hit)
    return [f for f in found if f]


def runs(pages):
    pages = sorted(pages)
    out, start, prev = [], None, None
    for p in pages:
        if start is None:
            start = prev = p
        elif p == prev + 1:
            prev = p
        else:
            out.append((start, prev)); start = prev = p
    if start is not None:
        out.append((start, prev))
    return ', '.join(str(a) if a == b else '%d-%d' % (a, b) for a, b in out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('old'); ap.add_argument('new')
    ap.add_argument('--old-version', required=True)
    ap.add_argument('--new-version', required=True)
    ap.add_argument('--zip', help='add the guide and reprint PDF to this print package')
    a = ap.parse_args()

    guide = os.path.join(a.new, 'REPRINT-since-v%s.md' % a.old_version)
    pdf_out = os.path.join(a.new, 'Monoplatoon-v%s-reprint-since-v%s.pdf' % (a.new_version, a.old_version))
    writer = PdfWriter()
    rows, unchanged, n_out = [], [], 0

    for name, label, ranges, pairs, whole in PRINT_FILES:
        newp = os.path.join(a.new, name)
        if not os.path.exists(newp):
            continue
        total = len(PdfReader(newp).pages)
        changed = changed_pages(os.path.join(a.old, name), newp)
        if changed is None:
            pages, why, pieces = set(range(1, total + 1)), 'new or re-paginated: reprint all', {}
        else:
            pages, why = set(changed), ''
            pieces = {p: name_pieces(newp, p, regs) for p, regs in changed.items()}
        if pages and whole:
            pages, why = set(range(1, total + 1)), 'changed: the rulebook is reprinted whole'
        for f, b in pairs:   # never half a sheet
            if f in pages or b in pages:
                pages |= {f, b}
        if not pages:
            unchanged.append(label)
            continue
        reader = PdfReader(newp)
        titles = {p: page_title(reader.pages[p - 1].extract_text()) for p in pages}
        # group consecutive pages that share a paper so the table reads as print jobs
        groups = []
        for p in sorted(pages):
            paper = paper_for(ranges, p)
            if groups and groups[-1][1] == paper and groups[-1][0][-1] == p - 1:
                groups[-1][0].append(p)
            else:
                groups.append(([p], paper))
        for plist, paper in groups:
            start = n_out + 1
            for p in plist:
                writer.add_page(reader.pages[p - 1]); n_out += 1
            named = []
            for p in plist:
                for n in pieces.get(p, []):
                    if n not in named:
                        named.append(n)
            if not named:
                named = [titles[p] for p in plist if p in pieces] or ['other side of a changed sheet']
            what = ', '.join(named)[:200]
            rows.append((label, runs(plist), paper, runs(range(start, n_out + 1)), why or what))

    lines = ['## Reprint guide: v%s since v%s' % (a.new_version, a.old_version), '']
    if not rows:
        lines += ['Nothing printable changed since v%s. Keep what you have.' % a.old_version]
    else:
        lines += ['Already printed v%s? Print only these %d page%s from `%s`, on the paper listed. '
                  'Everything else is unchanged.' % (a.old_version, n_out, '' if n_out == 1 else 's', os.path.basename(pdf_out)), '',
                  '| Item | Its pages | Paper | Reprint PDF pages | What changed |', '| --- | --- | --- | --- | --- |']
        lines += ['| %s | %s | %s | %s | %s |' % r for r in rows]
        if unchanged:
            lines += ['', 'No changes: %s.' % ', '.join(unchanged)]
        lines += ['', 'Only changes to the pieces you cut out count; titles, paper notes and footers in the trimmed margins do not. '
                  'Double-sided sheets are listed as front and back together. The rulebook is always reprinted whole.']
    text = '\n'.join(lines) + '\n'
    open(guide, 'w').write(text)
    if n_out:
        writer.add_metadata({'/Title': 'MONOPLATOON v%s - reprint since v%s' % (a.new_version, a.old_version)})
        with open(pdf_out, 'wb') as fh:
            writer.write(fh)
    if a.zip:
        folder = os.path.splitext(os.path.basename(a.zip))[0].replace('-print', '')
        with zipfile.ZipFile(a.zip, 'a', zipfile.ZIP_DEFLATED) as z:
            z.write(guide, folder + '/' + os.path.basename(guide))
            if n_out:
                z.write(pdf_out, folder + '/' + os.path.basename(pdf_out))
    print(text)


if __name__ == '__main__':
    main()
