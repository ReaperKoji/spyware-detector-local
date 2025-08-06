import os
import shutil
import hashlib
from datetime import datetime

QUARANTINE_DIR = os.path.join(os.path.dirname(__file__), '..', 'quarentena')

def ensure_quarantine_dir():
    if not os.path.exists(QUARANTINE_DIR):
        os.makedirs(QUARANTINE_DIR)

def hash_file(filepath):
    try:
        with open(filepath, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()
    except Exception:
        return None

def quarantine_file(filepath):
    try:
        ensure_quarantine_dir()
        if not os.path.isfile(filepath):
            return f"[X] Arquivo não encontrado: {filepath}"

        hash_val = hash_file(filepath)
        filename = os.path.basename(filepath)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        new_name = f"{timestamp}_{hash_val[:8]}_{filename}"
        dest_path = os.path.join(QUARANTINE_DIR, new_name)

        shutil.move(filepath, dest_path)
        return f"[✔] Arquivo movido para quarentena: {dest_path}"
    except Exception as e:
        return f"[X] Falha ao mover para quarentena: {filepath} -> {e}"

def list_quarantined_files():
    ensure_quarantine_dir()
    return os.listdir(QUARANTINE_DIR)

def restore_file(quarantined_filename, restore_path):
    try:
        src = os.path.join(QUARANTINE_DIR, quarantined_filename)
        shutil.move(src, restore_path)
        return f"[✔] Arquivo restaurado para: {restore_path}"
    except Exception as e:
        return f"[X] Falha ao restaurar: {e}"
