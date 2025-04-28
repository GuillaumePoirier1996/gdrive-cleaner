import os

from googleapiclient.discovery import build

from auth import authenticate_google_drive
from drive_operations import list_files
from utils import DATA_DIR


def main():
    print("🔑 Authentification Google Drive...")
    creds = authenticate_google_drive()
    service = build("drive", "v3", credentials=creds)

    print("🔍 Récupération des fichiers Google Drive...")
    files = list_files(service)

    # Facultatif : sauvegarder pour vérification manuelle
    files.to_csv(
        os.path.join(DATA_DIR, "files.csv"),
        sep=";",
        encoding="utf-8",
        index=False,
    )

    # print("🧠 Détection des doublons par dossier...")
    # duplicates = find_duplicates(files)

    # print(f"📦 {len(duplicates)} doublons trouvés à supprimer.")

    # Facultatif : sauvegarder pour vérification manuelle
    # duplicates.to_csv("../data/duplicates.csv", index=False)

    # if duplicates.empty:
    #     print("Aucun fichier en double trouvé !!!!")
    # else:
    #     print("🧹 Suppression des doublons...")
    #     delete_files(service, duplicates)

    print("✅ Traitement terminé.")


if __name__ == "__main__":
    main()
