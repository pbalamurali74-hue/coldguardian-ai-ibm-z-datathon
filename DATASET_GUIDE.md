# Real measured temperature data for ColdGuardian AI

## Public research dataset selected

**Long-range freeze-preventive vaccine carriers in Nepal: thermal data**  
Source: Mendeley Data, DOI: https://doi.org/10.17632/j277dvs69g.1  
Dataset page: https://data.mendeley.com/datasets/j277dvs69g/1  
Licence shown on the dataset page: **CC BY 4.0**.

The authors describe temperature measurements recorded by LogTag TRIX-8 monitors at 24 health posts in Nepal, across freeze-preventive vaccine carriers, standard vaccine carriers, ice-pack freezers (where available), and ambient locations. The CSVs are measured research data, not the synthetic shipment records currently bundled with ColdGuardian. Cite the dataset and its authors (Alexandra Sibole, Steven Diesburg, Sandeep Kumar) in any submission or presentation.

## Important scope distinction

This source provides measured thermal time series. It does **not** provide the complete shipment, GPS route, facility capacity, wastage outcome, or product-disposition fields required to validate every part of ColdGuardian. Therefore:

- The **Real-data research lab** evaluates temperature time-series behaviour on uploaded measured data.
- The main operations dashboard still uses clearly labelled synthetic shipment/facility metadata unless you replace those data with appropriately sourced records.
- Do not describe the prototype's synthetic logistics records as real, and do not claim clinical or vaccine-safety validation from this dataset alone.
- Do not assume every series uses the standard +2°C to +8°C band. The correct operating range depends on the equipment/product and study context. Use temperature ranges only when supported by the dataset documentation or qualified domain guidance.

## How to use the measured data

1. Open the Mendeley Data page above and choose **Download All**.
2. Extract the downloaded archive locally. Keep the original files unchanged so the data provenance is reproducible.
3. Inspect one CSV's header and identify its timestamp (or date/time) column and temperature column. Column names may differ by file.
4. Normalize a selected series using the helper script below. It creates a new file; it does not overwrite the source data.
5. In the deployed ColdGuardian app, scroll to **Real-data research lab** and upload the normalized CSV.
6. Review the observed time series and the chronological holdout MAE for the simple persistence and linear-trend baselines. These are exploratory results, not proof of general predictive performance.

Example command (replace the column names with the exact headers in your downloaded CSV):

```bash
python scripts/prepare_measured_temperature_csv.py \
  --input "/path/to/original.csv" \
  --timestamp-col "timestamp" \
  --temperature-col "temperature" \
  --series-id "Nepal_carrier_01" \
  --output "measured_temperature_normalized.csv"
```

If the source has separate date and time columns, use `--date-col` and `--time-col` instead of `--timestamp-col`.

## Normalized CSV format

The research lab expects:
- `timestamp`: parseable date/time
- `temperature_c`: numeric measured temperature in degrees Celsius
- `series_id`: optional label for the sensor/location series

The helper script adds a `source_file` column for traceability. Keep the dataset citation and original file alongside analysis outputs.
