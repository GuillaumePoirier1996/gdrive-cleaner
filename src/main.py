from auth import set_service
from drive_operations import (
    list_files,
    rename_files,
    trash_files
)
from utils import (
    save_files,
    find_global_duplicates,
    find_duplicates_by_folders
)
from config import DATA_FILE

def main():
    print("🔑 Authenticating with Google Drive...")
    service = set_service()

    print("🔍 Retrieving Google Drive files...")
    files = list_files(service)

    # Option: Save for manual verification
    save_choice = str(input("Do you want to save files from your Google Drive to ckeck? [y/n]")).lower()
    
    if save_choice == "y":
        print("🗂️ Saving files to JSON...")
        save_files(files, DATA_FILE)

    print("🧠 First duplicate detection...")
    global_duplicates = find_global_duplicates(files, verbose=False)

    print(f"📦 {len(global_duplicates)} duplicates found to be removed.")

    if not global_duplicates:
        print("No duplicate found!")
    else:
        print("🧹 Removing firsts duplicates... (to trash)")
        # Option: First removing
        remove_choice_1 = str(input("Do you want to remove these duplicates from your Google Drive? [y/n]")).lower()
        if remove_choice_1 == "y":
            # Remove duplicates from Google Drive
            trash_files(service, global_duplicates, files, verbose=False)

    print("🧠 Detecting duplicate files in remaining folders...")
    ids_to_remove, ids_to_rename, new_names = find_duplicates_by_folders(files, global_duplicates)

    if not ids_to_remove:
        print("No duplicate files found!")
    else:
        print("🧹 Removing duplicate files... (to trash)")
        # Option: Second removing
        remove_choice_2 = str(input("Do you want to remove these duplicates from your Google Drive? [y/n]")).lower()
        if remove_choice_2 == "y":
            # Remove duplicates from Google Drive
            trash_files(service, ids_to_remove, files, verbose=False)

    # Optional: Renaning to simplify
    rename_choice = str(input("The program is about to rename files (drop (1), copy of, delete some whitespaces) from your Google Drive.\n\
Do you want to continue ? [y/n]")).lower()

    if rename_choice == "y":
        print("📝 Renaming files...")
        rename_files(service, ids_to_rename, new_names, files, verbose=False)

    print("✅ Process completed.")

if __name__ == "__main__":
    main()
