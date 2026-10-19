# Scientific and engineering model notes

## Scientific layers

1. **Observed/entered soil measurements** — dummy inputs at this stage. N, P and K are *three different soil assays*, each in mg/kg, with different chemical availability and extraction methods. Numbers are not themselves the plant-available fertilizer requirement.
2. **Official reference fertilizer plan** — product masses (urea/TSP/MOP, kg/ha) from Sri Lankan DOA *field chilli*, scaled by area and stage.
3. **Experimental soil budget** — controlled mock pathway requiring explicit user-entered conversion/calibration coefficients. This is *not* a trained model or a locally validated crop prescription.
4. **Single-liquid composition** — composition in N-P₂O₅-K₂O mass percentages, measured liquid density and dilution factor. One stock solution has only one controllable degree of freedom (volume), so it cannot generally meet three nutrient demands exactly.
5. **Human review before actuation** — no pump or GPIO interface is present; responses specify that physical dose control is disabled.

## Future hardware integration

- Separate read-only `GET /sensor/latest` or ingestion `POST /sensor/observations` (authenticated), with sensor origin, calibration ID, timestamps and laboratory cross-validation metadata.
- Sensor values should be logged to a real database with quality checks. Never trust a cheap NPK probe without lab checks.
- Dose authorization must be distinct from simulation; require agronomist-approved dose prescriptions, liquid-product MSDS/label, density verification, pump calibration, high-concentration/overdose checks, and an emergency stop.

## Why not pretend the current code is an AI model?

No paired local fertilizer-response training data were supplied. Making a random forest or a neural network that learns fabricated labels from a DOA area equation would merely imitate the equation and make misleading confidence claims. The current audited simulator is a prerequisite to a genuine labelled-data modelling study, not the final AI component.
