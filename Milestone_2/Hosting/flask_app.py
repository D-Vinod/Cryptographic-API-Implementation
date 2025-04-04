from flask import Flask, request, jsonify
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives import serialization, hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives.asymmetric import padding as rsa_padding
from cryptography.hazmat.primitives import padding as aes_padding
from pydantic import BaseModel
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
    return 'Hosting for EN4720 - Course Project, Milestone 2: Cryptographic API Implementation'

##########################################################################################################################################################
# Generate either an AES or RSA key based on the request data

# KeyGenerationRequest model
class KeyGenerationRequest(BaseModel):
    key_type: str
    key_size: int

# Key Generation Endpoint
@app.route("/generate-key", methods=["POST"])
def generate_key():
    try:
        data = request.get_json()
        key_type = data.get("key_type")
        key_size = data.get("key_size")

        logger.info(f"Generating key with type: {key_type} of size: {key_size}.")

        if key_type not in ["AES", "RSA"]:
            return jsonify({"key_type_error": "Unsupported key type in key generation."}), 400

        if key_type == "AES":
            if key_size not in [128, 192, 256]:
                return jsonify({"error": "Invalid key size for AES."}), 400
            key = os.urandom(key_size // 8)  # Generate random bytes for AES key
        elif key_type == "RSA":
            if key_size not in [2048, 3072, 4096]:
                return jsonify({"error": "Invalid key size for RSA."}), 400
            key = rsa.generate_private_key(public_exponent=65537, key_size=key_size)

        # Store the key in memory
        key_id = str(len(keys_store) + 1)
        keys_store[key_id] = key

        # Serialize and encode the key in Base64
        if key_type == "AES":
            key_value = base64.b64encode(key).decode()

        elif key_type == "RSA":
            private_key_pem = key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            )
            public_key_pem = key.public_key().public_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PublicFormat.SubjectPublicKeyInfo
            )
            return jsonify({"key_id": key_id, "private_key": base64.b64encode(private_key_pem).decode(), "public_key": base64.b64encode(public_key_pem).decode()})

        return jsonify({"key_id": key_id, "key_value": key_value})

    except Exception as e:
        logger.error(f"Error with key generation - {e}.")
        return jsonify({"Fatal_error": f"Internal Error with key generation. {str(e)}"}), 500

##########################################################################################################################################################
# Encrypt the plaintext using the specified key and algorithm
    
# EncryptionRequest model
class EncryptionRequest(BaseModel):
    key_id: str
    plaintext: str
    algorithm: str

# Encryption Endpoint
@app.route("/encrypt", methods=["POST"])
def encrypt():
    try:
        data = request.get_json()
        key_id = data.get("key_id")
        plaintext = data.get("plaintext")
        algorithm = data.get("algorithm")
        
        logger.info(f"Encrypting message with key_id: {key_id}.")

        if key_id not in keys_store:
           return jsonify({"Key_id_error": "Key not available."}), 404

        key = keys_store[key_id]

        if algorithm == "AES":
            # Generate a random IV (Initialization Vector)
            iv = os.urandom(16)
            cipher = Cipher(algorithms.AES(key), modes.CBC(iv), backend=default_backend())
            encryptor = cipher.encryptor()

            # Pad the plaintext to match block size
            padder = aes_padding.PKCS7(algorithms.AES.block_size).padder()
            padded_data = padder.update(plaintext.encode()) + padder.finalize()

            # Encrypt the data
            ciphertext_bytes = encryptor.update(padded_data) + encryptor.finalize()
            ciphertext = base64.b64encode(iv + ciphertext_bytes).decode()

        elif algorithm == "RSA":

            '''Calculate the max plaintext size for RSA encryption as RSA has a limit 
            on the size of plaintext that can be encrypted depending on the key size'''
            public_key = key.public_key()  # Get the RSA public key
            key_size_bytes = public_key.key_size // 8  # Convert key size from bits to bytes
            hash_size = hashes.SHA512().digest_size  # Get SHA-512 hash size in bytes
            padding_overhead = 2 * hash_size + 2  # OAEP padding overhead
            max_size = key_size_bytes - padding_overhead  # Compute max plaintext size
            if len(plaintext.encode()) > max_size:
                return jsonify({"RSA_plaintext_size_error": f"Message too long! Max size for RSA with key size {key_size_bytes * 8} is {max_size} bits. Provided plaintext is {len(plaintext.encode())} bits."}), 413

            # RSA encryption uses the public key to encrypt
            public_key = key.public_key()
            ciphertext = base64.b64encode(
                public_key.encrypt(
                    plaintext.encode(),
                    rsa_padding.OAEP(
                        mgf = rsa_padding.MGF1(algorithm=hashes.SHA512()),
                        algorithm = hashes.SHA512(),
                        label = None
                    )
                )
            ).decode()

        else:
            return jsonify({"encrypt_algorithm_error": "Unsupported algorithm."}), 400

        return jsonify({"ciphertext": ciphertext})

    except Exception as e:
        logger.error(f"Error in encryption - {e}.")
        return jsonify({"Fatal error": f"Encryption failed: {str(e)}."}), 500

