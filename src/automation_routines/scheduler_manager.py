
import platform
import subprocess
import os
import sys

def get_python_path():
    return sys.executable

def get_script_path():
    # Assumes valid structure relative to this file
    current_dir = os.path.dirname(os.path.abspath(__file__))
    script_path = os.path.join(current_dir, "daily_health_check.py")
    return script_path

def setup_windows_task():
    print("🖥️  Detected Windows Environment.")
    print("   Setting up Windows Task Scheduler for Daily Health Check...")
    
    task_name = "B2B_Outreach_DailyHealthCheck"
    python_exe = get_python_path()
    script_path = get_script_path()
    
    # Using schtasks is often more reliable than PowerShell from python subprocess
    # /SC DAILY /TN "Name" /TR "path" /ST 07:00 /F
    
    # We need to wrap the command to ensure it runs in the right directory or setting PYTHONPATH
    # easier: pass the working dir to the action? schtasks doesn't easily support working dir in simple /TR.
    # So we used the fixed import in daily_health_check.py (sys.path.append) to handle this.
    
    command = f'schtasks /create /sc DAILY /tn "{task_name}" /tr "\'{python_exe}\' \'{script_path}\'" /st 07:00 /f'
    
    print(f"   Executing: {command}")
    
    try:
        # shell=True to allow command parsing
        result = subprocess.run(command, shell=True, capture_output=True, text=True)
        
        if result.returncode == 0:
            print(f"✅ SUCCESS: Task '{task_name}' scheduled daily at 7:00 AM.")
            print("   You can manage this in the 'Task Scheduler' app.")
            print("   Run manually: schtasks /run /tn \"B2B_Outreach_DailyHealthCheck\"")
        else:
            print("❌ FAILURE: Could not create task.")
            print(f"   Error: {result.stderr}")
            print("   Hint: You might need to run this script as Administrator.")
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")

def setup_cron_task():
    print("🐧 Detected Unix-like Environment.")
    
    python_exe = get_python_path()
    script_path = get_script_path()
    
    cron_line = f"0 7 * * * {python_exe} {script_path} >> {os.path.dirname(script_path)}/daily_health.log 2>&1"
    
    print("   Cron jobs must be added manually to your user's crontab.")
    print("\n   📋 COPY THIS LINE:")
    print(f"   {cron_line}")
    print("\n   👉 ACTION: Run 'crontab -e' and paste the line above at the bottom.")

if __name__ == "__main__":
    print("--- WordPress Automation Scheduler Setup ---")
    
    if platform.system() == "Windows":
        setup_windows_task()
    else:
        setup_cron_task()
