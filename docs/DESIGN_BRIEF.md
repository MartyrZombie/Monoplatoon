# Design brief

Production specs for every printed piece. Dimensions were fit-tested on a new US classic Monopoly board (mint green) in an earlier build and are reused here unchanged.

## Board stickers (matte sticker paper, 100%)

| Piece | Size | Count | Notes |
| --- | --- | --- | --- |
| Backing green | `#BFDDC8` | | Matched to the board; behind every sticker |
| Property / Rotation / utility / tax / card space | 1 5/8 x 2 9/16 in | 36 | Colour band, name, spot art, joke, price |
| Corner | 2 9/16 in square | 4 | Payday, CQ Desk, Block Leave, Staff Duty |
| Deck label | 3.45 x 2.3 in | 2 | Covers each centre card outline (3 5/16 x 2 3/16 in) |
| Centre bar, pieces A + B | 11.6 x 2.5 in, plus 0.5 in green above and 0.65 in below | 2 | Butt together at a letter gap; covers the old logo and tagline |
| Mascot piece | 4.15 x 2.4 in | 1 | Applied last, bottom edge on the bar's top line |
| Maker's mark | 1.7 x 1 in | 2 | Oval and rounded rectangle; covers the maker's oval |

## Cards and table pieces

| Piece | Size | Count | Stock | Sides |
| --- | --- | --- | --- | --- |
| Command Guidance | 2 1/8 x 3 3/16 in | 16 | Pale green 65 lb | Single, black ink |
| Barracks Lawyer | 2 1/8 x 3 3/16 in | 16 | Buff / manila 65 lb | Single, black ink |
| The Building | 2 1/8 x 3 3/16 in | 18 | Grey 65 lb | Double, mirrored backs |
| Characters + 1SG role + Readiness | 2 1/8 x 3 3/16 in | 19 | White 65 lb | Double, one shared back |
| Title deeds | 2 1/8 x 3 3/16 in | 28 | White 65 lb | Single |
| Player aids | 6 x 4 in | 1 First Sergeant + 5 Soldier | Goldenrod 65 lb | Single |
| Trackers | 5 x 3 in | 6 Smoke + 1 Command Climate | Goldenrod 65 lb | Single |
| Form pads | 2 x 3 in | 5 pads x 36 sheets | Plain 20 lb | Single, pad-glued top |
| Policy Letter pad | 2 1/8 x 3 3/16 in | 27 sheets | Plain 20 lb | Single, pad-glued top |

Cards print nine to a portrait letter page at 100%. Back sheets are mirrored left to right for a long-edge flip.

## Type and colour

- Headlines: DejaVu Sans Condensed Bold (bundled in `fonts/`), close to the board's own lettering.
- Body: Courier / Courier Bold, the typewriter face built into every PDF reader.
- Rules text black. Flavor and glosses dark grey `#555555`.
- Accent olive `#4B5320`; Walk-Back red `#B3261E`; property groups use the standard Monopoly colours.

## Art

All line art is original, drawn in code in `src/mp.py`, in a plain cartoon manner. Never Hasbro's art, logo or mascot.

- **Specialist Pennyless:** an E-4 in an oversized PT shirt and patrol cap, always holding a form. Poses: shrug, salute (wrong hand), asleep, Hawaiian shirt, point, counting $1 bills, hammer with no handle, pinning on patches, standing.
- **Secretary Brock Lethality:** suit and tie, mid-push-up, stopwatch on the floor. Building cards only.
- **The Commander-in-Chief:** never shown; a hand holding a phone that reads 2:00 AM. Building cards only.
- About 50 spot icons for spaces and cards: mold, the one dryer, the truck on blocks, the inbox stack, the handle-less hammer, the reflective belt, the glove-as-beret, and so on.

## Phases

| Phase | File | Script |
| --- | --- | --- |
| 0 | Style and fit test | Done in the earlier build; measurements reused |
| 1 | Board stickers | `src/phase1.py` |
| 2 | Decks | `src/phase2.py` |
| 3 | Characters, role, Readiness, deeds | `src/phase3.py` |
| 4 | Aids, trackers, pads | `src/phase4.py` |
| 5 | Rulebook, glossary, print checklist | `src/phase5.py` |
