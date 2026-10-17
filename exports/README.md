# Exports

`make final-check` requires two files here: `PRD.pdf` and `RICE.pdf`.

```bash
make pdf        # renders 06_PRD.md and the ranked RICE table (with every assumption) through headless Chrome
```

No pandoc needed. If Chrome or Chromium is not installed, open the Markdown in any preview, **Print to PDF**, and save as `exports/PRD.pdf`
and `exports/RICE.pdf` (for RICE, run `make rice` and print its table).

Regenerate both after any change to the PRD or the RICE inputs: the numbers in them must match `reports/metrics.json`.
