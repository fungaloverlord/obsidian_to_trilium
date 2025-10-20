"""Trilium note uploader that handles hierarchy creation."""
from typing import Dict, Optional, List, Any, Tuple
from trilium_py.client import ETAPI
from directory_scanner import FileNode
from md_converter import MarkdownConverter
from pathlib import Path
import re


class TriliumUploader:
    """Uploads Markdown files to Trilium preserving directory hierarchy."""

    def __init__(self, server_url: str, token: str):
        """
        Initialize the uploader.

        Args:
            server_url: Trilium server URL
            token: ETAPI authentication token
        """
        self.ea = ETAPI(server_url, token)
        self.converter = MarkdownConverter()
        # Maps file paths to created note IDs
        self.note_id_map: Dict[str, str] = {}
        # Maps note titles to note IDs (for wiki link resolution)
        self.title_to_id_map: Dict[str, str] = {}
        # Default label key to extract from frontmatter
        self.label_keys = ['tags', 'labels', 'categories']
        # Track pending relations to create after all notes are uploaded
        self.pending_relations: List[Tuple[str, str]] = []  # (source_note_id, target_title)
        # Track notes that need wiki link replacement in content
        self.notes_with_wiki_links: List[Tuple[str, str]] = []  # (note_id, html_content)
        # Orphans note ID for placeholder notes
        self.orphans_note_id: Optional[str] = None

    def upload_tree(self, root_node: FileNode, parent_note_id: str = "root") -> Dict[str, str]:
        """
        Upload an entire directory tree to Trilium.

        Args:
            root_node: Root FileNode from DirectoryScanner
            parent_note_id: Parent note ID in Trilium (default: 'root')

        Returns:
            Dictionary mapping file paths to created note IDs
        """
        self.note_id_map.clear()
        self.title_to_id_map.clear()
        self.pending_relations.clear()
        self.notes_with_wiki_links.clear()

        # Create or find the Orphans note for placeholder notes
        self.orphans_note_id = self._get_or_create_orphans_note(parent_note_id)

        # First pass: upload all notes
        self._upload_recursive(root_node, parent_note_id)

        # Second pass: update wiki link placeholders in content
        self._update_wiki_link_content()

        # Third pass: create relations between notes
        self._create_pending_relations()

        return self.note_id_map

    def _upload_recursive(self, node: FileNode, parent_note_id: str):
        """
        Recursively upload nodes to Trilium.

        Args:
            node: Current FileNode to process
            parent_note_id: Parent note ID in Trilium
        """
        if node.is_directory:
            # Create a parent note for this directory
            note_id = self._create_directory_note(node, parent_note_id)
            if note_id:
                self.note_id_map[str(node.path)] = note_id
                # Process children with this directory as parent
                for child in node.children:
                    self._upload_recursive(child, note_id)
        else:
            # Create a note from the Markdown file
            note_id = self._create_markdown_note(node, parent_note_id)
            if note_id:
                self.note_id_map[str(node.path)] = note_id

    def _get_or_create_orphans_note(self, parent_note_id: str = "root") -> Optional[str]:
        """
        Get or create the Orphans note for placeholder notes.

        Args:
            parent_note_id: Parent note ID for the Orphans note (default: 'root')

        Returns:
            Orphans note ID or None if failed
        """
        # Search for existing Orphans note
        try:
            # Try to find an existing Orphans note
            search_results = self.ea.search_notes("note.title = 'Orphans'")
            if search_results and len(search_results) > 0:
                orphans_id = search_results[0]['noteId']
                print(f"📂 Found existing Orphans note (ID: {orphans_id})")
                return orphans_id
        except Exception as e:
            print(f"  ⚠️  Could not search for Orphans note: {e}")

        # Create new Orphans note if not found
        note_data = {
            "parentNoteId": parent_note_id,
            "title": "Orphans",
            "content": "<p>This note contains placeholder notes created for unresolved wiki links.</p>",
            "type": "text"
        }

        try:
            response = self.ea.create_note(**note_data)
            if response and 'note' in response:
                orphans_id = response['note']['noteId']

                # Add readOnly label
                self._add_readonly_label(orphans_id)

                print(f"📂 Created Orphans note (ID: {orphans_id})")
                return orphans_id
            else:
                print(f"  ⚠️  Failed to create Orphans note")
                return None
        except Exception as e:
            print(f"  ⚠️  Error creating Orphans note: {e}")
            return None

    def _add_readonly_label(self, note_id: str) -> bool:
        """
        Add #readOnly label to a note.

        Args:
            note_id: Trilium note ID

        Returns:
            True if successful, False otherwise
        """
        try:
            response = self.ea.create_attribute(
                noteId=note_id,
                type="label",
                name="readOnly",
                value="",
                isInheritable=False
            )
            return response is not None
        except Exception as e:
            print(f"  ⚠️  Error adding readOnly label: {e}")
            return False

    def _create_directory_note(self, node: FileNode, parent_note_id: str) -> Optional[str]:
        """
        Create a note representing a directory (container note).

        Args:
            node: FileNode representing a directory
            parent_note_id: Parent note ID

        Returns:
            Created note ID or None if failed
        """
        note_data = {
            "parentNoteId": parent_note_id,
            "title": node.title,
            "content": f"<p>Notes from folder: {node.name}</p>",
            "type": "text"
        }

        try:
            response = self.ea.create_note(**note_data)
            if response and 'note' in response:
                note_id = response['note']['noteId']

                # Add readOnly label
                self._add_readonly_label(note_id)

                print(f"✅ Created folder note: {node.name} (ID: {note_id})")
                return note_id
            else:
                print(f"❌ Failed to create folder note: {node.name}")
                print(f"   Response: {response}")
                print(f"   Parent ID: {parent_note_id}")
                return None
        except Exception as e:
            print(f"❌ Error creating folder note {node.name}: {e}")
            print(f"   Parent ID: {parent_note_id}")
            import traceback
            traceback.print_exc()
            return None

    def _create_markdown_note(self, node: FileNode, parent_note_id: str) -> Optional[str]:
        """
        Create a note from a Markdown file.

        Args:
            node: FileNode representing a Markdown file
            parent_note_id: Parent note ID

        Returns:
            Created note ID or None if failed
        """
        try:
            # Convert Markdown to HTML and extract frontmatter and wiki links
            html_content, frontmatter, wiki_links = self.converter.convert_file(str(node.path))

            # Store frontmatter and wiki links in node for later use
            node.frontmatter = frontmatter
            node.wiki_links = wiki_links

            note_data = {
                "parentNoteId": parent_note_id,
                "title": node.title,
                "content": html_content,
                "type": "text"
            }

            response = self.ea.create_note(**note_data)
            if response and 'note' in response:
                note_id = response['note']['noteId']

                # Add readOnly label
                self._add_readonly_label(note_id)

                # Store title to ID mapping for wiki link resolution
                self.title_to_id_map[node.title] = note_id

                # Track note content if it has wiki links that need to be resolved
                if wiki_links:
                    self.notes_with_wiki_links.append((note_id, html_content))

                # Track pending relations for wiki links
                for target_title in wiki_links:
                    self.pending_relations.append((note_id, target_title))

                # Add labels from frontmatter
                labels_count = 0
                if frontmatter:
                    labels_count = self._add_labels_from_frontmatter(note_id, frontmatter)

                # Build status message
                extras = []
                if labels_count:
                    extras.append(f"{labels_count} label(s)")
                if wiki_links:
                    extras.append(f"{len(wiki_links)} link(s)")

                if extras:
                    print(f"✅ Created note: {node.title} (ID: {note_id}) with {', '.join(extras)}")
                else:
                    print(f"✅ Created note: {node.title} (ID: {note_id})")

                return note_id
            else:
                print(f"❌ Failed to create note: {node.title}")
                return None
        except Exception as e:
            print(f"❌ Error creating note {node.title}: {e}")
            return None

    def _extract_labels(self, frontmatter: Dict[str, Any]) -> List[str]:
        """
        Extract labels from frontmatter metadata.

        Args:
            frontmatter: Parsed YAML frontmatter dictionary

        Returns:
            List of label strings
        """
        labels = []

        # Check common label keys
        for key in self.label_keys:
            if key in frontmatter:
                value = frontmatter[key]
                # Handle both string and list formats
                if isinstance(value, str):
                    # Split comma-separated tags
                    labels.extend([tag.strip() for tag in value.split(',')])
                elif isinstance(value, list):
                    labels.extend([str(tag).strip() for tag in value])

        # Remove duplicates and empty strings
        labels = list(set(label for label in labels if label))
        return labels

    def _add_labels_from_frontmatter(self, note_id: str, frontmatter: Dict[str, Any]) -> int:
        """
        Add labels to a Trilium note based on frontmatter.

        Args:
            note_id: Trilium note ID
            frontmatter: Parsed YAML frontmatter dictionary

        Returns:
            Number of labels added
        """
        labels = self._extract_labels(frontmatter)

        if not labels:
            return 0

        labels_added = 0
        for label in labels:
            try:
                # Parse label: if it contains "/" or "_", split into name=value
                # e.g., "theme/justice" -> name="theme", value="justice"
                # e.g., "period/ancient-greek" -> name="period", value="ancient-greek"
                if '/' in label:
                    parts = label.split('/', 1)  # Split on first "/" only
                    label_name = parts[0]
                    label_value = parts[1]
                elif '_' in label:
                    parts = label.split('_', 1)  # Split on first "_" only
                    label_name = parts[0]
                    label_value = parts[1]
                else:
                    label_name = label
                    label_value = ""

                # Create label attribute for the note
                # create_attribute(noteId, type, name, value, isInheritable)
                response = self.ea.create_attribute(
                    noteId=note_id,
                    type="label",
                    name=label_name,
                    value=label_value,
                    isInheritable=False
                )
                if response:
                    labels_added += 1
                else:
                    if label_value:
                        print(f"  ⚠️  Failed to add label '{label_name}={label_value}' to note {note_id}")
                    else:
                        print(f"  ⚠️  Failed to add label '{label_name}' to note {note_id}")
            except Exception as e:
                if '_' in label:
                    print(f"  ⚠️  Error adding label '{label.split('_', 1)[0]}={label.split('_', 1)[1]}': {e}")
                else:
                    print(f"  ⚠️  Error adding label '{label}': {e}")

        return labels_added

    def _create_placeholder_note(self, note_title: str, parent_note_id: Optional[str] = None) -> Optional[str]:
        """
        Create a placeholder note for a missing wiki link target.

        Args:
            note_title: Title of the note to create
            parent_note_id: Parent note ID (default: uses Orphans note)

        Returns:
            Created note ID or None if failed
        """
        # Use Orphans note as parent if not specified
        if parent_note_id is None:
            parent_note_id = self.orphans_note_id

        # Fallback to root if Orphans note creation failed
        if parent_note_id is None:
            parent_note_id = "root"
            print(f"  ⚠️  Warning: Using 'root' as parent for placeholder note (Orphans note unavailable)")

        note_data = {
            "parentNoteId": parent_note_id,
            "title": note_title,
            "content": "<p><em>This note was automatically created as a placeholder for a wiki link reference.</em></p>",
            "type": "text"
        }

        try:
            response = self.ea.create_note(**note_data)
            if response and 'note' in response:
                note_id = response['note']['noteId']

                # Add readOnly label
                self._add_readonly_label(note_id)

                print(f"  📝 Created placeholder note: {note_title} (ID: {note_id})")
                return note_id
            else:
                print(f"  ⚠️  Failed to create placeholder note: {note_title}")
                return None
        except Exception as e:
            print(f"  ⚠️  Error creating placeholder note {note_title}: {e}")
            return None

    def _update_wiki_link_content(self):
        """
        Update note content to replace wiki link placeholders with actual Trilium reference links.
        Creates placeholder notes for missing wiki link targets.
        """
        if not self.notes_with_wiki_links:
            return

        print(f"\n🔄 Updating {len(self.notes_with_wiki_links)} note(s) with wiki links...")

        # First pass: identify missing notes and create placeholders
        missing_notes = set()
        for note_id, original_html in self.notes_with_wiki_links:
            wiki_placeholder_pattern = r'<span data-wiki-link="([^"]+)">([^<]+)</span>'
            matches = re.findall(wiki_placeholder_pattern, original_html)
            for note_name, _ in matches:
                if note_name not in self.title_to_id_map:
                    missing_notes.add(note_name)

        # Create placeholder notes for missing references
        if missing_notes:
            print(f"\n📝 Creating {len(missing_notes)} placeholder note(s) for missing wiki links...")
            for note_title in missing_notes:
                placeholder_id = self._create_placeholder_note(note_title)
                if placeholder_id:
                    self.title_to_id_map[note_title] = placeholder_id

        # Second pass: replace placeholders with actual links
        updated_count = 0
        for note_id, original_html in self.notes_with_wiki_links:
            # Replace <span data-wiki-link="note_name">text</span> with proper Trilium links
            def replace_wiki_placeholder(match):
                note_name = match.group(1)
                link_text = match.group(2)
                target_note_id = self.title_to_id_map.get(note_name)

                if target_note_id:
                    # Create Trilium reference link
                    return f'<a class="reference-link" href="#root/{target_note_id}">{link_text}</a>'
                else:
                    # If target still not found (shouldn't happen now), keep as plain text with warning marker
                    return f'<span style="color: red;" title="Note not found">{link_text}</span>'

            wiki_placeholder_pattern = r'<span data-wiki-link="([^"]+)">([^<]+)</span>'
            updated_html = re.sub(wiki_placeholder_pattern, replace_wiki_placeholder, original_html)

            # Update the note content if changes were made
            if updated_html != original_html:
                try:
                    self.ea.update_note_content(note_id, updated_html)
                    updated_count += 1
                except Exception as e:
                    print(f"  ⚠️  Error updating note {note_id} content: {e}")

        if updated_count:
            print(f"✅ Updated {updated_count} note(s) with resolved wiki links")

    def _create_pending_relations(self):
        """
        Create Trilium relations for all pending wiki links after all notes are uploaded.
        """
        if not self.pending_relations:
            return

        print(f"\n🔗 Creating {len(self.pending_relations)} relation(s)...")

        relations_created = 0
        for source_note_id, target_title in self.pending_relations:
            # Find target note ID by title
            target_note_id = self.title_to_id_map.get(target_title)

            if not target_note_id:
                print(f"  ⚠️  Warning: Cannot find note titled '{target_title}' for relation")
                continue

            try:
                # Create relation attribute
                response = self.ea.create_attribute(
                    noteId=source_note_id,
                    type="relation",
                    name="references",
                    value=target_note_id,
                    isInheritable=False
                )
                if response:
                    relations_created += 1
                else:
                    print(f"  ⚠️  Failed to create relation: {source_note_id} -> {target_title}")
            except Exception as e:
                print(f"  ⚠️  Error creating relation to '{target_title}': {e}")

        if relations_created:
            print(f"✅ Created {relations_created} relation(s)")

    def get_note_id(self, file_path: str) -> Optional[str]:
        """
        Get the Trilium note ID for a given file path.

        Args:
            file_path: Path to the file

        Returns:
            Note ID if found, None otherwise
        """
        return self.note_id_map.get(str(Path(file_path).resolve()))
