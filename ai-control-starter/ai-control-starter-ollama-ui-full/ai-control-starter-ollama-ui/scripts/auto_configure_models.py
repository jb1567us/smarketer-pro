import json
import subprocess
import sys
from pathlib import Path

# Add the parent directory to Python path
BASE_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(BASE_DIR))

try:
    import psutil  # from requirements.txt
except ImportError as e:
    print(f"Import error: {e}")
    sys.exit(1)


CONFIG_PATH = BASE_DIR / "model_config.json"


def get_memory_gb() -> float:
    mem = psutil.virtual_memory().total
    return mem / (1024 ** 3)


def detect_profile() -> str:
    mem_gb = get_memory_gb()
    if mem_gb < 8:
        return "tiny"
    elif mem_gb < 16:
        return "small"
    elif mem_gb < 32:
        return "medium"
    else:
        return "large"


def get_installed_models() -> set:
    try:
        result = subprocess.run(
            ["ollama", "list"],
            capture_output=True,
            text=True,
            check=True,
        )
    except Exception as e:
        print("Error calling `ollama list`:", e)
        return set()

    lines = result.stdout.strip().splitlines()
    models = set()
    for line in lines[1:]:
        parts = line.split()
        if parts:
            models.add(parts[0])
    return models


def ensure_model(model_name: str, installed: set) -> str:
    if any(m.startswith(model_name) for m in installed):
        print(f"Model already installed: {model_name}")
        return model_name

    print(f"Pulling model via Ollama: {model_name} ...")
    try:
        subprocess.run(["ollama", "pull", model_name], check=True)
        print(f"Pulled model: {model_name}")
    except Exception as e:
        print(f"Warning: failed to pull model '{model_name}': {e}")
    return model_name


def main():
    profile = detect_profile()
    print(f"Detected memory profile: {profile} (RAM ≈ {get_memory_gb():.1f} GB)")

    recommended = {
        "tiny": {
            "planning": ["phi3", "llama3"],
            "coding": ["deepseek-coder", "codellama", "llama3"],
            "utility": ["phi3", "llama3"],
        },
        "small": {
            "planning": ["llama3", "phi3"],
            "coding": ["codellama", "deepseek-coder", "llama3"],
            "utility": ["phi3", "llama3"],
        },
        "medium": {
            "planning": ["llama3", "llama2"],
            "coding": ["codellama", "deepseek-coder", "llama3"],
            "utility": ["llama3", "phi3"],
        },
        "large": {
            "planning": ["llama3", "llama2"],
            "coding": ["codellama", "deepseek-coder", "llama3"],
            "utility": ["llama3", "phi3"],
        },
    }

    rec = recommended.get(profile, recommended["small"])

    installed = get_installed_models()
    print("Installed models detected:", installed or "(none or error)")

    chosen = {}
    for task, candidates in rec.items():
        for model in candidates:
            chosen_model = ensure_model(model, installed)
            chosen[task] = chosen_model
            break

    default_model = chosen.get("planning") or "llama3"

    config = {
        "backend": "ollama",
        "default_model": default_model,
        "tasks": chosen,
    }

    CONFIG_PATH.write_text(json.dumps(config, indent=2), encoding="utf-8")

    print("\nWrote model_config.json with:")
    print(json.dumps(config, indent=2))


if __name__ == "__main__":
    main()