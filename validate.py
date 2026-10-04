#!/usr/bin/env python3
"""
validate.py - Requirement 2: Validate rows and export a problem list.

The input file is never modified; problematic rows are written to a new file.

Usage:
    python validate.py sample_signups.csv [problems.csv]
"""

import sys
import re

import pandas as pd

# Reuse the loader delivered in Requirement 1.
from overview import load_signups, REQUIRED_COLUMNS

# Student ID: one or more ASCII digits only.
ID_PATTERN = re.compile(r"[0-9]+")
EMAIL_DOMAIN = "smbu.edu.cn"

# Bilingual reasons so the problem list is readable by both audiences.
REASON_EMPTY_ID = "学号为空 / student ID is empty"
REASON_BAD_ID = "学号不是纯数字 / student ID must contain digits only"
REASON_EMPTY_EMAIL = "邮箱为空 / email is empty"
REASON_EMAIL_MISMATCH = "邮箱与学号不匹配 / email must be {email}"
REASON_DUPLICATE_ID = "学号重复报名 / student ID appears {n} times"


def check_required_columns(df):
    """Raise a clear error if any expected column is missing."""
    missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
    if missing:
        raise ValueError(f"CSV is missing required column(s): {missing}")


def validate_dataframe(df):
    """Check every row and return a list of reason lists (one per row)."""
    check_required_columns(df)
    reasons_per_row = [[] for _ in range(len(df))]

    # Count how many times each non-empty ID occurs.
    id_counts = df["学号"].value_counts()

    for pos, (_, row) in enumerate(df.iterrows()):
        sid = row["学号"]
        email = row["邮箱"]

        # Rule 1: ID must be non-empty and digits only.
        if sid == "":
            reasons_per_row[pos].append(REASON_EMPTY_ID)
        elif ID_PATTERN.fullmatch(sid) is None:
            reasons_per_row[pos].append(REASON_BAD_ID)

        # Rule 2: email must be exactly "<学号>@smbu.edu.cn".
        expected_email = f"{sid}@{EMAIL_DOMAIN}" if sid else ""
        if email == "":
            reasons_per_row[pos].append(REASON_EMPTY_EMAIL)
        elif sid and email != expected_email:
            reasons_per_row[pos].append(
                REASON_EMAIL_MISMATCH.format(email=expected_email)
            )

        # Rule 3: duplicate registration (same non-empty ID appears > once).
        if sid and id_counts.get(sid, 0) > 1:
            reasons_per_row[pos].append(
                REASON_DUPLICATE_ID.format(n=id_counts[sid])
            )

    return reasons_per_row


def build_problem_list(df, reasons_per_row):
    """Return problematic rows plus an '问题原因 / issues' column."""
    reasons_text = ["；".join(reasons) for reasons in reasons_per_row if reasons]
    # A pandas Series mask is required so an empty mask still keeps columns.
    problem_mask = pd.Series(
        [bool(reasons) for reasons in reasons_per_row], index=df.index
    )
    problems = df.loc[problem_mask].copy()
    problems["问题原因 / issues"] = reasons_text
    return problems


def build_clean_dataframe(df, reasons_per_row):
    """Return rows that have no issues at all."""
    clean_mask = pd.Series(
        [not reasons for reasons in reasons_per_row], index=df.index
    )
    return df.loc[clean_mask].copy()


def main():
    if len(sys.argv) not in (2, 3):
        print("Usage: python validate.py <signups.csv> [problems.csv]")
        sys.exit(1)

    input_path = sys.argv[1]
    output_path = sys.argv[2] if len(sys.argv) == 3 else "problems.csv"

    df = load_signups(input_path)
    reasons_per_row = validate_dataframe(df)
    problems = build_problem_list(df, reasons_per_row)

    # utf-8-sig so Excel opens the Chinese text correctly.
    problems.to_csv(output_path, index=False, encoding="utf-8-sig")

    print(f"Checked {len(df)} row(s).")
    print(f"Problem rows: {len(problems)} -> {output_path}")
    print(f"Clean rows: {len(df) - len(problems)}")
    if len(problems) > 0:
        print("\nProblem preview:")
        print(
            problems[["姓名", "学号", "邮箱", "问题原因 / issues"]].to_string(
                index=True
            )
        )


if __name__ == "__main__":
    main()
