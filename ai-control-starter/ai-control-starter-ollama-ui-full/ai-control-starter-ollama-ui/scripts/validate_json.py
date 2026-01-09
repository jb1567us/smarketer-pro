import json
import argparse
from pathlib import Path

from jsonschema import Draft7Validator


def load_schema(name: str, base_dir: Path) -> dict:
    schema_path = base_dir / "schemas" / f"{name}.schema.json"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schema file not found: {schema_path}")
    return json.loads(schema_path.read_text(encoding="utf-8"))


def main():
    ap = argparse.ArgumentParser(description="Validate JSON/JSONL against a schema.")
    ap.add_argument("--schema", required=True, help="Schema base name (e.g. 'creativespec')")
    ap.add_argument("--in", dest="infile", required=True, help="Path to JSON or JSONL file.")
    args = ap.parse_args()

    base_dir = Path(__file__).resolve().parents[1]
    schema = load_schema(args.schema, base_dir)

    infile = Path(args.infile)
    if not infile.exists():
        raise FileNotFoundError(f"Input file not found: {infile}")

    data = []
    if infile.suffix.lower() == ".jsonl":
        for line in infile.read_text(encoding="utf-8").splitlines():
            if line.strip():
                data.append(json.loads(line))
    else:
        contents = infile.read_text(encoding="utf-8")
        parsed = json.loads(contents)
        if isinstance(parsed, list):
            data = parsed
        else:
            data = [parsed]

    validator = Draft7Validator(schema)
    errors_found = False

    for idx, item in enumerate(data):
        errors = sorted(validator.iter_errors(item), key=lambda e: e.path)
        if errors:
            errors_found = True
            print(f"Record {idx} has errors:")
            for e in errors:
                print("  -", e.message)

    if not errors_found:
        print("All records are valid against schema", args.schema)


if __name__ == "__main__":
    main()
