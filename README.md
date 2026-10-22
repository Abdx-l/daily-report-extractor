# Daily Report Extractor

Extract date, weather, crew count, hours, and delay notes from construction daily reports. Text files work directly; image input can use an installed `tesseract` executable for OCR. Validation reports field-specific errors and a review flag marks ambiguous captures.

```sh
python extract.py examples/report.txt --csv extracted.csv
python extract.py examples/report.txt --gold examples/answer.json
python -m unittest discover -s tests -v
```

The parser accepts labels such as `Date:`, `Weather:`, `Crew:`, `Hours:`, and `Delay:`. Its review flag is a heuristic based on missing labels and OCR provenance. The gold comparison reports exact field accuracy, making extraction quality measurable on a labeled set.

