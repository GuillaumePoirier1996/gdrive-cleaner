from typing import Any, Dict, List

def list_files(service) -> Dict[str, Dict[str, Any]]:
    """
    List non-trashed, non-shared files owned by the current user.
    Return a dictionary {id: file}, with cleaned parent_id.
    """
    page_token = None
    all_files = {}

    while True:
        results = (
            service.files()
            .list(
                fields=(
                    "nextPageToken, files(id, name, modifiedTime, mimeType, parents, size, trashed, shared, owners)"
                ),
                pageSize=1000,
                pageToken=page_token,
                q="trashed = false",
            )
            .execute()
        )
        items = results.get("files", [])
        for item in items:
            # Skip shared files
            if item.get("shared"):
                continue

            # Skip files not owned exclusively by me
            owners = item.get("owners", [])
            if not owners or not all(owner.get("me") for owner in owners):
                continue

            # Clean parent_id
            parents = item.get("parents")
            item["parent_id"] = parents[0] if isinstance(parents, list) and parents else None

            all_files[item["id"]] = item

        page_token = results.get("nextPageToken")
        if not page_token:
            break

    return all_files

def move_files(service, ids: List[str], elements: Dict[str, Dict[str, Any]], destination_id: str, verbose=False):
    """
    Move a list of files/folders to a new location by their ID.

    Args:
        service: Google Drive API connection
        ids (List[str]): List of IDs to move
        elements (Dict[str, Dict[str, Any]]): Details of files/folders
        destination_id (str): ID of the destination folder
        verbose (bool): Whether to print the moves

    """
    for id_ in ids:
        folder = elements.get(id_, {"name": "(unknown)"})
        try:
            service.files().update(
                fileId=id_,
                addParents=destination_id,
                removeParents=elements[id_]["parent_id"],
                fields="id, parents"
            ).execute()
            if verbose:
                print(f"Moved: {folder['name']} to {destination_id}")
        except Exception as e:
            print(f"Error moving {folder['name']} (id={id_}): {e}")


def rename_files(service, ids: List[str], new_names: List[str], elements: Dict[str, Dict[str, Any]], verbose=False):
    """
    Rename a list of files/folders by IDs.

    Args:
        service: Google Drive API connection
        ids List(str): ID of the file/folder to rename
        new_names List(str): New name for the file/folder
        elements (Dict[str, Dict[str, Any]]): Details of files/folders
        verbose (bool): Whether to print the renaming
    """
    for id_, new_name in zip(ids, new_names):
        folder = elements.get(id_, {"name": "(unknown)"})
        try:
            service.files().update(
                fileId=id_,
                body={'name': new_name}
            ).execute()
            if verbose:
                print(f"Renamed: {folder['name']} to {new_name}")
        except Exception as e:
            print(f"Error renaming {folder['name']} (id={id_}): {e}")

    
def trash_files(service, ids: List[str], elements: Dict[str, Dict[str, Any]], verbose=False):
    """
    Move a list of files/folders to the trash by their ID.

    Args:
        service: Google Drive API connection
        ids (List[str]): List of IDs to delete
        elements (Dict[str, Dict[str, Any]]): Details of files/folders
        verbose (bool): Whether to print the deletions
    """
    for id_ in ids:
        folder = elements.get(id_, {"name": "(unknown)"})
        try:
            service.files().update(
                fileId=id_,
                body={'trashed': True}
            ).execute()
            if verbose:
                print(f"Deleted: {folder['name']}")
        except Exception as e:
            print(f"Error deleting {folder['name']} (id={id_}): {e}")