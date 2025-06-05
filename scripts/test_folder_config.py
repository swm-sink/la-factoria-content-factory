#!/usr/bin/env python3
"""Test Google Drive folder configuration."""

import os
import sys

from dotenv import load_dotenv

# Load environment variables
load_dotenv()


def test_folder_config():
    """Test that all required folder IDs are configured."""
    print("🔍 Testing Google Drive Folder Configuration")
    print("=" * 50)

    # Check environment variables
    folder_configs = {
        "DRIVE_FOLDER_ID": "Parent folder",
        "DRIVE_INPUT_FOLDER_ID": "📥 Input folder",
        "DRIVE_OUTPUT_FOLDER_ID": "📦 Output folder",
        "DRIVE_ARCHIVE_FOLDER_ID": "✅ Archive folder",
    }

    all_configured = True

    for env_var, description in folder_configs.items():
        value = os.getenv(env_var)
        if value and value != f"YOUR_{env_var}":
            print(f"✅ {description}: {value}")
        else:
            print(f"❌ {description}: NOT CONFIGURED")
            all_configured = False

    print("\n" + "=" * 50)

    if all_configured:
        print("🎉 All folder IDs are properly configured!")
        print("\n📁 Folder URLs:")
        print(
            f"   📥 Input: https://drive.google.com/drive/folders/{os.getenv('DRIVE_INPUT_FOLDER_ID')}"
        )
        print(
            f"   📦 Output: https://drive.google.com/drive/folders/{os.getenv('DRIVE_OUTPUT_FOLDER_ID')}"
        )
        print(
            f"   ✅ Archive: https://drive.google.com/drive/folders/{os.getenv('DRIVE_ARCHIVE_FOLDER_ID')}"
        )
        print("\n✨ Future content will be organized properly in the Output folder!")
        return True
    else:
        print("❌ Some folder IDs are missing. Please run setup script.")
        return False


if __name__ == "__main__":
    success = test_folder_config()
    sys.exit(0 if success else 1)
