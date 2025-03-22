from flask import Flask, request, jsonify
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import padding
import os
import base64
import binascii
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# In-memory storage for keys
keys_store = {}

@app.route('/')
def hello_world():
    return 'Harry Potter, The Boy Who Lived.!!'

@app.route("/generate-key", methods=["POST"])
def generate_key():
    try:
        data = request.get_json()
        key_type = data.get("key_type")
        key_size = data.get("key_size")

        logger.info(f"Generating key with type: {key_type}, size: {key_size}")

        if key_type not in ["AES", "RSA"]:
            return jsonify({"error": "Unsupported key type"}), 400

        if key_type == "AES":
            if key_size not in [128, 192, 256]:
                return jsonify({"error": "Invalid key size for AES"}), 400
            key = os.urandom(key_size // 8)
            
        elif key_type == "RSA":
            if key_size not in [2048, 3072, 4096]:
                return jsonify({"error": "Invalid key size for RSA"}), 400
            key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)

        key_id = str(len(keys_store) + 1)
        keys_store[key_id] = key

        if key_type == "AES":
            key_value = base64.b64encode(key).decode()
        elif key_type == "RSA":
            key_value = base64.b64encode(key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )).decode()

        return jsonify({"key_id": key_id, "key_value": key_value})

    except Exception as e:
        logger.error(f"Error generating key: {e}")
        return jsonify({"error": "Internal server error"}), 500

@app.route("/encrypt", methods=["POST"])
def encrypt():
    try:
        data = request.get_json()
        key_id = data.get("key_id")
        plaintext = data.get("plaintext")
        algorithm = data.get("algorithm")

        logger.info(f"Encrypting message with key_id: {key_id}")

        if key_id not in keys_store:
            return jsonify({"error": "Key not found"}), 404

        key = keys_store[key_id]

        if algorithm == "AES":
            iv = os.urandom(16)
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()

            padder = padding.PKCS7(algorithms.AES.block_size).padder()
            padded_data = padder.update(plaintext.encode()) + padder.finalize()

            ciphertext = encryptor.update(padded_data) + encryptor.finalize()
            ciphertext = base64.b64encode(iv + ciphertext).decode()

        else:
            return jsonify({"error": "Unsupported algorithm"}), 400

        return jsonify({"ciphertext": ciphertext})

    except Exception as e:
        logger.error(f"Encryption error: {e}")
        return jsonify({"error": "Encryption failed"}), 500

@app.route("/decrypt", methods=["POST"])
def decrypt():
    try:
        data = request.get_json()
        key_id = data.get("key_id")
        ciphertext = data.get("ciphertext")
        algorithm = data.get("algorithm")

        logger.info(f"Decrypting message with key_id: {key_id}")

        if key_id not in keys_store:
            return jsonify({"error": "Key not found"}), 404

        key = keys_store[key_id]

        if algorithm == "AES":
            padding_length = len(ciphertext) % 4
            if padding_length:
                ciphertext += "=" * (4 - padding_length)

            ciphertext = base64.b64decode(ciphertext)
            iv = ciphertext[:16]
            ciphertext = ciphertext[16:]

            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            decryptor = cipher.decryptor()

            padded_plaintext = decryptor.update(ciphertext) + decryptor.finalize()

            unpadder = padding.PKCS7(algorithms.AES.block_size).unpadder()
            plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
            plaintext = plaintext.decode()

        else:
            return jsonify({"error": "Unsupported algorithm"}), 400

        return jsonify({"plaintext": plaintext})

    except (ValueError, binascii.Error) as e:
        return jsonify({"error": f"Decryption failed: {str(e)}"}), 400

@app.route("/generate-hash", methods=["POST"])
def generate_hash():
    try:
        data = request.get_json()
        text = data.get("data")
        algorithm = data.get("algorithm")

        logger.info(f"Generating Hash using Algorithm: {algorithm}")

        if algorithm not in ["SHA-256", "SHA-512"]:
            return jsonify({"error": "Unsupported hashing algorithm"}), 400

        if algorithm == "SHA-256":
            digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        elif algorithm == "SHA-512":
            digest = hashes.Hash(hashes.SHA512(), backend=default_backend())

        digest.update(text.encode())
        hash_value = base64.b64encode(digest.finalize()).decode()

        return jsonify({"hash_value": hash_value, "algorithm": algorithm})

    except Exception as e:
        logger.error(f"Hash generation error: {e}")
        return jsonify({"error": "Hash generation failed"}), 500

@app.route("/verify-hash", methods=["POST"])
def verify_hash():
    try:
        data = request.get_json()
        text = data.get("data")
        hash_value = data.get("hash_value")
        algorithm = data.get("algorithm")

        logger.info(f"Verifying hash: {hash_value}")

        if algorithm not in ["SHA-256", "SHA-512"]:
            return jsonify({"error": "Unsupported hashing algorithm"}), 400

        if algorithm == "SHA-256":
            digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        elif algorithm == "SHA-512":
            digest = hashes.Hash(hashes.SHA512(), backend=default_backend())

        digest.update(text.encode())
        computed_hash = base64.b64encode(digest.finalize()).decode()

        is_valid = computed_hash == hash_value
        message = "Hash matches the data." if is_valid else "Hash does not match the data."

        return jsonify({"is_valid": is_valid, "message": message})

    except Exception as e:
        logger.error(f"Hash verification error: {e}")
        return jsonify({"error": "Hash verification failed"}), 500

if __name__ == "__main__":
    app.run(debug=True)
