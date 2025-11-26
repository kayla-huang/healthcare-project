# Quick checks for datetime events sample

This repository provides a lightweight Python script `analyze_datetimeevents.py` that performs basic quality checks on a `datetimeevents` sample (for example `datetimeevents_sample_1000.csv`) in memory-constrained environments.

## What it does
- Count total rows
- Compute missing values per column
- Summarize the distribution of the `warning` flag
- List the top five `itemid` values
- List the top five `valueuom` values
- Count unique `subject_id`, `hadm_id`, and `stay_id` to gauge patient/admission/ICU stay coverage
- Count records where `storetime` occurs before or exactly at `charttime` to flag potential ordering issues
- Count parse failures for `charttime` and `storetime` timestamps to surface format problems
- Summarize `storetime - charttime` delay (minutes) with min, max, and mean

## How to run
1. Confirm the CSV path (defaults to the repository file `datetimeevents_sample_1000.csv`). If you want to use a different path, adjust the `CSV_PATH` constant before calling `main()`.
2. Execute the script:
   ```bash
   python analyze_datetimeevents.py
   ```

## Output guide
- `Rows`: total row count of the sample
- `Missing values per column`: number of missing values for each column
- `Unique IDs`: distinct counts of `subject_id`, `hadm_id`, and `stay_id`
- `Warning flag counts`: counts for each value in the `warning` column
- `Top itemids`: five most frequent `itemid` values
- `Top valueuom`: five most frequent `valueuom` values
- `Records where storetime < charttime`: rows where `storetime` precedes `charttime`
- `Records where storetime == charttime`: rows where `storetime` equals `charttime`
- `Timestamp parse failures`: counts of unparseable `charttime` or `storetime` values
- `Storetime minus charttime (minutes)`: sample size plus min/max/mean delay in minutes

These checks help quickly assess completeness, latency, and potential data issues when you cannot load the full dataset.
