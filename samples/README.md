# Sample data for dataclean

- `employee_data.txt` — raw dirty sample (comma-separated, duplicate rows, missing ages,
  missing dates, mixed date formats).
- `rules.yaml` — example cleaning rules.

Run:

    dataclean clean samples/employee_data.txt --rules samples/rules.yaml --out /tmp/cleaned.csv --report markdown