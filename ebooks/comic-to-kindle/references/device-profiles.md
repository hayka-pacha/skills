# Device profiles

KCC resizes every page to the profile's screen. A profile one size too small gives soft pages; one size too large gives pages the reader must shrink or crop, which is the "cut pages" complaint. Match the exact model when possible, otherwise the closest resolution.

Users rarely know the profile code. They say a marketing name, a generation number, or a year. The tables map those to the code (`-p`).

## Kindle

| Model as users name it | Generation / year | Profile | Screen |
|---|---|---|---|
| Kindle 1 | 1st gen, 2007 | `K1` | 600x670 |
| Kindle 2 | 2nd gen, 2009 | `K2` | 600x670 |
| Kindle DX / DXG | 2009-2010 | `KDX` | 824x1000 |
| Kindle Keyboard, Kindle Touch | 3rd/4th gen | `K34` | 600x800 |
| Kindle 5, Kindle 7 | 2012, 2014 | `K57` | 600x800 |
| Kindle basic 8 / 10 | 2016, 2019 | `K810` | 600x800 |
| Kindle basic 11 (also the 2024 basic) | 11th gen, 2022 / 2024 | `K11` | 1072x1448 |
| Paperwhite 1 / 2 | 2012, 2013 | `KPW` | 758x1024 |
| Voyage | 7th gen, 2014 | `KV` | 1072x1448 |
| Paperwhite 3 / 4, Oasis 1 | 2015, 2018, 2016 | `KPW34` | 1072x1448 |
| Oasis 2 / Oasis 3 | 9th gen 2017, 10th gen 2019 | `KO` | 1264x1680 |
| Paperwhite 5, Paperwhite Signature Edition | 11th gen, 2021 | `KPW5` | 1236x1648 |
| Paperwhite 6, Signature Edition 2024 | 12th gen, 2024 | `KPW6` | 1272x1696 |
| Colorsoft | 2024 | `KCS` | 1272x1696 |
| Scribe 1 / 2 | 2022, 2024 | `KS` | 1860x2480 |
| Scribe 3, Scribe Colorsoft | 2025 | `KS3` / `KSCS` | 1986x2648 |

Kindle outputs: `MOBI` for USB transfer, `EPUB` for Send to Kindle, `MOBI+EPUB` for both in one run. `CBZ` is what KCC picks automatically for the very old KF7 models.

## Kobo

| Model | Profile | Screen |
|---|---|---|
| Mini, Touch | `KoMT` | 600x800 |
| Glo | `KoG` | 768x1024 |
| Glo HD | `KoGHD` | 1072x1448 |
| Aura | `KoA` | 758x1024 |
| Aura HD | `KoAHD` | 1080x1440 |
| Aura H2O | `KoAH2O` | 1080x1430 |
| Aura ONE | `KoAO` | 1404x1872 |
| Nia | `KoN` | 758x1024 |
| Clara HD, Clara 2E, Clara BW | `KoC` | 1072x1448 |
| Clara Colour | `KoCC` | 1072x1448 |
| Libra H2O, Libra 2 | `KoL` | 1264x1680 |
| Libra Colour | `KoLC` | 1264x1680 |
| Forma | `KoF` | 1440x1920 |
| Sage | `KoS` | 1440x1920 |
| Elipsa, Elipsa 2E | `KoE` | 1404x1872 |

Kobo output: `EPUB`. KCC names it `.kepub.epub` so the Kobo opens it with its native renderer (faster page turns, correct fixed layout). Copy it anywhere on the device over USB; no conversion service needed. Pass `-- --nokepub` only if the user wants a plain `.epub` for another app.

## reMarkable

| Model | Profile | Screen |
|---|---|---|
| reMarkable 1 / 2 | `Rmk1` / `Rmk2` | 1404x1872 |
| Paper Pro | `RmkPP` | 1620x2160 |
| Paper Pro Move | `RmkPPMove` | 954x1696 |

Output: `PDF`.

## Anything else

`-p OTHER -- --customwidth W --customheight H` builds for an arbitrary screen. Look the resolution up on the manufacturer's spec sheet, and prefer `EPUB` output unless the device documents something else.

## Colour devices

KCC converts to grayscale by default because e-ink panels are grayscale and it makes files a third of the size. For Colorsoft, Clara Colour, Libra Colour or a tablet, add `-- --forcecolor`. On colour e-ink, `--eraserainbow` removes the moiré-like rainbow artifacts some screens show on fine hatching.
