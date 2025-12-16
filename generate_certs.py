"""Генерирует самоподписанные SSL сертификаты для локального HTTPS"""
import os
import subprocess
from pathlib import Path

certs_dir = Path("d:/bot/certs")
certs_dir.mkdir(exist_ok=True)

cert_file = certs_dir / "cert.pem"
key_file = certs_dir / "key.pem"

if not cert_file.exists() or not key_file.exists():
    print("🔐 Генерирую самоподписанные сертификаты...")
    cmd = f'openssl req -x509 -newkey rsa:4096 -nodes -out "{cert_file}" -keyout "{key_file}" -days 365 -subj "/CN=localhost"'
    subprocess.run(cmd, shell=True)
    print(f"✅ Сертификаты созданы в {certs_dir}")
else:
    print(f"✅ Сертификаты уже существуют в {certs_dir}")
