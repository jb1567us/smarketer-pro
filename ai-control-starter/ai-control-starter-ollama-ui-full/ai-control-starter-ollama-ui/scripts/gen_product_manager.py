import json
import sys
from pathlib import Path

# Add the parent directory to Python path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

try:
    import model_client
    from model_client import ModelClientError
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


def main():
    # Role-specific generator script.
    # Role ID: product_manager
    # Role Label: Product Manager
    # Purpose: Define product requirements and user experience

    base_dir = Path(__file__).resolve().parents[1]
    control_path = base_dir / "control.md"
    artifacts_dir = base_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    if not control_path.exists():
        raise FileNotFoundError("control.md not found. Generate it first (option 3 in run.bat).")

    control_text = control_path.read_text(encoding="utf-8")

    system_prompt = (
        "You are the Product Manager for this project. "
        "Your purpose: Define product requirements and user experience"
    )

    user_prompt = (
        "Here is the current Control Doc:\n\n"
        + control_text
        + "\n\n"
        "Produce a single, coherent artifact for the role 'Product Manager'. "
        "Make it directly useful with minimal filler. "
        "Output ONLY the artifact content (no commentary)."
    )

    try:
        content = model_client.generate_text(system_prompt, user_prompt, task="coding")
    except ModelClientError as e:
        raise SystemExit(f"Error generating artifact for Product Manager: {e}")

    out_file = artifacts_dir / "product_manager_artifact_v0.1.md"
    out_file.write_text(content, encoding="utf-8")
    print("Wrote artifact for role 'Product Manager' to:", out_file)


if __name__ == "__main__":
    main()
