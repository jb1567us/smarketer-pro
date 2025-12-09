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
    # Role ID: technical_lead
    # Role Label: Technical Lead
    # Purpose: Design the technical architecture and implementation

    base_dir = Path(__file__).resolve().parents[1]
    control_path = base_dir / "control.md"
    artifacts_dir = base_dir / "artifacts"
    artifacts_dir.mkdir(parents=True, exist_ok=True)

    if not control_path.exists():
        raise FileNotFoundError("control.md not found. Generate it first (option 3 in run.bat).")

    control_text = control_path.read_text(encoding="utf-8")

    system_prompt = (
        "You are the Technical Lead for this project. "
        "Your purpose: Design the technical architecture and implementation"
    )

    user_prompt = (
        "Here is the current Control Doc:\n\n"
        + control_text
        + "\n\n"
        "Produce a single, coherent artifact for the role 'Technical Lead'. "
        "Make it directly useful with minimal filler. "
        "Output ONLY the artifact content (no commentary)."
    )

    try:
        content = model_client.generate_text(system_prompt, user_prompt, task="coding")
    except ModelClientError as e:
        raise SystemExit(f"Error generating artifact for Technical Lead: {e}")

    out_file = artifacts_dir / "technical_lead_artifact_v0.1.md"
    out_file.write_text(content, encoding="utf-8")
    print("Wrote artifact for role 'Technical Lead' to:", out_file)


if __name__ == "__main__":
    main()
