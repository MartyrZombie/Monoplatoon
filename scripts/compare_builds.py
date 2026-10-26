#!/usr/bin/env python3
"""Compare two folders of MONOPLATOON PDFs page by page.

    python scripts/compare_builds.py OLD_DIR NEW_DIR [--dpi 50] [--report out.md] [--diffs DIFF_DIR]

For every PDF present in both folders it checks:
  * page count and page size
  * extracted text per page (the version stamp in footers is ignored)
  * rendered pixels per page: share of pixels that changed, and where

Exit code is 0 when nothing differs beyond the version stamp, 1 otherwise.
Needs: pypdf, pypdfium2, Pillow.
"""
import argparse
import difflib
import os
import re
import sys

import pypdfium2 as pdfium
from PIL import Image, ImageChops
from pypdf import PdfReader

VERSION_RE = re.compile(r'MONOPLATOON v[0-9A-Za-z.\-]+')


def norm_text(t):
    t = VERSION_RE.sub('MONOPLATOON', t or '')
    return '\n'.join(line.rstrip() for line in t.splitlines() if line.strip())


def render(path, dpi):
    doc = pdfium.PdfDocument(path)
    out = [doc[i].render(scale=dpi / 72).to_pil().convert('L') for i in range(len(doc))]
    doc.close()
    return out


def footer_mask(img):
    """Blank the bottom 0.5 in, where the footer carries the version stamp."""
    from PIL import ImageDraw
    img = img.copy()
    cut = int(img.height * 0.5 / 11)
    ImageDraw.Draw(img).rectangle([0, img.height - cut, img.width, img.height], fill=255)
    return img


def compare_file(a, b, dpi, diff_dir):
    lines, changed = [], False
    ra, rb = PdfReader(a), PdfReader(b)
    na, nb = len(ra.pages), len(rb.pages)
    if na != nb:
        lines.append('- **Page count** %d -> %d' % (na, nb)); changed = True
    for i in range(min(na, nb)):
        sa = tuple(round(float(v), 1) for v in ra.pages[i].mediabox[2:])
        sb = tuple(round(float(v), 1) for v in rb.pages[i].mediabox[2:])
        if sa != sb:
            lines.append('- p%d **page size** %s -> %s' % (i + 1, sa, sb)); changed = True
        ta, tb = norm_text(ra.pages[i].extract_text()), norm_text(rb.pages[i].extract_text())
        if ta != tb:
            changed = True
            d = [l for l in difflib.unified_diff(ta.splitlines(), tb.splitlines(), lineterm='', n=0) if not l.startswith(('---', '+++', '@@'))]
            lines.append('- p%d **text** differs (%d lines): %s' % (i + 1, len(d), '; '.join(d[:4])[:300]))
    ia, ib = render(a, dpi), render(b, dpi)
    worst = 0.0
    for i in range(min(len(ia), len(ib))):
        pa, pb = footer_mask(ia[i]), footer_mask(ib[i])
        if pa.size != pb.size:
            continue
        diff = ImageChops.difference(pa, pb).point(lambda v: 255 if v > 40 else 0)
        n = diff.histogram()[255]
        share = n / (diff.width * diff.height)
        worst = max(worst, share)
        if n:
            changed = True
            box = diff.getbbox()
            bx = tuple(round(v / dpi, 2) for v in box)
            lines.append('- p%d **pixels** %.3f%% changed, region %s in' % (i + 1, share * 100, bx))
            if diff_dir:
                os.makedirs(diff_dir, exist_ok=True)
                side = Image.new('L', (pa.width * 3, pa.height), 255)
                side.paste(pa, (0, 0)); side.paste(pb, (pa.width, 0)); side.paste(ImageChops.invert(diff), (pa.width * 2, 0))
                side.save(os.path.join(diff_dir, '%s_p%02d.png' % (os.path.splitext(os.path.basename(a))[0], i + 1)))
    return changed, lines, na, nb, worst


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('old'); ap.add_argument('new')
    ap.add_argument('--dpi', type=int, default=50)
    ap.add_argument('--report')
    ap.add_argument('--diffs', help='write side-by-side diff images here')
    a = ap.parse_args()
    names = sorted(f for f in os.listdir(a.old) if f.endswith('.pdf'))
    out = ['# Build comparison', '', 'Old: `%s`  ' % a.old, 'New: `%s`' % a.new, '',
           '| File | Pages old -> new | Max pixel change | Result |', '| --- | --- | --- | --- |']
    detail, any_change = [], False
    for n in names:
        nb = os.path.join(a.new, n)
        if not os.path.exists(nb):
            out.append('| %s | missing in new | | **MISSING** |' % n); any_change = True; continue
        changed, lines, pa, pb, worst = compare_file(os.path.join(a.old, n), nb, a.dpi, a.diffs)
        any_change |= changed
        out.append('| %s | %d -> %d | %.3f%% | %s |' % (n, pa, pb, worst * 100, '**differs**' if changed else 'identical'))
        if lines:
            detail += ['', '### ' + n] + lines
    for n in sorted(f for f in os.listdir(a.new) if f.endswith('.pdf') and f not in names):
        out.append('| %s | new file | | added |' % n)
    out += detail
    out += ['', 'Footers are excluded from the pixel check and version stamps from the text check.']
    text = '\n'.join(out)
    print(text)
    if a.report:
        open(a.report, 'w').write(text + '\n')
    sys.exit(1 if any_change else 0)


if __name__ == '__main__':
    main()
