import os

# Absolute paths for files/directories
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_FILE = os.path.join(CURRENT_DIR, "../config/client_secret.json")
TOKEN_FILE = os.path.join(CURRENT_DIR, "../config/token.pickle")
DATA_FILE = os.path.join(CURRENT_DIR, "../data/files.json")

# Scope for accepting access
SCOPES = ["https://www.googleapis.com/auth/drive"]

# Regex patterns
DUPLICATE_PATTERN = r"(\s*\(\d{1,2}\)\s*)+|\s*(cop(y|ie)\s*(.|de|of)\s*\b)+"