##########################################################################################################################################################
# Decrypt the ciphertext using the specified key and algorithm
    
# DecryptionRequest model
class DecryptionRequest(BaseModel):
    key_id: str
    ciphertext: str
    algorithm: str

# Decryption Endpoint
@app.route("/decrypt", methods=["POST"])
def decrypt():
    try:
        data = request.get_json()
        key_id = data.get("key_id")
        ciphertext = data.get("ciphertext")
        algorithm = data.get("algorithm")
        
        logger.info(f"Decrypting message with key_id: {key_id}.")

        if key_id not in keys_store:
            return jsonify({"Key_id_error": "Key not available."}), 404

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

            unpadder = aes_padding.PKCS7(algorithms.AES.block_size).unpadder()
            plaintext = unpadder.update(padded_plaintext) + unpadder.finalize()
            plaintext = plaintext.decode()

        elif algorithm == "RSA":
            try:
                # RSA decryption uses the private key to decrypt
                plaintext = key.decrypt(
                    base64.b64decode(ciphertext),
                    rsa_padding.OAEP(
                        mgf = rsa_padding.MGF1(algorithm=hashes.SHA512()),
                        algorithm = hashes.SHA512(),
                        label = None
                    )
                ).decode()
            except Exception as e:
                return jsonify({"Fatal error": f"RSA decryption failed: {str(e)}."}), 500

        else:
            return jsonify({"decrypt_algorithm_error": "Unsupported algorithm."}), 400

        return jsonify({"plaintext": plaintext})

    except (ValueError, binascii.Error) as e:
        return jsonify({"Fatal error": f"Decryption failed: {str(e)}"}), 500

##########################################################################################################################################################
# Generate a hash of the data using the specified algorithm
        
# HashGeneration model
class HashGeneration(BaseModel):
    data: str
    algorithm: str

# Hash Generation Endpoint
@app.route("/generate-hash", methods=["POST"])
def generate_hash():
    try:
        data = request.get_json()
        text = data.get("data")
        algorithm = data.get("algorithm")

        logger.info(f"Generating Hash using Algorithm: {algorithm}")

        if algorithm not in ["SHA-256", "SHA-512"]:
            return jsonify({"hashing_algorithm_error": "Unsupported hashing algorithm"}), 400

        if algorithm == "SHA-256":
            digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        elif algorithm == "SHA-512":
            digest = hashes.Hash(hashes.SHA512(), backend=default_backend())

        digest.update(text.encode())
        hash_value = base64.b64encode(digest.finalize()).decode()

        return jsonify({"hash_value": hash_value, "algorithm": algorithm})

    except Exception as e:
        logger.error(f"Hash generation error: {e}")
        return jsonify({"Fatal error": f"Hash generation failed: {str(e)}"}), 500

##########################################################################################################################################################
# Verify if the provided hash matches the hash computed from the data using the specified algorithm
    
# HashVerification model
class HashVerification(BaseModel):
    data: str
    hash_value: str
    algorithm: str

# Hash Verification Endpoint
@app.route("/verify-hash", methods=["POST"])
def verify_hash():
    try:
        data = request.get_json()
        text = data.get("data")
        hash_value = data.get("hash_value")
        algorithm = data.get("algorithm")

        logger.info(f"Verifying hash: {hash_value}")

        if algorithm not in ["SHA-256", "SHA-512"]:
            return jsonify({"hashing_algorithm_error": "Unsupported hashing algorithm"}), 400

        if algorithm == "SHA-256":
            digest = hashes.Hash(hashes.SHA256(), backend=default_backend())
        elif algorithm == "SHA-512":
            digest = hashes.Hash(hashes.SHA512(), backend=default_backend())

        digest.update(text.encode())
        computed_hash = base64.b64encode(digest.finalize()).decode()

        is_valid = computed_hash == hash_value
        message = "Hash matches the data." if is_valid else "Hash does not match the data."

        return jsonify({"hash_validity": is_valid, "message": message})

    except Exception as e:
        logger.error(f"Hash verification error: {e}")
        return jsonify({"Fatal error": f"Hash verification failed : {str(e)}"}), 500

##########################################################################################################################################################
    
# Run the API
if __name__ == "__main__":
    app.run(debug=True)
