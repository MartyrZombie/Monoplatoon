#!/usr/bin/env python3
"""Build every MONOPLATOON print file into dist/, plus one combined PDF and a zip package.

    python build.py            # build everything
    python build.py 2 4        # build only phases 2 and 4 (no combined PDF or zip)

Output folder can be changed with the MONOPLATOON_OUT environment variable.
"""
import os
import runpy
import sys
import zipfile

ROOT = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)

from mp import OUT_DIR, VERSION  # noqa: E402  (after sys.path tweak)

PHASES = {
    1: ('phase1.py', 'Monoplatoon_Phase1_Board_Stickers.pdf'),
    2: ('phase2.py', 'Monoplatoon_Phase2_Decks.pdf'),
    3: ('phase3.py', 'Monoplatoon_Phase3_Characters_and_Deeds.pdf'),
    4: ('phase4.py', 'Monoplatoon_Phase4_Table_Pieces.pdf'),
    5: ('phase5.py', 'Monoplatoon_Phase5_Rulebook.pdf'),
}
# Rulebook first in the combined file, then the rest in print order.
COMBINED_ORDER = [5, 1, 2, 3, 4]

PRINT_README = """MONOPLATOON v{v} -- print package
=====================================

Print every file on ordinary portrait letter (8.5 x 11 in) paper at 100% /
Actual size. Never "fit to page". Mirrored back sheets assume you flip on the
long edge.

File                                          Paper                  Notes
--------------------------------------------  ---------------------  -----------------------------------------
Monoplatoon_Phase5_Rulebook.pdf               plain 20 lb            Read this first. Has the full checklist.
Monoplatoon_Phase1_Board_Stickers.pdf         matte sticker paper    Mint backing. Bar A, bar B, then mascot.
Monoplatoon_Phase2_Decks.pdf  pages 1-2       pale green 65 lb       Command Guidance, single-sided, black ink.
                              pages 3-4       buff / manila 65 lb    Barracks Lawyer, single-sided, black ink.
                              pages 5-8       grey 65 lb             The Building: front, flip, back.
Monoplatoon_Phase3_Characters_and_Deeds.pdf   white 65 lb            Characters front/back x3, then deeds.
Monoplatoon_Phase4_Table_Pieces.pdf pp 1-6    goldenrod 65 lb        Player aids and trackers, single-sided.
                                    pp 7-24   plain 20 lb            Pads: cut, stack, clamp, pad-glue the top.

Monoplatoon_Complete_Print_Set.pdf is all of the above in one file, in the
order listed, if you would rather send a single job to a print shop.

Uses the board, money, houses, hotels, dice and tokens from a US classic
Monopoly set. All characters are invented. No real people appear.
"""


def build_phase(n):
    script, name = PHASES[n]
    print('[phase %d] %s' % (n, script), flush=True)
    runpy.run_path(os.path.join(SRC, script), run_name='__main__')
    path = os.path.join(OUT_DIR, name)
    if not os.path.exists(path):
        raise SystemExit('phase %d did not produce %s' % (n, path))
    return path


def combine(paths):
    from pypdf import PdfWriter
    out = os.path.join(OUT_DIR, 'Monoplatoon_Complete_Print_Set.pdf')
    w = PdfWriter()
    for p in paths:
        w.append(p)
    w.add_metadata({'/Title': 'MONOPLATOON v%s - Complete Print Set' % VERSION})
    with open(out, 'wb') as fh:
        w.write(fh)
    return out


def package(files):
    name = 'Monoplatoon-v%s-print.zip' % VERSION
    out = os.path.join(OUT_DIR, name)
    folder = 'Monoplatoon-v%s' % VERSION
    with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
        z.writestr(folder + '/README-PRINT.txt', PRINT_README.format(v=VERSION))
        for f in files:
            z.write(f, folder + '/' + os.path.basename(f))
    return out


def main(argv):
    wanted = [int(a) for a in argv] or sorted(PHASES)
    built = {n: build_phase(n) for n in wanted}
    if argv:
        return
    combined = combine([built[n] for n in COMBINED_ORDER])
    zipped = package([built[n] for n in COMBINED_ORDER] + [combined])
    print('\nVersion %s' % VERSION)
    for p in [built[n] for n in COMBINED_ORDER] + [combined, zipped]:
        print('  %-50s %7.1f KB' % (os.path.basename(p), os.path.getsize(p) / 1024))


if __name__ == '__main__':
    main(sys.argv[1:])
