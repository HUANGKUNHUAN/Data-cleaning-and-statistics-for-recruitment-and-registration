# Association Signup CSV Tool

A small command-line tool that processes the hundreds of signup forms exported
by the registration questionnaire each year. The tool is built in three
incremental steps, each delivered as a separate pull request:

| PR | Requirement | Script |
|----|-------------|--------|
| 1 | Load & overview | `overview.py` |
| 2 | Validate & clean | `validate.py` |
| 3 | Statistics & export | `stats.py` |

## Assumptions

The questionnaire export was not fully specified, so the following assumptions
are made. They are listed here on purpose per the task instructions.

1. **CSV columns** are exactly: `姓名`, `学号`, `邮箱`, `志愿1`, `志愿2`,
   `推荐人`. Leading/trailing spaces in headers and cells are stripped.
2. **Encoding** is UTF-8 (a BOM is tolerated, `utf-8-sig`); if that fails,
   GBK is tried as a fallback.
3. **Student ID (`学号`)** must contain digits only (`0-9`). There is **no
   fixed length** — 8-digit and 10-digit IDs both pass. IDs are read as text
   so leading zeros are preserved.
4. **Email (`邮箱`)** must be exactly `学号@smbu.edu.cn`, e.g. student
   `20240101` must use `20240101@smbu.edu.cn`. The comparison is case
   sensitive; any mismatch is treated as a typo.
5. **Empty values** include blank cells and whitespace-only cells. Empty
   `志愿2` / `推荐人` are normal (they are optional fields), not errors.
6. **Duplicate student ID**: every row whose `学号` appears more than once is
   sent to the problem list (including all occurrences), so the duplicates can
   be reviewed manually. None of the rows are deleted automatically.
7. **The input file is never modified.** The tool only reads it; every result
   is written to a new file.
8. **Cleaned data** means rows that pass all validation rules (valid ID,
   matching email, not part of a duplicate ID).

## Requirements

- Python 3.8 or newer
- pandas (see `requirements.txt`)

## Installation

```bash
python -m venv .venv
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# macOS / Linux
source .venv/bin/activate

pip install -r requirements.txt
```

## Usage

### 1. Load & overview

Prints how many rows the file contains, how many empty cells each column has,
and whether there are fully duplicate rows.

```bash
python overview.py sample_signups.csv
```

The file `sample_signups.csv` is a small sample included in the repo. It
contains deliberately problematic rows (bad IDs, mismatched emails, duplicate
IDs, fully duplicate rows, padded whitespace) so the tool can be tried without
real data. Replace it with the real questionnaire export when needed.

### 2. Validate & clean

Checks each row against the rules and exports a problem list. The input file
is never modified.

- `学号` must be non-empty and digits only;
- `邮箱` must be exactly `学号@smbu.edu.cn`;
- every row whose `学号` appears more than once is flagged as a duplicate
  signup (all occurrences, for manual review).

```bash
python validate.py sample_signups.csv
```

Outputs `problems.csv`: one row per problematic signup, keeping the original
columns plus `问题原因 / issues`, which lists every reason why the row failed.
An optional second argument sets a different output path.

### 3. Statistics & export

Runs validation first, then reports statistics on the cleaned data:

```bash
python stats.py sample_signups.csv
```

- prints and exports `first_choice_summary.csv` — applicant count grouped by
  `志愿1`;
- prints how many people filled **both** `志愿1` and `志愿2`, and how many
  filled **exactly one** (people who filled neither are also reported for
  completeness);
- exports the fully cleaned dataset as `cleaned.csv`.

An optional second argument sets an output directory.

## Output files

| File | Meaning |
|------|---------|
| `problems.csv` | Problem list: every problematic row with all failure reasons. |
| `first_choice_summary.csv` | Number of applicants per first choice. |
| `cleaned.csv` | Clean dataset: rows that pass every validation rule. |

These generated files are git-ignored; run the commands above to recreate them.

## Project structure

```
signup-tool/
├── overview.py          # PR1: load & overview
├── validate.py          # PR2: validate & export problem list
├── stats.py             # PR3: statistics & export cleaned data
├── sample_signups.csv   # sample data with edge cases
├── requirements.txt
└── README.md
```
