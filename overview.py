#!/usr/bin/env python3
"""
overview.py - Requirement 1: Load a signup CSV and print a quick overview.

Usage:
    python overview.py sample_signups.csv
"""

import sys

import pandas as pd

# The six columns exported by the registration questionnaire.
REQUIRED_COLUMNS = ["姓名", "学号", "邮箱", "志愿1", "志愿2", "推荐人"]


def load_signups(path):
    """Load the signup CSV as strings and normalize it.

    - dtype=str: keep student IDs as text so leading zeros are preserved.
    - keep_default_na=False: empty cells become "" instead of NaN.
    - utf-8-sig reads plain UTF-8 and also strips a BOM if present;
      GBK is tried as a fallback for exports from Chinese Windows.
    - Header names and cell values are whitespace-stripped.
    """
    last_error = None
    for encoding in ("utf-8-sig", "gbk"):
        try:
            df = pd.read_csv(
                path,
                dtype=str,
                encoding=encoding,
                keep_default_na=False,
            )
            break
        except UnicodeDecodeError as exc:
            last_error = exc
    else:  # No encoding worked.
        raise last_error

    # Normalize header names (strip BOM leftovers / spaces).
    df.columns = [str(col).strip() for col in df.columns]

    # Trim surrounding whitespace in every cell; whitespace-only -> "".
    df = df.apply(
        lambda col: col.map(lambda v: v.strip() if isinstance(v, str) else v)
    )
    return df


def print_overview(df):
    """Print row count, per-column empty counts, and fully duplicate rows."""
    print("=" * 60)
    print("CSV Overview")
    print("=" * 60)
    print(f"Total rows: {len(df)}")

    # Report any expected columns that are missing from the export.
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        print(f"WARNING - missing expected columns: {missing}")

    # Count empty (blank or whitespace-only) cells in each column.
    print("\nEmpty values per column:")
    for col in df.columns:
        empty_count = int((df[col] == "").sum())
        print(f"  {col}: {empty_count}")

    # Fully duplicated rows: identical content in every column.
    # keep=False marks every row that has at least one duplicate.
    dup_mask = df.duplicated(keep=False)
    dup_rows = df[dup_mask]
    print(f"\nFully duplicate rows: {len(dup_rows)} row(s)")
    if len(dup_rows) > 0:
        print(dup_rows.to_string(index=True))
    print("=" * 60)


def main():
    if len(sys.argv) != 2:
        print("Usage: python overview.py <signups.csv>")
        sys.exit(1)

    df = load_signups(sys.argv[1])
    print_overview(df)


if __name__ == "__main__":
    main()
