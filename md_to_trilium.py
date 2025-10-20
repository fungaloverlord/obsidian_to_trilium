"""Main application for converting Markdown directories to Trilium notes."""
import sys
import argparse
from pathlib import Path
from directory_scanner import DirectoryScanner
from trilium_uploader import TriliumUploader


class MarkdownToTrilium:
    """Main application class for Markdown to Trilium conversion."""

    def __init__(self, server_url: str, token: str):
        """
        Initialize the converter.

        Args:
            server_url: Trilium server URL
            token: ETAPI authentication token
        """
        self.server_url = server_url
        self.token = token

    def convert_directory(self, directory_path: str, parent_note_id: str = "root",
                         preview: bool = False, include_hidden: bool = False):
        """
        Convert a directory of Markdown files to Trilium notes.

        Args:
            directory_path: Path to directory containing Markdown files
            parent_note_id: Parent note ID in Trilium (default: 'root')
            preview: If True, show what would be uploaded without uploading
            include_hidden: Whether to include hidden files/folders
        """
        # Validate directory
        dir_path = Path(directory_path).resolve()
        if not dir_path.exists():
            print(f"❌ Error: Directory does not exist: {directory_path}")
            return False
        if not dir_path.is_dir():
            print(f"❌ Error: Not a directory: {directory_path}")
            return False

        # Scan directory
        print(f"\n📂 Scanning directory: {dir_path}")
        scanner = DirectoryScanner(str(dir_path), include_hidden=include_hidden)
        root_node = scanner.scan()

        if not root_node.children:
            print("⚠️  No Markdown files or subdirectories found.")
            return False

        # Show preview
        print("\n📋 Directory structure:")
        scanner.print_tree(root_node)

        markdown_files = scanner.get_all_markdown_files()
        print(f"\n📊 Found {len(markdown_files)} Markdown file(s)")

        if preview:
            print("\n👁️  Preview mode - no files uploaded.")
            return True

        # Upload to Trilium
        print(f"\n⬆️  Uploading to Trilium (parent: {parent_note_id})...")
        uploader = TriliumUploader(self.server_url, self.token)

        try:
            note_map = uploader.upload_tree(root_node, parent_note_id)
            print(f"\n✅ Successfully created {len(note_map)} note(s) in Trilium!")
            return True
        except Exception as e:
            print(f"\n❌ Error during upload: {e}")
            return False


def main():
    """CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Convert Markdown files to Trilium notes, preserving directory hierarchy."
    )
    parser.add_argument(
        "directory",
        help="Directory containing Markdown files to convert"
    )
    parser.add_argument(
        "--server",
        default="http://localhost:8080",
        help="Trilium server URL (default: http://localhost:8080)"
    )
    parser.add_argument(
        "--token",
        default="9NOzNsvFz2oH_p6uSvOqU/lMrVOtB7vaFhdqQSYLUs8TSijMw2U3Axto=",
        help="Trilium ETAPI authentication token"
    )
    parser.add_argument(
        "--parent",
        default="root", #noteID
        help="Parent note ID in Trilium (default: root)"
    )
    parser.add_argument(
        "--preview",
        action="store_true",
        help="Preview mode - show what would be uploaded without uploading"
    )
    parser.add_argument(
        "--include-hidden",
        action="store_true",
        help="Include hidden files and folders (starting with .)"
    )

    args = parser.parse_args()

    converter = MarkdownToTrilium(args.server, args.token)
    success = converter.convert_directory(
        args.directory,
        parent_note_id=args.parent,
        preview=args.preview,
        include_hidden=args.include_hidden
    )

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
