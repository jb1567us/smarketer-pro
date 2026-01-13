import json
import os
import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
import inspect

class GoldenMaster:
    def __init__(self, snapshot_dir: str = "snapshots"):
        self.snapshot_dir = Path(snapshot_dir)
        self.snapshot_dir.mkdir(parents=True, exist_ok=True)

    def _default_serializer(self, obj):
        """Helper to serialize non-JSON objects."""
        if isinstance(obj, (datetime.date, datetime.datetime)):
            return obj.isoformat()
        if hasattr(obj, '__dict__'):
            return str(obj)
        return str(obj)

    def record(self, func: Callable, inputs: List[Dict[str, Any]], snapshot_name: str) -> str:
        """
        Runs the function with provided inputs and saves the output to a JSON snapshot.
        
        Args:
            func: The function to test.
            inputs: A list of kwargs dictionaries to pass to the function.
            snapshot_name: unique name for this test case.
            
        Returns:
            Path to the saved snapshot file.
        """
        results = []
        for i, kwargs in enumerate(inputs):
            try:
                output = func(**kwargs)
                status = "success"
            except Exception as e:
                output = str(e)
                status = "error"
            
            results.append({
                "input_index": i,
                "input_args": kwargs,
                "status": status,
                "output": output
            })

        data = {
            "timestamp": datetime.datetime.now().isoformat(),
            "function_name": func.__name__,
            "snapshot_name": snapshot_name,
            "results": results
        }

        filepath = self.snapshot_dir / f"{snapshot_name}.json"
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=self._default_serializer)
        
        return str(filepath)

    def verify(self, func: Callable, snapshot_name: str) -> bool:
        """
        Re-runs the function using inputs from the snapshot and compares outputs.
        
        Returns:
            True if match, False (and prints diff) if mismatch.
        """
        filepath = self.snapshot_dir / f"{snapshot_name}.json"
        if not filepath.exists():
            print(f"❌ Snapshot '{snapshot_name}' not found at {filepath}")
            return False

        with open(filepath, 'r', encoding='utf-8') as f:
            snapshot_data = json.load(f)

        print(f"🔍 Verifying '{snapshot_name}' against snapshot from {snapshot_data['timestamp']}...")
        
        all_passed = True
        
        for result in snapshot_data['results']:
            kwargs = result['input_args']
            expected_output = result['output']
            expected_status = result['status']

            try:
                actual_output = func(**kwargs)
                actual_status = "success"
            except Exception as e:
                actual_output = str(e)
                actual_status = "error"

            # Normalize for comparison (JSON roundtrip simulation)
            # This handles cases where original output was a tuple but JSON made it a list
            # or custom objects became strings.
            try:
                normalized_actual = json.loads(json.dumps(actual_output, default=self._default_serializer))
            except:
                normalized_actual = str(actual_output)

            if actual_status != expected_status or normalized_actual != expected_output:
                print(f"  ❌ Mismatch for input: {kwargs}")
                print(f"     Expected ({expected_status}): {expected_output}")
                print(f"     Actual   ({actual_status}): {normalized_actual}")
                all_passed = False
            
        if all_passed:
            print(f"✅ verification successful: {len(snapshot_data['results'])} inputs matched.")
            return True
        else:
            print(f"❌ Verification FAILED for '{snapshot_name}'")
            return False
