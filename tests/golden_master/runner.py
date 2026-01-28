import subprocess
import os
import sys

def run_script(path):
    print(f"\n--- Running {os.path.basename(path)} ---")
    try:
        # Clone current env and force UTF-8 encoding for child process IO
        child_env = os.environ.copy()
        child_env["PYTHONIOENCODING"] = "utf-8"
        
        result = subprocess.run(
            [sys.executable, path],
            capture_output=True,
            text=True,
            env=child_env,
            encoding='utf-8'
        )
        print(result.stdout)
        if result.stderr:
            print("Errors/Warnings:")
            print(result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"Failed to run {path}: {e}")
        return False

def main():
    print("Starting Golden Master Grandmaster Verification Suite\n")
    
    scripts = [
        "tests/golden_master/verify_maps.py",
        "tests/golden_master/verify_scraper.py",
        "tests/golden_master/verify_agents.py",
        "tests/golden_master/verify_social.py",
        "tests/golden_master/verify_core.py",
        "tests/golden_master/verify_pinterest.py",
        "tests/golden_master/verify_exports.py",
        "tests/golden_master/verify_infrastructure.py"
    ]
    
    passed = 0
    failed = 0
    
    for script in scripts:
        if not os.path.exists(script):
            print(f"Warning: Script {script} not found, skipping.")
            continue
            
        if run_script(script):
            passed += 1
        else:
            failed += 1
            
    print("\n" + "=" * 40)
    print(f"FINAL SUMMARY: {passed} PASSED, {failed} FAILED")
    print("=" * 40)
    
    if failed > 0:
        sys.exit(1)
    else:
        sys.exit(0)

if __name__ == "__main__":
    main()
