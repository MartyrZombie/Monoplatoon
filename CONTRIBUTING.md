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
3. Run `python build.py` and open the PDFs in `dist/`. Print one sheet at 100% if you changed any sizes.
4. Push. The *CI* workflow builds everything, checks page counts and attaches a proof you can download from the run page.

If a change adds or removes pages, update the expected counts in `.github/workflows/ci.yml` and the table in `build.py`'s `README-PRINT.txt`.

## Releasing

1. On `develop`, bump `VERSION` (for example `0.1.0` to `0.2.0`).
2. Add a `## [0.2.0] - YYYY-MM-DD` section at the top of `CHANGELOG.md`. It becomes the release notes.
3. Open a pull request from `develop` into `main` and merge it with a merge commit.
4. *Release print package* runs on `main`: it creates the `v0.2.0` release with the zip and PDFs, and publishes `ghcr.io/martyrzombie/monoplatoon-print:0.2.0` (and `:latest`) to GitHub Packages.

Re-merging without a version bump is safe: the release workflow sees the tag already exists, builds a workflow artifact only, and warns you.

## Tone rules for new content

- The joke is the machine: pay, barracks, policy, budgets, paperwork, the chain of command. Never the soldier, their family, or anyone a soldier would be ashamed to laugh at.
- Policy gags stay procedural (renames, memos, forms, lab fees), never a policy that hurt real people.
- Every invented name is invented. No real people, no real units.
- Any term of art gets a straight-faced one-line gloss, and the gloss goes into `GLOSSARY` in `src/data.py`.
- Never reproduce Hasbro's artwork, logo or mascot. Draw originals in `src/mp.py`.
