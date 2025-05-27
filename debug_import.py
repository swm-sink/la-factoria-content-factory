import os
from unittest.mock import patch

print("Starting import debug script...")

# Temporarily patch os.environ to provide a dummy GCP_PROJECT_ID during import
try:
    with patch.dict("os.environ", {"GCP_PROJECT_ID": "dummy-project-id"}):
        print("Patching os.environ with dummy GCP_PROJECT_ID...")
        # Attempt to import main.py
        from main import app

        print("Successfully imported main.py")
except ValueError as e:
    print(f"Caught ValueError during import: {e}")
except Exception as e:
    print(f"Caught unexpected exception during import: {e}")

print("Debug script finished.")
