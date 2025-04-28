import pandas as pd
from unidecode import unidecode

from utils import (
    DUPLICATE_PATTERN,
    EXTENSION_CLEANUP_PATTERN,
    EXTENSION_CLEANUP_REPLACEMENT,
)


def list_files(service) -> pd.DataFrame:
    page_token = None
    all_files = []

    while True:
        results = (
            service.files()
            .list(
                fields="nextPageToken, files(id, name, modifiedTime, mimeType, parents, size)",
                pageSize=1000,
                pageToken=page_token,
            )
            .execute()
        )
        items = results.get("files", [])
        all_files.extend(items)
        page_token = results.get("nextPageToken")
        if not page_token:
            break

    return pd.DataFrame(all_files)


def find_duplicates(df: pd.DataFrame):
    # Enlève les dossiers de la sélection
    df = df[df["mimeType"] != "application/vnd.google-apps.folder"].copy()

    # parents est une liste de dossiers (IDs de dossiers).
    # Exemple : ['1a2b3c4d'] pour un fichier dans un seul dossier.
    # Ou [] ou None si le fichier n’est pas dans un dossier explicite
    # (par exemple à la racine).
    # Parfois même : ['id1', 'id2'] si le fichier est partagé entre
    # plusieurs dossiers ! 😱
    # Pandas ne peut pas grouper sur une colonne de listes directement
    # ça renverrait une erreur ou des résultats inattendus.
    # ✅ Solution pratique : créer une colonne "parent" simple
    df["parent"] = df["parents"].apply(
        lambda x: x[0] if isinstance(x, list) and x else "root"
    )

    # Normalisation du nom
    df["normalized_name"] = df["name"].fillna("").apply(unidecode)

    # Création du base_name pour tout le monde
    df["base_name"] = (
        df["normalized_name"]
        .str.replace(DUPLICATE_PATTERN, "", regex=True)
        .str.replace(
            EXTENSION_CLEANUP_PATTERN, EXTENSION_CLEANUP_REPLACEMENT, regex=True
        )
        .str.strip()
        .str.lower()
    )

    # Pour les fichiers qui ont le même nom (base_name), on garde le plus récent.
    # La fonction est créée pour être appliquée à chaque dossiers (groupe de fichiers).
    def mark_duplicates(folder):
        # Ceux que l’on garde dans ce dossier
        keep = folder.sort_values(by="modifiedTime").drop_duplicates(
            subset="base_name", keep="last"
        )
        # Ceuxw que l’on supprime dans ce dossier
        folder["to_remove"] = ~folder.index.isin(keep.index)
        return folder

    # Appliquer la fonction à chaque dossier
    # (group_keys=False pour ne pas ajouter le nom du groupe dans l’index)
    df = df.groupby("parent", group_keys=False).apply(mark_duplicates)
    return df[df["to_remove"]]


def delete_files(service, duplicates: pd.DataFrame):
    for _, row in duplicates.iterrows():
        try:
            service.files().delete(fileId=row["id"]).execute()
        except Exception as e:
            print(f"Erreur lors de la suppression de {row['name']} ({row['id']}) : {e}")
