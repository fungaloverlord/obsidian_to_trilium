"""Directory scanner for discovering Markdown files and folder structure."""
from pathlib import Path
from typing import List, Dict, Any, Optional
from dataclasses import dataclass, field


@dataclass
class FileNode:
    """Represents a file in the directory tree."""
    path: Path
    name: str
    title: str  # Derived from filename without extension
    is_directory: bool
    children: List['FileNode']
    parent: Optional['FileNode'] = None
    frontmatter: Optional[Dict[str, Any]] = None  # YAML frontmatter metadata
    wiki_links: List[str] = field(default_factory=list)  # Wiki-style [[links]] found in content

    def __repr__(self):
        type_str = "DIR" if self.is_directory else "FILE"
        return f"{type_str}: {self.name} ({len(self.children)} children)"


class DirectoryScanner:
    """Scans directories for Markdown files and builds a tree structure."""

    def __init__(self, root_path: str, include_hidden: bool = False):
        """
        Initialize the scanner.

        Args:
            root_path: Root directory to scan
            include_hidden: Whether to include hidden files/folders (starting with .)
        """
        self.root_path = Path(root_path).resolve()
        self.include_hidden = include_hidden

    def scan(self) -> FileNode:
        """
        Scan the directory tree and build a hierarchical structure.

        Returns:
            Root FileNode representing the directory tree
        """
        return self._scan_recursive(self.root_path, None)

    def _scan_recursive(self, path: Path, parent: FileNode = None) -> FileNode:
        """
        Recursively scan a directory.

        Args:
            path: Current path to scan
            parent: Parent FileNode

        Returns:
            FileNode representing this path
        """
        # Skip hidden files/folders if not included
        if not self.include_hidden and path.name.startswith('.'):
            return None

        # Create node for this path
        is_directory = path.is_dir()
        title = path.stem if not is_directory else path.name

        node = FileNode(
            path=path,
            name=path.name,
            title=title,
            is_directory=is_directory,
            children=[],
            parent=parent
        )

        # If it's a directory, scan children
        if is_directory:
            try:
                for child_path in sorted(path.iterdir()):
                    # Only process directories and .md files
                    if child_path.is_dir() or child_path.suffix.lower() == '.md':
                        child_node = self._scan_recursive(child_path, node)
                        if child_node:
                            node.children.append(child_node)
            except PermissionError:
                print(f"Warning: Permission denied for {path}")

        return node

    def print_tree(self, node: FileNode = None, indent: int = 0):
        """
        Print the directory tree structure.

        Args:
            node: Starting node (uses root if None)
            indent: Current indentation level
        """
        if node is None:
            root = self.scan()
            self.print_tree(root, 0)
            return

        prefix = "  " * indent
        icon = "📁" if node.is_directory else "📄"
        print(f"{prefix}{icon} {node.name}")

        for child in node.children:
            self.print_tree(child, indent + 1)

    def get_all_markdown_files(self) -> List[FileNode]:
        """
        Get a flat list of all Markdown file nodes.

        Returns:
            List of FileNode objects representing .md files
        """
        root = self.scan()
        result = []
        self._collect_markdown_files(root, result)
        return result

    def _collect_markdown_files(self, node: FileNode, result: List[FileNode]):
        """Recursively collect all Markdown file nodes."""
        if not node.is_directory:
            result.append(node)

        for child in node.children:
            self._collect_markdown_files(child, result)
