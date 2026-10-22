"""Parse construction report fields from text or optional OCR."""
import argparse
import csv
import json
import re
import subprocess
from datetime import date
from pathlib import Path


FIELDS = {"date": r"date", "weather": r"weather|conditions", "crew": r"crew|workers", "hours": r"hours|shift", "delay": r"delay|delays"}


def read_text(path):
    path = Path(path)
    if path.suffix.lower() in (".png", ".jpg", ".jpeg", ".tif", ".tiff"):
        result = subprocess.run(["tesseract", str(path), "stdout"], capture_output=True, text=True, check=True)
        return result.stdout, True
    return path.read_text(encoding="utf-8"), False


def extract(text, ocr=False):
    values = {}
    for line in text.splitlines():
        for field, label in FIELDS.items():
            match = re.match(rf"\s*(?:{label})\s*:\s*(.*?)\s*$", line, re.IGNORECASE)
            if match and field not in values:
                values[field] = match.group(1)
    errors = []
    try:
        values["date"] = date.fromisoformat(values["date"]).isoformat()
    except (KeyError, ValueError):
        errors.append("date: expected YYYY-MM-DD")
    for field, maximum in (("crew", 10000), ("hours", 24)):
        try:
            number = float(values[field])
            if not 0 <= number <= maximum or (field == "crew" and not number.is_integer()):
                raise ValueError()
            values[field] = int(number) if field == "crew" else number
        except (KeyError, ValueError):
            errors.append(f"{field}: expected 0..{maximum}" + (" integer" if field == "crew" else ""))
    if not values.get("weather"):
        errors.append("weather: missing")
    values.setdefault("delay", "")
    return {"fields": values, "errors": errors, "review": bool(errors or ocr or len(values.get("delay", "")) > 120)}


def score(result, gold):
    keys = ("date", "weather", "crew", "hours", "delay")
    correct = {key: result["fields"].get(key) == gold.get(key) for key in keys}
    return {"correct": correct, "accuracy": sum(correct.values()) / len(keys)}


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("input")
    p.add_argument("--csv")
    p.add_argument("--gold")
    a = p.parse_args()
    text, ocr = read_text(a.input)
    result = extract(text, ocr)
    if a.csv:
        with open(a.csv, "w", newline="", encoding="utf-8") as file:
            writer = csv.DictWriter(file, fieldnames=["source", *FIELDS, "review", "errors"])
            writer.writeheader()
            writer.writerow({"source": a.input, **result["fields"], "review": result["review"], "errors": "; ".join(result["errors"])})
    if a.gold:
        result["evaluation"] = score(result, json.loads(Path(a.gold).read_text(encoding="utf-8")))
    print(json.dumps(result, indent=2))
    raise SystemExit(bool(result["errors"]))


if __name__ == "__main__":
    main()

