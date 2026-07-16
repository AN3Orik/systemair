# Systemair Model Datasheets

These documents support the `max_airflow_m3h` values in `custom_components/systemair/const.py`.

The individual product cards were generated on 2026-07-16 by the official Systemair Datasheet API:

```text
https://datasheet.systemair.com/pdf/v1/detail?itemNo={ITEM_NO}&division=005&language=en
```

## Value Definition

`max_airflow_m3h` uses the manufacturer's ErP `qv max` value in m³/h. Systemair's product-range leaflet labels the equivalent residential-unit value as `Qmax at 100 Pa`.

The ErP field `Ps ref = 50 Pa` belongs to `qv ref`; it is not the pressure associated with `qv max`.

## Confirmed Values

| Registry entries | `qv max`, m³/h | Primary saved document | Item number and reuse evidence |
|---|---:|---|---|
| `VSC 100` | 166 | [VSC 100.pdf](VSC%20100.pdf) | 488806 |
| `VSC 200` | 333 | [VSC 200.pdf](VSC%20200.pdf) | 488807 |
| `VSC 300` | 510 | [VSC 300.pdf](VSC%20300.pdf) | 488808 |
| `VR 400 DCV/B`, `VR 400 DE` | 302 | [VR 400 DE.pdf](VR%20400%20DE.pdf) | Item 12529 (`VR 400 DCV /DE`) declares 302. Exact DCV/B L/R items 12309/12314 omit ErP data, while the archived official `VR 400 DCV/B` curve independently reaches the same `Qmax at 100 Pa`; the saved [VR 400 DCV-B.pdf](VR%20400%20DCV-B.pdf) documents the exact registry variant |
| `VR 700 DCV` | 554 | [VR 700 DCV-DE.pdf](VR%20700%20DCV-DE.pdf) | Item 12528 (`VR 700 DCV /DE`) declares 554. Exact item 12425 lists 240 W instead of 230 W but its archived official `VR 700 DCV` curve independently agrees at `Qmax at 100 Pa`; [VR 700 DCV.pdf](VR%20700%20DCV.pdf) documents that registry revision |
| `VR 700 DC` | 515 | [VR 700 DC-DE.pdf](VR%20700%20DC-DE.pdf) | Item 12523 (`VR 700 DC /DE`) declares 515 and has the same 246 W supply and extract fans as exact item 12424; [VR 700 DC.pdf](VR%20700%20DC.pdf) documents the exact registry variant |
| `VSR 150/B`, `VSR 150/B L`, `VSR 150/B R` | 169 | [VSR 150-B.pdf](VSR%20150-B.pdf) | Representative L item 588885; R item 588884 and the 2019 technical fiche publish the same value |
| `VSR 200/B L`, `VSR 200/B R` | 284 | [VSR 200-B.pdf](VSR%20200-B.pdf) | Representative L item 588864; R item 588863 publishes the same value |
| `VSR 300` | 368 | [VSR 300.pdf](VSR%20300.pdf) | 488802 |
| `VSR 400` | 615 | [VSR 400.pdf](VSR%20400.pdf) | 488881 |
| `VSR 500` | 609 | [VSR 500.pdf](VSR%20500.pdf) | 488804 |
| `VSR 700` | 870 | [VSR 700.pdf](VSR%20700.pdf) | 488866 |
| `VTC 200 L`, `VTC 200 R` | 267 | [VTC 200.pdf](VTC%20200.pdf) | Representative L item 24803; R item 24802 publishes the same value |
| `VTC 200-1 L`, `VTC 200-1 R` | 284 | [SAVE VSC VSR VTC VTR Technical Fiche 2019.pdf](SAVE%20VSC%20VSR%20VTC%20VTR%20Technical%20Fiche%202019.pdf) | The official 2019 technical fiche publishes 284 for the base model; the L/R duct layout does not change the internals. The newer generated card is retained because it publishes 286 for a later catalogue revision |
| `VTC 300 L`, `VTC 300 R` | 364 | [VTC 300.pdf](VTC%20300.pdf) | Representative L item 488841; R item 488840 publishes the same value |
| `VTC 500 L`, `VTC 500 R` | 602 | [VTC 500.pdf](VTC%20500.pdf) | Representative L item 488843; R item 488842 publishes the same value |
| `VTC 700 L`, `VTC 700 R` | 855 | [VTC 700.pdf](VTC%20700.pdf) | Representative L item 488845; R item 488844 publishes the same value |
| `VTR 100/B` | 150 | [VTR 100-B.pdf](VTR%20100-B.pdf) | 488809 |
| `VTR 150/B L 500W`, `VTR 150/B L 1000W` | 278 | [VTR 150-B L.pdf](VTR%20150-B%20L.pdf) | Representative L 500 W item 488821; L 1000 W item 488819 publishes the same value |
| `VTR 150/B R 500W`, `VTR 150/B R 1000W` | 258 | [VTR 150-B R.pdf](VTR%20150-B%20R.pdf) | Representative R 500 W item 488820; R 1000 W item 488818 publishes the same value |
| `VTR 150/K L 500W`, `VTR 150/K L 1000W` | 278 | [VTR 150-K L.pdf](VTR%20150-K%20L.pdf) | White and stainless-steel L items 488811, 488813, 488815, and 488817 publish the same value |
| `VTR 150/K R 500W`, `VTR 150/K R 1000W` | 258 | [VTR 150-K R.pdf](VTR%20150-K%20R.pdf) | White and stainless-steel R items 488810, 488812, 488814, and 488816 publish the same value |
| All four `VTR 200/B` L/R and 500/1000 W entries | 257 | [VTR 200-B R 1000W item 14882.pdf](VTR%20200-B%20R%201000W%20item%2014882.pdf) | The basic-unit ErP block publishes 257. The local-demand block's 2567 and `qv ref 0.5` are decimal-shift errors: the unchanged 180 W `P max`, unchanged SPI, basic `qv ref 0.05`, and performance curve make the tenfold values physically inconsistent. L/R and heater size do not change the fan/heat-exchanger internals |
| All four `VTR 250/B` L/R and 500/1000 W entries | 307 | [VTR 250-B.pdf](VTR%20250-B.pdf) | Items 488822, 488823, 488824, and 488825 publish the same value |
| `VTR 275/B L`, `VTR 275/B R` | 316 | [VTR 275-B.pdf](VTR%20275-B.pdf) | L/R and 500/1000 W items 488879, 488880, 588879, and 588880 publish the same value |
| `VTR 300/B L`, `VTR 300/B R` | 351 | [VTR 300-B.pdf](VTR%20300-B.pdf) | Representative L item 488827; R item 488826 publishes the same value |
| `VTR 350/B L`, `VTR 350/B R` | 504 | [VTR 350-B.pdf](VTR%20350-B.pdf) | Representative L item 488921; R item 488920 publishes the same value |
| `VTR 500 L`, `VTR 500 R` | 572 | [VTR 500.pdf](VTR%20500.pdf) | Representative L item 488831; R item 488830 publishes the same value |
| `VTR 700 L`, `VTR 700 R` | 951 | [VTR 700.pdf](VTR%20700.pdf) | Representative L item 488835; R item 488834 publishes the same value |

