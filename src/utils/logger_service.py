import sys
import os
import subprocess
import datetime
import threading

# Global flag to ensure we don't double-spawn everything on reloads
_LOGGING_INITIALIZED = False
_LOG_LOCK = threading.Lock()

class DualLogger:
    """Redirects writes to both a file and the original stream (stdout/stderr)."""
    def __init__(self, filepath, original_stream):
        self.file = open(filepath, 'a', encoding='utf-8', buffering=1)
        self.terminal = original_stream

    def write(self, message):
        try:
            self.terminal.write(message)
        except:
            pass
        
        try:
            self.file.write(message)
        except:
            pass 

    def flush(self):
        try:
            self.terminal.flush()
        except:
            pass
        try:
            self.file.flush()
        except:
            pass

    def close(self):
        try:
            self.file.close()
        except:
            pass

def start_global_logging():
    """
    Sets up global logging to a file and spawns a separate PowerShell window to tail it.
    Should be called once at application startup.
    """
    global _LOGGING_INITIALIZED
    
    with _LOG_LOCK:
        if _LOGGING_INITIALIZED:
            return

        try:
            # 1. Setup Log File
            # Move up two levels from src/utils to get to root/logs
            root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
            log_dir = os.path.join(root_dir, "logs")
            os.makedirs(log_dir, exist_ok=True)
            log_file = os.path.join(log_dir, "engine.log")

            # Initialize/Truncate log file
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            with open(log_file, 'w', encoding='utf-8') as f:
                f.write(f"=== Smarketer Pro Global Log Started: {timestamp} ===\n\n")

            # 2. Redirect stdout/stderr globally
            # Only redirect if not already redirected
            if not isinstance(sys.stdout, DualLogger):
                sys.stdout = DualLogger(log_file, sys.stdout)
            
            if not isinstance(sys.stderr, DualLogger):
                sys.stderr = DualLogger(log_file, sys.stderr)

            # 3. Spawn The Window
            # Only on Windows for now, and only if enabled in config
            if sys.platform == 'win32':
                try:
                    # Deferred import to ensure config is loaded
                    from config import config
                    should_spawn = config.get('logging', {}).get('spawn_background_window', False)
                except ImportError:
                    should_spawn = False
                
                if should_spawn:
                    # Check if window already exists to prevent duplicates
                    check_cmd = 'powershell -Command "Get-Process | Where-Object {$_.MainWindowTitle -eq \'Smarketer Pro Background Activity\'} | Select-Object -ExpandProperty Id"'
                    try:
                        existing_pid = subprocess.check_output(check_cmd, shell=True).decode().strip()
                    except:
                        existing_pid = ""

                    if not existing_pid:
                        print("[System] Spawning Background Terminal Window...")
                        cmd = f'start powershell -NoExit -Command "$host.UI.RawUI.WindowTitle = \'Smarketer Pro Background Activity\'; Get-Content -Path \'{log_file}\' -Wait"'
                        subprocess.Popen(cmd, shell=True)
                    else:
                        print(f"[System] Log window already active (PID: {existing_pid}). Skipping spawn.")
                else:
                    print("[System] Background log window disabled by config.")

            print("[System] Global logging initialized.")
            _LOGGING_INITIALIZED = True

        except Exception as e:
            # Fallback print to original stdout if possible, or just fail silently
            try:
                sys.__stdout__.write(f"Failed to init global logging: {e}\n")
            except:
                pass

import logging

def get_logger(name):
    """
    Returns a standard Python logger configured to write to the global log file and console.
    """
    logger = logging.getLogger(name)
    
    # prevent adding handlers multiple times
    if logger.hasHandlers():
        return logger
        
    logger.setLevel(logging.DEBUG)
    
    # Formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # 1. File Handler (pointing to the same engine.log)
    root_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    log_file = os.path.join(root_dir, "logs", "engine.log")
    
    try:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(formatter)
        file_handler.setLevel(logging.DEBUG)
        logger.addHandler(file_handler)
    except Exception as e:
        print(f"Failed to attach file handler to logger {name}: {e}")

    # 2. Console Handler (so it shows in the background window via DualLogger redirection)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    console_handler.setLevel(logging.INFO) # Keep console cleaner
    logger.addHandler(console_handler)
    
    return logger
