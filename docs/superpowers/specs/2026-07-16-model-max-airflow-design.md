# Model Maximum Airflow Registry

## Goal

Add a passport maximum airflow value to every ventilation unit already listed in `MODEL_SPECS`.

## Scope

- Extend each existing `MODEL_SPECS` entry with `max_airflow_m3h`.
- Do not create another model table or restructure the registry.
- Do not add airflow sensors or estimation logic in this change.
- Save every official model datasheet found during research under `docs/datasheet/`.
- Report all sources used and every model left unresolved.

## Data Definition

`max_airflow_m3h` is either:

- a positive integer containing the manufacturer's ErP `qv max` value in m³/h; or
- `None` when that value cannot be verified.

For bidirectional residential ventilation units, Systemair's product-range documentation labels this value as `Qmax at 100 Pa`. The `Ps ref = 50 Pa` field in the ErP table belongs to `qv ref`, not to `qv max`, and must not be described as the pressure for the maximum airflow.

Values must not be inferred from the model number, fan power, a related model, or a flow value published at another pressure.

When official Systemair sources publish different `qv max` values for revisions that share the same registry model name, store `None` unless the registry name can identify the applicable revision.

Left/right versions differ only by the duct layout and share the same internal ventilation specification. If one side has a confirmed value and the matching side has no independently published value, reuse the confirmed value. Heater-power variants may share a value when official documentation confirms they use the same base ventilation unit specification.

Legacy country or duct-layout variants may share an ErP value only when an official declaration and the archived performance curve for the exact registry model independently agree on `Qmax at 100 Pa`. Record any fan-power discrepancy in the source index instead of silently treating the product cards as identical.

Datasheet filenames must use the corresponding registry model name in a filesystem-safe form. A single base-model datasheet may support multiple left/right or heater-power variants; duplicate PDF copies are not required.

## Source Priority

1. Current official Systemair product data or ErP documentation.
2. Archived official Systemair datasheets, manuals, or product catalogues.
3. No value when an official source cannot be found or does not state a comparable 50 Pa maximum.

## Validation

Do not add tests for static registry metadata. Run the existing business-logic tests to confirm that adding the field does not change power calculations or entity behavior, and validate the researched values against the archived datasheets and source index.

## Deliverable Report

The final handoff must list:

- confirmed values grouped by source;
- saved datasheet paths and the registry entries each file covers;
- entries that reuse a confirmed base-model value;
- unresolved models stored as `None`;
- what documentation was found for unresolved models and why it was insufficient.
