import os
import json
from typing import Optional
from pathlib import Path

import requests


class ModelClientError(Exception):
    pass


BASE_DIR = Path(__file__).resolve().parent
CONFIG_PATH = BASE_DIR / "model_config.json"

DEFAULT_CONFIG = {
    "backend": "ollama",
    "default_model": "llama3",
    "tasks": {
        "planning": "llama3",
        "coding": "llama3",
        "utility": "llama3"
    }
}


def load_config() -> dict:
    if not CONFIG_PATH.exists():
        return DEFAULT_CONFIG
    try:
        data = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
        merged = DEFAULT_CONFIG.copy()
        merged.update({k: v for k, v in data.items() if k in merged})
        tasks = DEFAULT_CONFIG["tasks"].copy()
        tasks.update(data.get("tasks", {}))
        merged["tasks"] = tasks
        return merged
    except Exception:
        return DEFAULT_CONFIG


def _call_ollama(system_prompt: str, user_prompt: str, model_name: str, timeout: int = 120) -> str:
    url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")

    payload = {
        "model": model_name,
        "stream": False,
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    try:
        resp = requests.post(url, json=payload, timeout=timeout)
    except Exception as e:
        raise ModelClientError(f"Error calling Ollama at {url}: {e}") from e

    if resp.status_code != 200:
        raise ModelClientError(
            f"Ollama returned status {resp.status_code}: {resp.text[:200]}"
        )

    try:
        data = resp.json()
    except json.JSONDecodeError as e:
        raise ModelClientError(f"Could not decode Ollama JSON response: {e}") from e

    message = data.get("message") or {}
    content = message.get("content")
    if not content:
        raise ModelClientError(f"Ollama response missing 'message.content': {data}")

    return content


def _choose_model(task: Optional[str], override_model: Optional[str]) -> str:
    if override_model:
        return override_model

    cfg = load_config()

    if task:
        m = cfg.get("tasks", {}).get(task)
        if m:
            return m

    if cfg.get("default_model"):
        return cfg["default_model"]

    env_model = os.getenv("OLLAMA_MODEL")
    if env_model:
        return env_model

    return "llama3"


def generate_text(
    system_prompt: str,
    user_prompt: str,
    *,
    task: Optional[str] = None,
    model: Optional[str] = None
) -> str:
    cfg = load_config()
    backend = os.getenv("MODEL_BACKEND", cfg.get("backend", "ollama")).lower()

    chosen_model = _choose_model(task, model)

    if backend == "ollama":
        return _call_ollama(system_prompt, user_prompt, chosen_model)

    raise ModelClientError(
        f"Unsupported MODEL_BACKEND='{backend}'. "
        "Use 'ollama' (default), or extend model_client.py for other backends."
    )


def generate_text_fast(
    system_prompt: str,
    user_prompt: str,
    *,
    task: Optional[str] = None,
    model: Optional[str] = None,
    timeout: int = 90  # Shorter timeout for chat
) -> str:
    """Faster version with shorter timeout for chat interactions"""
    cfg = load_config()
    backend = os.getenv("MODEL_BACKEND", cfg.get("backend", "ollama")).lower()

    chosen_model = _choose_model(task, model)

    if backend == "ollama":
        return _call_ollama_fast(system_prompt, user_prompt, chosen_model, timeout=timeout)

    raise ModelClientError(f"Unsupported MODEL_BACKEND='{backend}'")


def _call_ollama_fast(system_prompt: str, user_prompt: str, model_name: str, timeout: int = 90) -> str:
    """Ollama call with configurable timeout and faster settings"""
    url = os.getenv("OLLAMA_URL", "http://localhost:11434/api/chat")

    # Faster, focused payload for chat responses
    payload = {
        "model": model_name,
        "stream": False,
        "options": {
            "num_predict": 1024,  # Reasonable response length
            "temperature": 0.3,   # More focused responses
            "top_k": 40,          # Faster sampling
            "top_p": 0.9,         # Balanced creativity
        },
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    }

    try:
        print(f"DEBUG: Fast call to {model_name} (timeout: {timeout}s)")
        resp = requests.post(url, json=payload, timeout=timeout)
        
        if resp.status_code != 200:
            # Try fallback to phi3:mini if available
            if model_name != "phi3:mini":
                print(f"DEBUG: Model {model_name} failed, trying phi3:mini")
                try:
                    return _call_ollama_fast(system_prompt, user_prompt, "phi3:mini", timeout=60)
                except:
                    pass
            raise ModelClientError(f"Ollama returned status {resp.status_code}")

        data = resp.json()
        message = data.get("message") or {}
        content = message.get("content")
        if not content:
            raise ModelClientError("Ollama response missing content")

        print(f"DEBUG: Response received in {resp.elapsed.total_seconds():.1f}s")
        return content

    except requests.exceptions.Timeout:
        # Fallback to faster model on timeout
        if model_name != "phi3:mini":
            print(f"DEBUG: Timeout with {model_name}, falling back to phi3:mini")
            try:
                return _call_ollama_fast(system_prompt, user_prompt, "phi3:mini", timeout=60)
            except:
                raise ModelClientError(f"All models timed out")
        raise ModelClientError(f"Ollama request timed out after {timeout} seconds")
    except Exception as e:
        raise ModelClientError(f"Error calling Ollama: {e}")