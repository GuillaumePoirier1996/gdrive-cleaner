import os

# Absolutiser les chemins du fichier JSON et du token
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(CURRENT_DIR, "../config/client_secret.json")
TOKEN_FILE = os.path.join(CURRENT_DIR, "../config/token.pickle")
DATA_DIR = os.path.join(CURRENT_DIR, "../data")

# Adresse pour accepter les accès
SCOPES = ["https://www.googleapis.com/auth/drive"]

# Regex
DUPLICATE_PATTERN = r"\(\d{1,2}\)|\bcopie\s*de\b"
EXTENSION_CLEANUP_PATTERN = r"\s+((\.\w+)+)$"
EXTENSION_CLEANUP_REPLACEMENT = r"\1"
