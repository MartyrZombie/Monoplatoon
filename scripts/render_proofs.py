#!/usr/bin/env python3
"""Render built PDFs to PNG proofs for a by-eye review.

    python scripts/render_proofs.py                  # every PDF in dist/ -> dist/proofs/
    python scripts/render_proofs.py dist/Monoplatoon_Phase2_Decks.pdf --pages 1-3 --dpi 100

The quality check catches what a script can; this is for the rest: does the art read,
does the joke land, does a sticker look right next to the real board.
"""
import argparse
import os
import sys

import pypdfium2 as pdfium

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def parse_pages(spec, n):
    if not spec:
        return list(range(1, n + 1))
    out = []
    for part in spec.split(','):
        a, _, b = part.partition('-')
        out += list(range(int(a), int(b or a) + 1))
    return [p for p in out if 1 <= p <= n]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('pdfs', nargs='*', help='PDFs to render (default: every PDF in dist/)')
    ap.add_argument('--pages', help='e.g. 1-3,7')
    ap.add_argument('--dpi', type=int, default=80)
    ap.add_argument('--out', default=os.path.join(ROOT, 'dist', 'proofs'))
    a = ap.parse_args()
    pdfs = a.pdfs or sorted(os.path.join(ROOT, 'dist', f) for f in os.listdir(os.path.join(ROOT, 'dist'))
                            if f.endswith('.pdf') and 'Complete' not in f and 'reprint' not in f)
    os.makedirs(a.out, exist_ok=True)
    for path in pdfs:
        doc = pdfium.PdfDocument(path)
        stem = os.path.splitext(os.path.basename(path))[0]
        for p in parse_pages(a.pages, len(doc)):
            png = os.path.join(a.out, '%s_p%02d.png' % (stem, p))
            doc[p - 1].render(scale=a.dpi / 72).to_pil().save(png)
            print(png)
        doc.close()


if __name__ == '__main__':
    sys.exit(main())
