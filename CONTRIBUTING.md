# Contributing

## Branches

| Branch | Purpose |
| --- | --- |
| `develop` | Where all work lands. Commit here directly, or branch off it and open a pull request back into it. |
| `main` | Released versions only. Changes arrive by merging a pull request from `develop`. |

CI refuses a pull request into `main` from any branch other than `develop`.

## Making a change

1. Work on `develop` (or a branch off it).
2. Edit game text in `src/data.py`; layout and art live in `src/phase*.py`, `src/cards.py` and `src/mp.py`.
3. Run `python build.py`, then `python scripts/quality_check.py` (it must end in PASS), then look at the pages you touched with `python scripts/render_proofs.py`. Print one sheet at 100% if you changed any sizes.
4. Push. *CI* builds everything and attaches a proof; *Quality check* runs the design rules and puts its report in the run summary.

If a change adds or removes pages, update `PAGES` in `scripts/quality_check.py`, the paper ranges in `scripts/reprint_diff.py`, and the table in `build.py`'s `README-PRINT.txt`. If you add a rule or a card type, add a check for it to `scripts/quality_check.py`.

## Releasing

1. On `develop`, bump `VERSION` (for example `0.1.0` to `0.2.0`).
2. Add a `## [0.2.0] - YYYY-MM-DD` section at the top of `CHANGELOG.md`. It becomes the release notes.
3. Open a pull request from `develop` into `main` and merge it with a merge commit.
4. *Release print package* runs on `main`: it runs the quality check, compares every page with the previous release, creates the `v0.2.0` release with the zip, all PDFs, a reprint guide in the notes and a reprint PDF of only the changed pages, and publishes `ghcr.io/martyrzombie/monoplatoon-print:0.2.0` (and `:latest`) to GitHub Packages.

To rehearse a release without publishing, run *Release print package* by hand from the Actions tab on `develop` and leave *publish* off. The notes, reprint PDF and QA report come back as a workflow artifact.

Re-merging without a version bump is safe: the release workflow sees the tag already exists, builds a workflow artifact only, and warns you.

## Tone rules for new content

- The joke is the machine: pay, barracks, policy, budgets, paperwork, the chain of command. Never the soldier, their family, or anyone a soldier would be ashamed to laugh at.
- Policy gags stay procedural (renames, memos, forms, lab fees), never a policy that hurt real people.
- Every invented name is invented. No real people, no real units, not even named in a joke.
- Any term of art gets a straight-faced one-line gloss, and the gloss goes into `GLOSSARY` in `src/data.py`.
- Never reproduce Hasbro's artwork, logo or mascot. Draw originals in `src/mp.py`.
