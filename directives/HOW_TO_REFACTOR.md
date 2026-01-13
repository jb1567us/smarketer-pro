# Refactoring Protocol

To ensure "things don't get lost" when refactoring, we use the **Golden Master** technique and a **Legacy Keeper** log.

## ⚡ Quick Start

1. **Create a refactoring script**:

   ```bash
   mkdir -p directives/refactor_sessions
   cp directives/refactoring_template.py directives/refactor_sessions/refactor_NAME.py
   ```

2. **Configure the script**:
   - Open your new script.
   - Import the function you want to change: `from src.my_module import my_function`.
   - Add some test inputs in the `test_inputs` list.

3. **Record Baseline (Golden Master)**:
   - Run this **BEFORE** you touch any code.

   ```bash
   python directives/refactor_sessions/refactor_NAME.py --record
   ```

   - This saves a snapshot of the current behavior to `fixtures/goldens/`.

4. **Refactor**:
   - Make your improvements to the code.
   - If you delete logic, consider using `LegacyKeeper` to log why:

     ```python
     from refactor_tools import LegacyKeeper
     LegacyKeeper().archive_code("old_logic", "if x: ...", "Obsolete")
     ```

5. **Verify**:
   - Run this **AFTER** your changes.

   ```bash
   python directives/refactor_sessions/refactor_NAME.py --verify
   ```

   - If it passes, you haven't broken the existing behavior!

## 🚀 Performance Tips

- **Mock Slow Operations**: If the function you are refactoring makes network calls (API, Database), the recording/verifying will be slow.
  - **Recommendation**: Pass a `mock=True` flag or inject a mock object into your function so you are testing the *logic*, not the network.
  - Example: Instead of `fetch_data()`, make your function accept a data provider: `process_data(provider=mock_provider)`.

## 🛡️ Why Use This?

- **Confidence**: You know for a fact you interpreted the inputs differently or same as before.
- **Documentation**: The `refactor_sessions` folder becomes a history of what was refactored and how it was tested.
- **Safety**: Prevents regression in complex logic (like "Orchestrator" or "Discovery Engine") where unit tests might be missing.
