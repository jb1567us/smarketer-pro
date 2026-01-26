import subprocess
import os
import tempfile
import typing

class NativeProxyDriver:
    """
    Driver for the high-performance Go-based proxy engine.
    """
    def __init__(self):
        # Path to the compiled engine
        self.engine_path = os.path.join(os.path.dirname(__file__), 'engine', 'proxy_engine.exe')
        
    def check_proxies(self, proxies: typing.List[str], workers: int = 200, timeout_ms: int = 5000) -> typing.List[str]:
        """
        Runs the sidecar engine to check proxies.
        Returns a list of working proxies.
        """
        if not os.path.exists(self.engine_path):
            raise FileNotFoundError(f"Proxy engine not found at {self.engine_path}. Please re-compile.")

        if not proxies:
            return []

        # Create temp files for input/output
        with tempfile.NamedTemporaryFile(mode='w+', delete=False, suffix='.txt') as input_file:
            input_path = input_file.name
            for p in proxies:
                input_file.write(p + "\n")
        
        output_path = input_path + ".out"

        try:
            # Run the engine
            cmd = [
                self.engine_path,
                "-input", input_path,
                "-output", output_path,
                "-workers", str(workers),
                "-timeout", str(timeout_ms)
            ]
            
            # Run silently (capture output)
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Engine failed: {result.stderr}")
                return []

            # Read results
            working_proxies = []
            if os.path.exists(output_path):
                with open(output_path, 'r') as f:
                    working_proxies = [line.strip() for line in f if line.strip()]
            
            print(f"Engine checked {len(proxies)} proxies. Found {len(working_proxies)} working.")
            return working_proxies

        finally:
            # Cleanup
            if os.path.exists(input_path):
                os.remove(input_path)
            if os.path.exists(output_path):
                os.remove(output_path)

if __name__ == "__main__":
    # Self-test
    driver = NativeProxyDriver()
    test_proxies = ["http://google.com:80", "127.0.0.1:9000", "8.8.8.8:53"] # Fake proxies
    print("Running test...")
    results = driver.check_proxies(test_proxies, timeout_ms=1000)
    print("Results:", results)
