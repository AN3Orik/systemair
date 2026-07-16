# Model Maximum Airflow Registry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Add verified Systemair ErP `qv max` values to every existing `MODEL_SPECS` entry and archive the supporting model documents.

**Architecture:** Keep airflow metadata in the existing per-model dictionaries in `custom_components/systemair/const.py`. Store representative official product cards in `docs/datasheet/`, maintain a source index that records item numbers, variant reuse, conflicts, and unresolved models, and rely on existing business-logic tests for regression coverage.

**Tech Stack:** Python 3.14, standard-library `unittest`, Ruff, Systemair Datasheet API, Markdown, PDF documents.

---

### Task 1: Archive Official Datasheets

**Files:**
- Create: `docs/datasheet/*.pdf`
- Create: `docs/datasheet/README.md`

The official PDF endpoint is:

```text
https://datasheet.systemair.com/pdf/v1/detail?itemNo={ITEM_NO}&division=005&language=en
```

Download one representative product card per base model, separate L/R cards where `qv max` differs, both conflicting `VTR 200/B` revisions, and the five legacy `VR` cards. Use these filesystem-safe filenames and item numbers:

| Filename | Item number |
|---|---:|
| `VSC 100.pdf` | 488806 |
| `VSC 200.pdf` | 488807 |
| `VSC 300.pdf` | 488808 |
| `VR 400 DCV-B.pdf` | 12309 |
| `VR 400 DC.pdf` | 12278 |
| `VR 400 DC-DE.pdf` | 12527 |
| `VR 400 DE.pdf` | 12529 |
| `VR 700 DCV.pdf` | 12425 |
| `VR 700 DCV-DE.pdf` | 12528 |
| `VR 700 DC.pdf` | 12424 |
| `VR 700 DC-DE.pdf` | 12523 |
| `VSR 150-B.pdf` | 588885 |
| `VSR 200-B.pdf` | 588864 |
| `VSR 300.pdf` | 488802 |
| `VSR 400.pdf` | 488881 |
| `VSR 500.pdf` | 488804 |
| `VSR 700.pdf` | 488866 |
| `VTC 200.pdf` | 24803 |
| `VTC 200-1.pdf` | 488862 |
| `VTC 300.pdf` | 488841 |
| `VTC 500.pdf` | 488843 |
| `VTC 700.pdf` | 488845 |
| `VTR 100-B.pdf` | 488809 |
| `VTR 150-B L.pdf` | 488821 |
| `VTR 150-B R.pdf` | 488820 |
| `VTR 150-K L.pdf` | 488813 |
| `VTR 150-K R.pdf` | 488812 |
| `VTR 200-B R 1000W item 14882.pdf` | 14882 |
| `VTR 200-B R 1000W item 79203.pdf` | 79203 |
| `VTR 250-B.pdf` | 488825 |
| `VTR 275-B.pdf` | 488880 |
| `VTR 300-B.pdf` | 488827 |
| `VTR 350-B.pdf` | 488921 |
| `VTR 500.pdf` | 488831 |
| `VTR 700.pdf` | 488835 |

Also archive the official 2019 SAVE technical fiche, the current SAVE technical-specifications leaflet, the archived VTC 200 datasheet, and the archived VR 400/700 technical booklet under the filenames recorded in `docs/datasheet/README.md`.

- [x] **Step 1: Download the PDFs**

Create `docs/datasheet/` and download each item above from the official endpoint without overwriting unrelated files.

- [x] **Step 2: Verify every PDF**

Check that every new `.pdf` starts with `%PDF`, is non-empty, and can be opened by `pypdf.PdfReader` using Windows Python:

```powershell
& 'C:\Users\ANZO-MI\AppData\Local\Microsoft\WindowsApps\py.exe' -3 -c "from pathlib import Path; from pypdf import PdfReader; files=list(Path('docs/datasheet').glob('*.pdf')); assert files; [(p.name, len(PdfReader(p).pages)) for p in files]"
```

Expected: exit code 0 and at least one readable page in every file.

- [x] **Step 3: Write the source index**

Create `docs/datasheet/README.md` with:

- the official endpoint and retrieval date;
- each filename, item number, declared `qv max`, and covered registry entries;
- explicit variant reuse for equal L/R and heater variants;
- the selected legacy `VTR 200/B` value of 257, the later 275 revision, and the 2567 decimal-shift error;
- the documented `VTC 200-1` value of 284 and the newer catalogue card's 286 discrepancy;
- the legacy `VR` cards that contain no comparable ErP `qv max`.

