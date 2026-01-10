"""Validate JSON/JSONL files against a schema in /schemas.

Usage:
  python scripts/validate_json.py --schema leadrecord --in data.jsonl
"""
import argparse, json, sys, pathlib
from jsonschema import validate, Draft202012Validator

SCHEMA_MAP = {
    "leadrecord": "schemas/leadrecord.schema.json",
    "creativespec": "schemas/creativespec.schema.json",
    "trackingevent": "schemas/trackingevent.schema.json"
}

def iter_items(path):
    p = pathlib.Path(path)
    text = p.read_text(encoding="utf-8").strip()
    if text.startswith("{"):
        yield json.loads(text)
    else:
        # JSONL
        for line in text.splitlines():
            line = line.strip()
            if line:
                yield json.loads(line)

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--schema", required=True, choices=SCHEMA_MAP.keys())
    ap.add_argument("--in", dest="infile", required=True)
    args = ap.parse_args()

    schema_path = pathlib.Path(SCHEMA_MAP[args.schema])
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    validator = Draft202012Validator(schema)

    ok = True
    for idx, obj in enumerate(iter_items(args.infile), 1):
        errors = sorted(validator.iter_errors(obj), key=lambda e: e.path)
        if errors:
            ok = False
            print(f"[FAIL] item {idx}")
            for e in errors:
                loc = "/".join([str(x) for x in e.absolute_path]) or "(root)"
                print(f"  - {loc}: {e.message}")
        else:
            print(f"[PASS] item {idx}")
    sys.exit(0 if ok else 1)

if __name__ == "__main__":
    main()
