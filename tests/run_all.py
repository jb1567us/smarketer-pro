import subprocess
import sys
import os
import time

def run_script(script_name):
    print(f"Testing {script_name}...", end=" ", flush=True)
    start = time.time()
    try:
        # Run process and capture output
        env = os.environ.copy()
        env["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(
            [sys.executable, script_name], 
            cwd=os.getcwd(),
            capture_output=True, 
            text=True, 
            encoding='utf-8',
            errors='replace',
            env=env,
            timeout=120 # 2 minute timeout per script
        )
        duration = time.time() - start
        
        if result.returncode == 0:
            print(f"✅ PASSED ({duration:.2f}s)")
            return True, result.stdout
        else:
            print(f"❌ FAILED ({duration:.2f}s)")
            print(f"\n--- Output of {script_name} ---\n{result.stdout}\n{result.stderr}\n-----------------------------")
            return False, result.stderr
    except subprocess.TimeoutExpired:
        print("❌ TIMEOUT")
        return False, "Timed out"
    except Exception as e:
        print(f"❌ ERROR: {e}")
        return False, str(e)

def main():
    print("========================================")
    print("    B2B Outreach Tool - System Test     ")
    print("========================================")
    
    scripts = [
        "tests/test_agents.py",
        "verify_llm.py",
        "verify_db.py",
        "verify_changes.py",
        "test_tasks.py",
        # "verify_proxy_agent.py", # Can be slow/network intensive, maybe skip for quick test or make optional?
        # "verify_seo_upgrade.py", # Also seemingly slow
        # "verify_social.py"
    ]
    
    # Check if we want to run the heavy ones
    if "--full" in sys.argv:
        scripts.extend([
            "verify_proxy_agent.py",
            "verify_seo_upgrade.py",
            "verify_social.py"
        ])
    else:
        print("(Skipping network-intensive verification scripts. Use --full to include them.)")

    passed = 0
    failed = 0
    
    for script in scripts:
        if not os.path.exists(script):
            print(f"⚠️  Skipping {script} (File not found)")
            continue
            
        success, _ = run_script(script)
        if success:
            passed += 1
        else:
            failed += 1

    print("\n========================================")
    print(f"Summary: {passed} Passed, {failed} Failed")
    print("========================================")
    
    if failed > 0:
        sys.exit(1)

if __name__ == "__main__":
    main()
