"""
Quick exploratory script for the datetime events sample.

The helpers avoid heavy dependencies so they can run in memory-constrained
environments. Run the script directly to generate a concise summary of the
sample file (row counts, missing values, common item IDs, and simple timestamp
checks). Adjust the `CSV_PATH` constant as needed.
"""

from __future__ import annotations

import csv
from collections import Counter, defaultdict
from dataclasses import dataclass
from datetime import datetime
from typing import Iterable

CSV_PATH = "datetimeevents_sample_1000.csv"


@dataclass
class TimeDeltaSummary:
    count: int
    min_minutes: float | None
    max_minutes: float | None
    mean_minutes: float | None


@dataclass
class Summary:
    rows: int
    missing: dict[str, int]
    warning_counts: dict[str | None, int]
    itemid_top: dict[str | None, int]
    valueuom_top: dict[str | None, int]
    store_before_chart: int
    store_equal_chart: int
    parse_failures: dict[str, int]
    unique_subjects: int
    unique_hadm: int
    unique_stays: int
    store_minus_chart: TimeDeltaSummary


def parse_timestamp(value: str | None) -> datetime | None:
    """Convert a timestamp string to a ``datetime`` object.

    Returns ``None`` when parsing fails so downstream checks can skip malformed
    values instead of raising.
    """

    if not value:
        return None

    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(value, fmt)
        except ValueError:
            continue
    return None


def summarize_rows(rows: Iterable[dict[str, str | None]]) -> Summary:
    missing: defaultdict[str, int] = defaultdict(int)
    warning_counts: Counter[str | None] = Counter()
    itemid_counts: Counter[str | None] = Counter()
    valueuom_counts: Counter[str | None] = Counter()
    store_before_chart = 0
    store_equal_chart = 0
    parse_failures = {"charttime": 0, "storetime": 0}
    total_rows = 0
    header: list[str] | None = None

    subjects: set[str] = set()
    hadms: set[str] = set()
    stays: set[str] = set()

    delta_count = 0
    delta_sum = 0.0
    delta_min: float | None = None
    delta_max: float | None = None

    for row in rows:
        total_rows += 1

        if header is None:
            header = list(row.keys())
            for column in header:
                missing[column] = 0

        for column, value in row.items():
            if value is None or value == "":
                missing[column] += 1

        warning_counts[row.get("warning")] += 1
        itemid_counts[row.get("itemid")] += 1
        valueuom_counts[row.get("valueuom")] += 1

        subject_id = row.get("subject_id")
        hadm_id = row.get("hadm_id")
        stay_id = row.get("stay_id")
        if subject_id:
            subjects.add(subject_id)
        if hadm_id:
            hadms.add(hadm_id)
        if stay_id:
            stays.add(stay_id)

        charttime = parse_timestamp(row.get("charttime"))
        storetime = parse_timestamp(row.get("storetime"))
        if row.get("charttime") and not charttime:
            parse_failures["charttime"] += 1
        if row.get("storetime") and not storetime:
            parse_failures["storetime"] += 1

        if charttime and storetime:
            if storetime < charttime:
                store_before_chart += 1
            if storetime == charttime:
                store_equal_chart += 1

            delta_minutes = (storetime - charttime).total_seconds() / 60.0
            delta_count += 1
            delta_sum += delta_minutes
            delta_min = delta_minutes if delta_min is None else min(delta_min, delta_minutes)
            delta_max = delta_minutes if delta_max is None else max(delta_max, delta_minutes)

    top_itemids = dict(itemid_counts.most_common(5))
    top_valueuom = dict(valueuom_counts.most_common(5))

    delta_mean = delta_sum / delta_count if delta_count else None
    delta_summary = TimeDeltaSummary(
        count=delta_count,
        min_minutes=delta_min,
        max_minutes=delta_max,
        mean_minutes=delta_mean,
    )

    return Summary(
        rows=total_rows,
        missing=dict(missing),
        warning_counts=dict(warning_counts),
        itemid_top=top_itemids,
        valueuom_top=top_valueuom,
        store_before_chart=store_before_chart,
        store_equal_chart=store_equal_chart,
        parse_failures=parse_failures,
        unique_subjects=len(subjects),
        unique_hadm=len(hadms),
        unique_stays=len(stays),
        store_minus_chart=delta_summary,
    )


def run_summary(path: str = CSV_PATH) -> Summary:
    with open(path, newline="") as handle:
        reader = csv.DictReader(handle)
        return summarize_rows(reader)


def print_timedelta_summary(label: str, data: TimeDeltaSummary) -> None:
    print(f"{label}:")
    if data.count == 0:
        print("  (no valid timestamp pairs)")
        return
    print(f"  Count: {data.count}")
    print(f"  Min minutes: {data.min_minutes}")
    print(f"  Max minutes: {data.max_minutes}")
    print(f"  Mean minutes: {data.mean_minutes}")


def main() -> None:
    summary = run_summary()

    print("Rows:", summary.rows)
    print("Missing values per column:")
    for column, count in summary.missing.items():
        print(f"  {column}: {count}")

    print("\nUnique IDs:")
    print(f"  Subjects: {summary.unique_subjects}")
    print(f"  Admissions (hadm_id): {summary.unique_hadm}")
    print(f"  Stays: {summary.unique_stays}")

    print("\nWarning flag counts:")
    for value, count in summary.warning_counts.items():
        print(f"  {value}: {count}")

    print("\nTop itemids:")
    for itemid, count in summary.itemid_top.items():
        print(f"  {itemid}: {count}")

    print("\nTop valueuom:")
    for valueuom, count in summary.valueuom_top.items():
        print(f"  {valueuom}: {count}")

    print("\nRecords where storetime < charttime:", summary.store_before_chart)
    print("Records where storetime == charttime:", summary.store_equal_chart)

    print("\nTimestamp parse failures:")
    for field, count in summary.parse_failures.items():
        print(f"  {field}: {count}")

    print()
    print_timedelta_summary("Storetime minus charttime (minutes)", summary.store_minus_chart)


if __name__ == "__main__":
    main()
