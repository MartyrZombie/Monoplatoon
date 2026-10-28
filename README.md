# MONOPLATOON

**Hurry up and wait.**

A print-and-play re-theme of Monopoly as the modern enlisted US Army. You climb from a moldy barracks to the Pentagon while the pay system, the chain of command and Congress change the rules faster than the game can print them. Satire aimed at the machine, never the soldier.

- 3 to 6 players, about 90 minutes on a hard clock, nobody is eliminated
- One player is the **First Sergeant**: runs the bank, collects every fine, writes local policy, and gets relieved for cause if the complaints pile up
- A **Policy Shelf** fills with Directives, Walk-Backs, Paperwork and Uniform Changes from the Secretary and the Commander-in-Chief, and a real box of uniform bits gets pinned to your shirt
- Every space, card and character has a joke and a straight-faced one-line gloss; the glossary is at the back of the rulebook

## Get the print files

Download the latest **`Monoplatoon-vX.Y.Z-print.zip`** from [Releases](../../releases). It holds every PDF plus `README-PRINT.txt`, which says which paper each file goes on. The same zip is published to [GitHub Packages](../../pkgs/container/monoplatoon-print).

| File | Paper | What it is |
| --- | --- | --- |
| `Monoplatoon_Phase5_Rulebook.pdf` | plain 20 lb | Rules, glossary, print checklist. Read first. |
| `Monoplatoon_Phase1_Board_Stickers.pdf` | matte sticker paper | All 40 spaces, deck labels, centre title bar, mascot piece, maker's mark |
| `Monoplatoon_Phase2_Decks.pdf` | pale green, buff, grey 65 lb | Command Guidance and Barracks Lawyer (single-sided, black ink), The Building (colour, mirrored backs) |
| `Monoplatoon_Phase3_Characters_and_Deeds.pdf` | white 65 lb | 12 characters, First Sergeant role card, 6 Readiness cards, 28 deeds |
| `Monoplatoon_Phase4_Table_Pieces.pdf` | goldenrod 65 lb, plain 20 lb | Player aids, Smoke and Complaint trackers, five form pads and the Policy Letter pad |
| `Monoplatoon_Complete_Print_Set.pdf` | | Everything above in one file |

**Already printed an earlier version?** Each release's notes include a reprint guide listing only the pages that changed since the previous release, on which paper, and the release attaches `Monoplatoon-vX.Y.Z-reprint-since-vA.B.C.pdf` with just those pages. The rulebook is reprinted whole when anything in it changes; double-sided sheets come as front and back together.

Print at **100% / Actual size**. Back sheets are mirrored for a long-edge flip. You also need a US classic Monopoly set for the board, money, houses, hotels, dice and tokens. See [docs/DESIGN_BRIEF.md](docs/DESIGN_BRIEF.md) for every dimension and colour.

## Build it yourself

Needs Python 3.10+.

```sh
pip install -r requirements.txt
python build.py          # everything, into dist/
python build.py 2        # just phase 2 (the decks)

pip install -r requirements-qa.txt
python scripts/quality_check.py      # check the design rules; must end in PASS
```

| Path | Contents |
| --- | --- |
| `src/data.py` | All game text: board, characters, every card, glossary. Edit words here. |
| `src/mp.py` | Shared fonts, colours, text fitting, the mascot and spot art |
| `src/cards.py` | Card sheet layout (9 per page, mirrored backs) |
| `src/phase1.py` ... `phase5.py` | One script per print file |
| `fonts/` | DejaVu Sans Condensed, bundled so builds look the same everywhere |
| `scripts/quality_check.py` | Checks every design rule a script can (deck math, sizes, overlaps, black ink, mirrored backs...) |
| `scripts/reprint_diff.py` | Works out the minimum reprint between two releases |
| `scripts/compare_builds.py` | Page-by-page text and pixel comparison of two builds |
| `scripts/render_proofs.py` | Renders pages to PNG for a by-eye review |
| `VERSION` | The version stamped on every page footer and used for the release tag |
| `CLAUDE.md` | Working notes and the full design rules for anyone (or any AI) editing the project |

## How changes and releases work

- All work goes to the **`develop`** branch. Every push builds the full set and keeps it as a downloadable proof for 14 days (Actions tab, *CI* run, *Artifacts*).
- The **Quality check** workflow runs on every push and pull request to `develop` and `main`, checking 400+ design rules. Its report is in the run summary.
- To release, bump `VERSION`, add a `CHANGELOG.md` entry, and open a pull request from `develop` into **`main`**. Only `develop` may merge into `main`.
- Merging into `main` runs *Release print package*: it builds, runs the quality check (any error stops the release), works out the minimal reprint since the previous release, creates the GitHub Release `vX.Y.Z` with the zip, the reprint PDF and every PDF attached, and publishes the zip to GitHub Packages. If that version was already released it publishes nothing and asks you to bump `VERSION`.

Details in [CONTRIBUTING.md](CONTRIBUTING.md).

## Legal

Fan-made parody for personal use. Not affiliated with, sponsored or endorsed by Hasbro; MONOPOLY is a trademark of Hasbro. No Hasbro artwork, logo or mascot is reproduced; all art here is original. Not affiliated with the US Army or the Department of Defense. All characters are invented and no real person is depicted.

Code is MIT licensed ([LICENSE](LICENSE)). The bundled DejaVu fonts are under their own license ([fonts/LICENSE-DejaVu.txt](fonts/LICENSE-DejaVu.txt)).
