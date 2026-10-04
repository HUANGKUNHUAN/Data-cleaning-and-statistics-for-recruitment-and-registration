#!/usr/bin/env python3
"""
stats.py - Requirement 3: Statistics on the cleaned data and exports.

Usage:
    python stats.py sample_signups.csv [output_dir]
"""

import os
import sys

# Reuse the loader (PR1) and the validation logic (PR2).
from overview import load_signups
from validate import validate_dataframe, build_clean_dataframe

EMPTY_LABEL = "(未填写 / not filled)"


def first_choice_summary(clean):
    """Count applicants per first choice (志愿1)."""
    choices = clean["志愿1"].replace("", EMPTY_LABEL)
    summary = choices.value_counts().rename_axis("志愿1").reset_index(name="人数")
    return summary.sort_values("人数", ascending=False).reset_index(drop=True)


def choice_coverage(clean):
    """Return counts of (both choices filled, exactly one filled, neither)."""
    first = clean["志愿1"] != ""
    second = clean["志愿2"] != ""
    both = int((first & second).sum())
    only_one = int((first ^ second).sum())  # XOR = exactly one of the two.
    neither = int((~first & ~second).sum())
    return both, only_one, neither


def main():
    if len(sys.argv) not in (2, 3):
        print("Usage: python stats.py <signups.csv> [output_dir]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) == 3 else "."
    os.makedirs(output_dir, exist_ok=True)

    # Re-run validation to derive the clean dataset; input is never modified.
    df = load_signups(input_path)
    reasons_per_row = validate_dataframe(df)
    clean = build_clean_dataframe(df, reasons_per_row)

    # 1) Group by first choice and export the summary table.
    summary = first_choice_summary(clean)
    summary_path = os.path.join(output_dir, "first_choice_summary.csv")
    summary.to_csv(summary_path, index=False, encoding="utf-8-sig")

    # 2) Count how many people filled both / only one of the two choices.
    both, only_one, neither = choice_coverage(clean)

    # 3) Export the cleaned dataset as a new CSV.
    cleaned_path = os.path.join(output_dir, "cleaned.csv")
    clean.to_csv(cleaned_path, index=False, encoding="utf-8-sig")

    print(f"Clean rows: {len(clean)}")
    print("\nFirst-choice summary:")
    print(summary.to_string(index=False))
    print(f"\nBoth choices filled: {both}")
    print(f"Only one choice filled: {only_one}")
    print(f"Neither choice filled: {neither}")
    print(f"\nExported: {summary_path}")
    print(f"Exported: {cleaned_path}")


if __name__ == "__main__":
    main()