## Unresolved Values

These registry entries intentionally use `None`:

No entry is unresolved solely because its L/R counterpart lacks a separate datasheet. Matching L/R entries always reuse the confirmed side's availability. The unresolved pairs below are blocked for both sides by a model-revision conflict or by the absence of any comparable ErP declaration.

| Registry entries | Saved documents | Reason |
|---|---|---|
| `VR 400 DC` | [VR 400 DC.pdf](VR%20400%20DC.pdf), [VR 400 DC-DE.pdf](VR%20400%20DC-DE.pdf), [VR 400 700 DC DCV Technical Booklet.pdf](VR%20400%20700%20DC%20DCV%20Technical%20Booklet.pdf) | Exact item 12278 and its `/DE` item 12527 both use 115 W supply/extract fans but contain no ErP `qv max`; the booklet only provides a performance curve, so a number would require estimation |

## Supplementary Documents

| Document | Source and purpose |
|---|---|
| [SAVE VSC VSR VTC VTR Technical Fiche 2019.pdf](SAVE%20VSC%20VSR%20VTC%20VTR%20Technical%20Fiche%202019.pdf) | Official Systemair asset; compact ErP table for the 2019 SAVE range |
| [SAVE VSC VSR VTC VTR Technical Specifications.pdf](SAVE%20VSC%20VSR%20VTC%20VTR%20Technical%20Specifications.pdf) | Official Systemair Storyblok asset; labels maximum residential airflow as `Qmax at 100 Pa` and reference airflow as `Qref at 50 Pa` |
| [VTC 200 Technical Data 2014.pdf](VTC%20200%20Technical%20Data%202014.pdf) | Archived Systemair datasheet; confirms VTC 200 L/R item numbers 24803/24802 and model construction |
| [VR 400 700 DC DCV Technical Booklet.pdf](VR%20400%20700%20DC%20DCV%20Technical%20Booklet.pdf) | Archived Systemair technical booklet, retrieved from a mirror because the legacy Systemair URL no longer serves the PDF |
| [VTR 200-B R 1000W item 79203.pdf](VTR%20200-B%20R%201000W%20item%2079203.pdf) | Later catalogue revision publishing 275 m³/h; retained to document the revision difference, but not used for the legacy registry entry sourced from item 14882 |
