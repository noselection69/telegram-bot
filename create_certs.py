"""Генерирует самоподписанные SSL сертификаты используя cryptography"""
from pathlib import Path
from datetime import datetime, timedelta
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization

def create_self_signed_cert(cert_file, key_file):
    """Создать самоподписанный сертификат"""
    
    # Генерируем приватный ключ
    key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
    )
    
    # Генерируем сертификат
    subject = issuer = x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
    ])
    
    cert = x509.CertificateBuilder().subject_name(
        subject
    ).issuer_name(
        issuer
    ).public_key(
        key.public_key()
    ).serial_number(
        x509.random_serial_number()
    ).not_valid_before(
        datetime.utcnow()
    ).not_valid_after(
        datetime.utcnow() + timedelta(days=365)
    ).add_extension(
        x509.SubjectAlternativeName([
            x509.DNSName(u"localhost"),
            x509.DNSName(u"127.0.0.1"),
        ]),
        critical=False,
    ).sign(key, hashes.SHA256())
    
    # Сохраняем сертификат
    with open(cert_file, "wb") as f:
        f.write(cert.public_bytes(serialization.Encoding.PEM))
    
    # Сохраняем ключ
    with open(key_file, "wb") as f:
        f.write(key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
        ))
    
    print(f"✅ Сертификаты созданы: {cert_file}, {key_file}")

if __name__ == "__main__":
    certs_dir = Path("certs")
    certs_dir.mkdir(exist_ok=True)
    
    cert_file = certs_dir / "cert.pem"
    key_file = certs_dir / "key.pem"
    
    if not cert_file.exists() or not key_file.exists():
        create_self_signed_cert(cert_file, key_file)
    else:
        print(f"✅ Сертификаты уже существуют")
