import json
from base64 import b64decode, b64encode
from typing import Any

from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.asymmetric.padding import MGF1, OAEP, hashes
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.primitives.serialization import load_pem_private_key

from app.config import settings
from app.models.flows import FlowDataExchange, FlowPing, parse_flow_message


def load_private_key() -> rsa.RSAPrivateKey:
    private_key = load_pem_private_key(
        settings.ENCRYPTION_KEY.encode("utf-8"),
        password=None,
        backend=default_backend(),
    )
    if isinstance(private_key, rsa.RSAPrivateKey):
        return private_key
    raise TypeError


def decrypt_request(
    encrypted_flow_data_b64: str, encrypted_aes_key_b64: str, initial_vector_b64: str
) -> tuple[FlowPing | FlowDataExchange, bytes, bytes]:
    flow_data = b64decode(encrypted_flow_data_b64)
    iv = b64decode(initial_vector_b64)

    # Decrypt the AES encryption key
    encrypted_aes_key = b64decode(encrypted_aes_key_b64)
    private_key = load_private_key()
    aes_key = private_key.decrypt(
        encrypted_aes_key,
        OAEP(mgf=MGF1(algorithm=hashes.SHA256()), algorithm=hashes.SHA256(), label=None),
    )

    # Decrypt the Flow data
    encrypted_flow_data_body = flow_data[:-16]
    encrypted_flow_data_tag = flow_data[-16:]
    decryptor = Cipher(algorithms.AES(aes_key), modes.GCM(iv, encrypted_flow_data_tag)).decryptor()
    decrypted_data_bytes = decryptor.update(encrypted_flow_data_body) + decryptor.finalize()
    decrypted_data = json.loads(decrypted_data_bytes.decode("utf-8"))
    return parse_flow_message(decrypted_data), aes_key, iv


def encrypt_response(response: Any, aes_key: bytes, iv: bytes) -> str:
    # Flip the initialization vector
    flipped_iv = bytearray()
    for byte in iv:
        flipped_iv.append(byte ^ 0xFF)

    # Encrypt the response data
    encryptor = Cipher(algorithms.AES(aes_key), modes.GCM(bytes(flipped_iv))).encryptor()
    return b64encode(
        encryptor.update(json.dumps(response).encode("utf-8")) + encryptor.finalize() + encryptor.tag
    ).decode("utf-8")
