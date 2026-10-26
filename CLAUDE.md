# CLAUDE.md

MONOPLATOON is a print-and-play re-theme of a US classic Monopoly set as the modern enlisted US Army. This repo generates every printed piece as PDFs from Python (reportlab). There is no app; the product is paper.

## Commands

```sh
pip install -r requirements-qa.txt              # build + QA tools (requirements.txt is build only)
python build.py                                 # all PDFs, combined set, versioned zip -> dist/
python build.py 2                               # one phase only (here: the decks)
python scripts/quality_check.py                 # self-test + source + dist/ PDFs; must end in PASS
python scripts/render_proofs.py --pages 1-2     # PNG proofs in dist/proofs/ to look at
python scripts/compare_builds.py OLD NEW        # page-by-page diff of two builds (text + pixels)
python scripts/reprint_diff.py OLD NEW --old-version X --new-version Y   # minimal reprint list
```

Set `MONOPLATOON_OUT` to build somewhere other than `dist/`.

## Layout

| Path | What |
| --- | --- |
| `src/data.py` | **All game text**: board, rent tables, characters, three decks, Readiness, glossary. Word changes go here. |
| `src/mp.py` | Fonts, colours, text fitting, page heading/footer, the mascot and Building characters, ~50 spot icons |
| `src/cards.py` | Card sheet geometry (3x3, 2 1/8 x 3 3/16 in), mirrored-back slots, sheet heading |
| `src/phase1.py` | Board stickers (36 spaces, corners, deck labels, title bar, mascot piece, maker's mark) |
| `src/phase2.py` | Command Guidance, Barracks Lawyer, The Building |
| `src/phase3.py` | Characters, First Sergeant role, Readiness, deeds |
| `src/phase4.py` | Player aids, trackers, form pads, Policy Letter pad |
| `src/phase5.py` | Rulebook (rules, characters table, add-ons, glossary, print checklist) |
| `scripts/` | Quality check, build comparison, reprint diff, proof renderer |
| `docs/DESIGN_BRIEF.md` | Every dimension, stock and colour |

## Branches and releases

- Work on `develop`. Only `develop` merges into `main` (CI enforces it).
- Every push to `develop` or `main` runs **CI** (build + proof artifact) and **Quality check**.
- A merge into `main` runs **Release print package**: build, QA (blocks on error), reprint diff against the previous release, GitHub Release `v<VERSION>`, and GitHub Packages `ghcr.io/martyrzombie/monoplatoon-print`.
- Any change to what gets printed needs a `VERSION` bump (semver: content = minor, fixes = patch) and a `CHANGELOG.md` section, which becomes the release notes.
- To test a release without publishing: run the *Release print package* workflow by hand on `develop` (publish left off).

## Design rules

These were agreed with the owner. The QA script enforces everything marked **(QA)**; the rest needs your eyes.

**Tone**
- The joke is always the machine: pay, barracks, policy, budgets, paperwork, the chain of command. Never the soldier, their family, or anyone a soldier would be ashamed to laugh at.
- Policy gags stay procedural (renames, memos, forms, lab fees). Never a policy that hurt real people.
- No real people anywhere, not even mentioned in a joke. The Secretary (Brock Lethality) and the Commander-in-Chief (a hand and a phone) are invented. **(QA: denylist of real names)**
- Every term of art gets a straight-faced one-line gloss, and every gloss term is in `GLOSSARY`, alphabetized. **(QA)**
- No emoji or decorative symbols. "Flair" means professional colour, layout and type. **(QA)**

**Game**
- Board layout and prices are stock Monopoly; property groups climb a ladder from Reception to The Building. **(QA)**
- Command Guidance and Barracks Lawyer match Chance and Community Chest card for card in effect and amount. **(QA)**
- The Building: 7 Directives, 4 Walk-Backs, 4 Paperwork, 3 Uniform Changes; Paperwork names its Step-token action. **(QA)**
- 10 to 12 characters, invented names with a real rank prefix, one rule each with a flavor line and gloss. **(QA)**
- Rule numbers must agree between the rulebook and the player aids: auctions open at $10, IG Complaint $50, Inspection $20 a piece, $500 stipend, Smoke 6, relief at 8 Complaints, $500 at 10:00, $1,500 start. **(QA)**
- Nobody is eliminated; 3 to 6 players; 90-minute clock. **(QA)**

**Production** (see `docs/DESIGN_BRIEF.md`)
- Stickers on mint `#BFDDC8`: spaces 1 5/8 x 2 9/16 in, corners 2 9/16 in, bar 11.6 x 2.5 in, mascot piece 4.15 x 2.4 in, deck labels 3.45 x 2.3 in, maker's mark 1.7 x 1 in. These were fit-tested on the real board; never change them casually. **(QA)**
- Cards 2 1/8 x 3 3/16 in, nine per letter page, 100% scale. Aids 6 x 4, trackers 5 x 3, pads 2 x 3 in. **(QA)**
- Command Guidance and Barracks Lawyer are single-sided, black ink only, on coloured stock. **(QA)**
- Double-sided sheets (The Building, characters) have backs mirrored left-to-right for a long-edge flip. **(QA)**
- Deeds print their purchase price (net worth is tallied from deeds). **(QA)**
- Headlines DejaVu Sans Condensed (bundled in `fonts/`, embedded in every PDF); body Courier. Rules black, flavor/gloss `#555555`. **(QA)**
- Nothing may overlap, run off the page, or spill out of a card. **(QA)**
- All art is original, drawn in code. Never Hasbro's artwork, logo or mascot (Rich Uncle Pennybags / Mr. Monopoly). **(QA: names only)**
- Player aids are postcard-brief; trackers are separate cards from the aids.
- Paper notes and titles belong in the trimmed margins, never under or over a piece.

## How to work here

1. Change text in `src/data.py`, layout in the phase scripts. Keep geometry in named constants; `scripts/reprint_diff.py` imports `cards.slot`, `phase1.std_cell` and friends to know where the pieces are.
2. `python build.py && python scripts/quality_check.py`. Fix every error; do not loosen a check to get a pass. If a check is wrong, fix the check and say why in the commit.
3. Render the pages you touched with `scripts/render_proofs.py` and look at them. Text fitting is automatic (`fit_block`, `fit_size`) and will shrink type silently, so check that nothing became unreadably small.
4. If page counts change, update `PAGES` in `scripts/quality_check.py`, the paper ranges in `scripts/reprint_diff.py`, and `README-PRINT` in `build.py`.
5. New rule or card type? Add a check to `scripts/quality_check.py` in the same change.
6. Commit to `develop`. Release by bumping `VERSION`, adding the changelog section, and opening a PR into `main`.
