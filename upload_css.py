#!/usr/bin/env python3
"""Upload the custom CSS file to Trilium as a CSS code note with #appCss label."""

import os
import sys
from pathlib import Path
from trilium_py.client import ETAPI


def load_env_file(env_path: Path) -> dict:
    """Load environment variables from .env file."""
    env_vars = {}
    if env_path.exists():
        with open(env_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    if '=' in line:
                        key, value = line.split('=', 1)
                        env_vars[key] = value
    return env_vars


def upload_css_to_trilium(server_url: str, token: str, css_file: Path, parent_note_id: str = "root"):
    """
    Upload CSS file to Trilium as a CSS code note.

    Args:
        server_url: Trilium server URL
        token: ETAPI token
        css_file: Path to CSS file
        parent_note_id: Parent note ID (default: root)
    """
    # Initialize Trilium API
    ea = ETAPI(server_url, token)

    # Read CSS file content
    with open(css_file, 'r', encoding='utf-8') as f:
        css_content = f.read()

    # Check if we have a saved CSS note ID
    css_note_id_file = css_file.parent / ".css_note_id"
    existing_note_id = None

    if css_note_id_file.exists():
        with open(css_note_id_file, 'r') as f:
            existing_note_id = f.read().strip()

    # Try to update existing note if we have an ID
    if existing_note_id:
        print(f"🔍 Found tracked CSS note ID: {existing_note_id}")
        try:
            ea.update_note_content(existing_note_id, css_content)
            print(f"✅ Updated CSS content in existing note")
            return existing_note_id
        except Exception as e:
            print(f"⚠️  Could not update existing note (may have been deleted): {e}")
            print("📝 Creating new note instead...")

    # Create new CSS note
    print("📝 Creating new 'custom' CSS note...")
    note_data = {
        "parentNoteId": parent_note_id,
        "title": "custom",
        "type": "code",
        "mime": "text/css",
        "content": css_content
    }

    try:
        response = ea.create_note(**note_data)
        if response and 'note' in response:
            note_id = response['note']['noteId']
            print(f"✅ Created CSS note (ID: {note_id})")

            # Add #appCss label
            print("🏷️  Adding #appCss label...")
            ea.create_attribute(
                noteId=note_id,
                type="label",
                name="appCss",
                value="",
                isInheritable=False
            )
            print(f"✅ Added #appCss label")

            # Save note ID for future updates
            with open(css_note_id_file, 'w') as f:
                f.write(note_id)
            print(f"💾 Saved CSS note ID for future updates")

            return note_id
        else:
            print(f"❌ Failed to create CSS note")
            return None
    except Exception as e:
        print(f"❌ Error creating CSS note: {e}")
        return None


def main():
    """Main function."""
    script_dir = Path(__file__).parent
    css_file = script_dir / ".css"

    # Check if CSS file exists
    if not css_file.exists():
        print(f"❌ Error: CSS file not found at {css_file}")
        sys.exit(1)

    # Load configuration from .env file
    env_file = script_dir / ".env"
    if not env_file.exists():
        print(f"❌ Error: .env file not found at {env_file}")
        print("Please create a .env file with your Trilium configuration")
        sys.exit(1)

    env_vars = load_env_file(env_file)

    # Get configuration
    token = env_vars.get('TRILIUM_TOKEN')
    server_url = env_vars.get('TRILIUM_SERVER', 'http://localhost:8080')
    parent_note_id = env_vars.get('TRILIUM_PARENT_NOTE', 'root')

    if not token:
        print("❌ Error: TRILIUM_TOKEN not set in .env file")
        sys.exit(1)

    print("=" * 60)
    print("Uploading Custom CSS to Trilium")
    print("=" * 60)
    print(f"CSS File: {css_file}")
    print(f"Server: {server_url}")
    print(f"Parent: {parent_note_id}")
    print()

    # Upload CSS
    note_id = upload_css_to_trilium(server_url, token, css_file, parent_note_id)

    if note_id:
        print()
        print("=" * 60)
        print("✅ SUCCESS!")
        print("=" * 60)
        print(f"CSS note created/updated with ID: {note_id}")
        print()
        print("The custom CSS is now active in Trilium.")
        print("Callout blocks will render with proper styling and emoji icons.")
    else:
        print()
        print("=" * 60)
        print("❌ FAILED")
        print("=" * 60)
        print("Could not upload CSS to Trilium")
        sys.exit(1)


if __name__ == "__main__":
    main()