### Task 2: Populate Maximum Airflow

**Files:**
- Modify: `custom_components/systemair/const.py:68`

- [x] **Step 1: Add `max_airflow_m3h` to every entry**

Use the following verified mapping. Repeated entries are intentional only where official data confirms the same base unit; conflicts and missing ErP values remain `None`.

```python
MAX_AIRFLOW_BY_MODEL = {
    "VSC 100": 166,
    "VSC 200": 333,
    "VSC 300": 510,
    "VR 400 DCV/B": 302,
    "VR 400 DC": None,
    "VR 400 DE": 302,
    "VR 700 DCV": 554,
    "VR 700 DC": 515,
    "VSR 150/B": 169,
    "VSR 150/B L": 169,
    "VSR 150/B R": 169,
    "VSR 200/B L": 284,
    "VSR 200/B R": 284,
    "VSR 300": 368,
    "VSR 400": 615,
    "VSR 500": 609,
    "VSR 700": 870,
    "VTC 200 L": 267,
    "VTC 200 R": 267,
    "VTC 200-1 L": 284,
    "VTC 200-1 R": 284,
    "VTC 300 L": 364,
    "VTC 300 R": 364,
    "VTC 500 L": 602,
    "VTC 500 R": 602,
    "VTC 700 L": 855,
    "VTC 700 R": 855,
    "VTR 100/B": 150,
    "VTR 150/B L 500W": 278,
    "VTR 150/B L 1000W": 278,
    "VTR 150/B R 500W": 258,
    "VTR 150/B R 1000W": 258,
    "VTR 150/K L 500W": 278,
    "VTR 150/K L 1000W": 278,
    "VTR 150/K R 500W": 258,
    "VTR 150/K R 1000W": 258,
    "VTR 200/B L 500W": 257,
    "VTR 200/B L 1000W": 257,
    "VTR 200/B R 500W": 257,
    "VTR 200/B R 1000W": 257,
    "VTR 250/B L 500W": 307,
    "VTR 250/B L 1000W": 307,
    "VTR 250/B R 500W": 307,
    "VTR 250/B R 1000W": 307,
    "VTR 275/B L": 316,
    "VTR 275/B R": 316,
    "VTR 300/B L": 351,
    "VTR 300/B R": 351,
    "VTR 350/B L": 504,
    "VTR 350/B R": 504,
    "VTR 500 L": 572,
    "VTR 500 R": 572,
    "VTR 700 L": 951,
    "VTR 700 R": 951,
}
```

Add each number directly to its existing `MODEL_SPECS` dictionary; do not create `MAX_AIRFLOW_BY_MODEL` as a second runtime registry.

- [x] **Step 2: Run focused tests**

```powershell
& 'C:\Users\ANZO-MI\AppData\Local\Microsoft\WindowsApps\py.exe' -3 -m unittest tests.test_power_calculation
```

Expected: all model metadata and power calculation tests pass.

### Task 3: Verify the Change

**Files:**
- Verify: `custom_components/systemair/const.py`
- Verify: `docs/datasheet/README.md`
- Verify: `docs/datasheet/*.pdf`

- [x] **Step 1: Run the full unit test suite**

```powershell
& 'C:\Users\ANZO-MI\AppData\Local\Microsoft\WindowsApps\py.exe' -3 -m unittest discover -s tests
```

Expected: all tests pass.

- [x] **Step 2: Run repository lint**

```powershell
& 'C:\Users\ANZO-MI\AppData\Local\Microsoft\WindowsApps\py.exe' -3.14 -m ruff format --check custom_components/systemair/const.py
& 'C:\Users\ANZO-MI\AppData\Local\Microsoft\WindowsApps\py.exe' -3.14 -m ruff check custom_components/systemair/const.py
```

Expected: scoped Ruff formatting and checks pass. The repository-wide wrapper is intentionally avoided because the user-owned `.tmp/hacs-default` tree contains unrelated files.

- [x] **Step 3: Inspect the final diff**

```powershell
git status --short
git diff --check
git diff -- custom_components/systemair/const.py docs/datasheet/README.md docs/superpowers/specs/2026-07-16-model-max-airflow-design.md
```

Expected: only the registry, source documentation, plan/spec files, and archived PDFs are new or changed. Do not commit or push without a new explicit request.
