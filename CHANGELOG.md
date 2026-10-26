# Changelog

Each release's notes are taken from its section here, so write the entry before merging `develop` into `main`. Versions follow [Semantic Versioning](https://semver.org/): a new card or rule tweak is a minor bump, a typo or layout fix is a patch.

## [0.1.1] - 2026-10-26

Fixes found by the new quality check, plus the tooling that found them.

### Fixed
- **The Motor Pool** (sticker and deed): the joke no longer names a real person. "since the Obama administration" is now "since 2009", in line with the no-real-people rule.
- **Card sheets:** the paper note ("Single-sided, black ink, on pale green…") was printed underneath the top row of cards, so only "Single-s" showed. It now sits below the cards, and the sheet title sits clear of the cut marks.
- **Character backs heading** no longer runs off the right edge of the page.
- **Sticker placement key** shows full names (it cut off "THE BATTALION CONFERENCE ROOM") and stays inside the page.

### Added
- **Quality check** (`scripts/quality_check.py` and the *Quality check* workflow on `develop` and `main`): 400+ checks of the design rules, including deck math against Chance and Community Chest, counts, dimensions and colours, glossary coverage, no real people or Hasbro characters, black-ink decks, mirrored backs, text overlap and overflow, and rulebook versus player-aid consistency. The release is blocked if it fails.
- **Minimal reprints:** every release lists exactly which pages changed since the last one, on which paper, and attaches a PDF of just those pages. The rulebook reprints whole; double-sided sheets reprint as front and back.
- `scripts/compare_builds.py` (page-by-page build comparison), `scripts/render_proofs.py` (PNG proofs for review), and `CLAUDE.md`.

## [0.1.0] - 2026-10-26

First complete print-and-play set.

### Added
- **Board stickers:** all 40 spaces renamed on the enlisted ladder from Reception to the Secretary's Office, each with spot art, a joke and its price; four corners; two deck labels; the centre title bar in two pieces with the *Hurry up and wait.* slogan; the Specialist Pennyless mascot piece; a *Made by the Lowest Bidder* maker's mark.
- **Command Guidance** and **Barracks Lawyer** decks, 16 cards each, one for one with Chance and Community Chest, single-sided black ink for coloured cardstock.
- **The Building** deck: 7 Directives, 4 Walk-Backs, 4 Paperwork, 3 Uniform Changes, with issuer icons for the Secretary and the Commander-in-Chief.
- **12 characters**, the First Sergeant role card and 6 secret Readiness cards, with one shared back.
- **28 title deeds** with purchase price for net worth at ETS.
- **Table pieces:** First Sergeant and Soldier player aids, Smoke and Command Climate trackers, and tear-off pads: Form 4856-ish, Form 31-ish, Memorandum for Record, Form 2823-ish, Risk Assessment, and the card-size Policy Letter pad.
- **Rulebook** with setup, auctions, the Policy Shelf, Inspection, Relief for Cause, *It's the Law*, a characters table, add-ons, glossary and print checklist.
- One-command build (`python build.py`) and a release workflow that publishes the print zip to Releases and GitHub Packages.
