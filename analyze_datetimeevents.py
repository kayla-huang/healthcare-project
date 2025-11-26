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
class Summary:
    rows: int
    missing: dict[str, int]
    warning_counts: dict[str | None, int]
    itemid_top: dict[str | None, int]
    store_before_chart: int


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
    store_before_chart = 0
    total_rows = 0
    header: list[str] | None = None

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

        charttime = parse_timestamp(row.get("charttime"))
        storetime = parse_timestamp(row.get("storetime"))
        if charttime and storetime and storetime < charttime:
            store_before_chart += 1

    top_itemids = dict(itemid_counts.most_common(5))

    return Summary(
        rows=total_rows,
        missing=dict(missing),
        warning_counts=dict(warning_counts),
        itemid_top=top_itemids,
        store_before_chart=store_before_chart,
    )


def run_summary(path: str = CSV_PATH) -> Summary:
    with open(path, newline="") as handle:
        reader = csv.DictReader(handle)
        return summarize_rows(reader)


def main() -> None:
    summary = run_summary()

    print("Rows:", summary.rows)
    print("Missing values per column:")
    for column, count in summary.missing.items():
        print(f"  {column}: {count}")

    print("\nWarning flag counts:")
    for value, count in summary.warning_counts.items():
        print(f"  {value}: {count}")

    print("\nTop itemids:")
    for itemid, count in summary.itemid_top.items():
        print(f"  {itemid}: {count}")

    print("\nRecords where storetime < charttime:", summary.store_before_chart)


if __name__ == "__main__":
    main()
