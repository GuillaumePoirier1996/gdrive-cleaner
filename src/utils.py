import json
from anytree import Node
from collections import defaultdict
import hashlib
from typing import Dict, List, Any, Set, Tuple
import re
from unidecode import unidecode
from config import DUPLICATE_PATTERN

def save_files(files: Dict[str, Any], filepath: str) -> None:
    """Save the files dictionary to a JSON file."""
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(files, f, ensure_ascii=False, indent=2)

def build_tree(files: Dict[str, dict]) -> Node:
    """
    Build a tree from a flat dictionary of file metadata.

    Args:
        files: A dictionary mapping file IDs to their metadata (including name, parent_id, size, etc.)

    Returns:
        The root node of the constructed tree.
    """
    node_map = {}
    root = Node("My Drive", file_id="root")  # Root node for the drive

    # Create all nodes
    for file_id, metadata in files.items():
        name = metadata["name"]
        parent_id = metadata.get("parent_id", "root")
        node = Node(name, file_id=file_id, size=metadata.get("size"), data=metadata)
        node_map[file_id] = node

    # Assign parents to build the tree structure
    for node in node_map.values():
        parent_id = node.data.get("parent_id", "root")
        parent = node_map.get(parent_id, root)
        node.parent = parent

    return root


def compute_subtree_hash(node: Node) -> str:
    """
    Compute a hash for a subtree, including the node's name, size, and recursively its children's hashes.

    Args:
        node: The root of the subtree to hash.

    Returns:
        A string representing the hash of the subtree.
    """
    hasher = hashlib.md5()
    hasher.update(node.name.encode())

    size = str(node.data.get("size", 0))  # Fallback to 0 if size is missing (likely a folder)
    hasher.update(size.encode())

    # Hash children recursively in sorted order for consistency
    children_hashes = sorted(compute_subtree_hash(child) for child in node.children)
    for child_hash in children_hashes:
        hasher.update(child_hash.encode())

    return hasher.hexdigest()


def collect_subtree_hashes(root: Node) -> Dict[str, List[Node]]:
    """
    Traverse the tree and collect a mapping from subtree hashes to lists of nodes that share that hash.

    Args:
        root: The root of the tree to hash.

    Returns:
        A dictionary mapping hash strings to lists of nodes with matching subtree structure and content.
    """
    hashes = defaultdict(list)

    for node in root.descendants:
        subtree_hash = compute_subtree_hash(node)
        hashes[subtree_hash].append(node)

    return hashes

def find_deepest_duplicates(hashes: Dict[str, List[Node]]) -> List[str]:
    """
    Identify duplicate subtrees and return the IDs of those considered as duplicates (excluding the original).

    Args:
        hashes: A dictionary mapping subtree hashes to nodes.

    Returns:
        A list of file IDs that are considered duplicates.
    """
    duplicate_ids = []

    for _, nodes in hashes.items():
        if len(nodes) > 1:
            # Sort nodes by tree depth (shallowest first = likely original)
            nodes_sorted = sorted(nodes, key=lambda node: node.depth)

            for duplicate in nodes_sorted[1:]:
                duplicate_ids.append(duplicate.data["id"])

    return duplicate_ids


def find_global_duplicates(elements: Dict[str, Dict[str, Any]], verbose: bool = False) -> List[str]:
    """
    First step of duplicates's detections (folder or files) of the Google Drive structure.

    Args:
        elements (Dict[str, Dict[str, Any]]): {id: {'name', 'modifiedTime', 'mimeType', 'parent_id', '...'}}
        verbose (bool): Whether to print detailed information about duplicates

    Returns:
        List[str]: List of IDs of duplicate folders
    """

    # 1. Build tree from folder structure
    root = build_tree(elements)

    # 2. Collect subtree hashes
    hashes = collect_subtree_hashes(root)

    # 3. Find duplicates
    ids_to_delete = find_deepest_duplicates(hashes)

    if verbose:
        for id_ in ids_to_delete:
            print(f"Duplicate folder found: {elements[id_]['name']} (ID: {id_})")

    return ids_to_delete


def find_duplicates_by_folders(elements: Dict[str, Dict[str, Any]], excluded_ids: Set[str]) -> Tuple[List[str], List[str], List[str]]:
    """
    Detect simple file duplicates (based on name) and propose which to delete.

    Args:
        elements (Dict[str, Dict[str, Any]]): {id: {'name', 'modifiedTime', 'mimeType', 'parent_id'}}
        excluded_ids (Set[str]): IDs already deleted or to ignore

    Returns:
        List[str]: List of IDs to delete
    """

    # 1. Filter: only normal files (not folders) and not in excluded IDs
    files = {
        id_: info for id_, info in elements.items()
        if info.get('mimeType') != "application/vnd.google-apps.folder" and id_ not in excluded_ids
    }

    # 2. Prepare: normalized base_name for each file
    for id_, info in files.items():
        name = info.get('name', '') or ''
        normalized_name = unidecode(name)
        base_name = (
            re.sub(DUPLICATE_PATTERN, '', normalized_name, flags=re.IGNORECASE)
            .strip()
            .lower()
        )
        info['base_name'] = base_name

    # 3. Group by parent folder and base_name
    folders = {}

    for id_, info in files.items():
        parent = info.get('parent_id')
        base_name = info.get('base_name')
        key = (parent, base_name)
        folders.setdefault(key, []).append(id_)

    # 4. Mark duplicates to delete
    ids_to_delete = []
    ids_to_rename = []
    new_names = []

    for (parent, base_name), ids in folders.items():
        if len(ids) > 1:
            # If multiple files with the same name in the same folder -> keep the most recent
            ids_sorted = sorted(
                ids,
                key=lambda id_: elements[id_]['modifiedTime'] or '',
                reverse=True  # most recent first
            )
            
            # Keep the first (most recent), delete the others
            ids_to_delete.extend(ids_sorted[1:])
            ids_to_rename.append(ids_sorted[0])
            new_names.append(base_name)

    return ids_to_delete, ids_to_rename, new_names