# Cryptographic API Implementation

## Introduction
This project is a **Cryptographic API** built using **FastAPI** and the **Cryptography** library, implementing both symmetric (AES) and asymmetric (RSA) encryption/decryption, along with hashing and hash verification functionalities. 

The API was tested locally using Postman and then deployed on **PythonAnywhere**, where it will remain available until **June 23rd, 2025**:

🔗 **API Endpoint**: [https://pase.pythonanywhere.com](https://pase.pythonanywhere.com)

## Features
- **Key Generation**
  - AES (128, 192, 256-bit keys)
  - RSA (2048, 3072, 4096-bit keys)
- **Encryption & Decryption**
  - AES-CBC (Symmetric Encryption)
  - RSA-OAEP (Asymmetric Encryption)
- **Hashing & Verification**
  - SHA-256
  - SHA-512

## API Endpoints
### 1. Generate a Key
#### **POST** `/generate-key`
Generates an AES or RSA key.

**Request Body:**
```json
{
  "key_type": "RSA",
  "key_size": 2048
}
```
**Response:**
```json
{
  "key_id": "1",
  "private_key": "...base64 encoded private key...",
  "public_key": "...base64 encoded public key..."
}
```

### 2. Generate a Hash
#### **POST** `/generate-hash`
Creates a hash digest using SHA-256 or SHA-512.

**Request Body:**
```json
{
  "data": "You are a wizard, Harry!",
  "algorithm": "SHA-256"
}
```
**Response:**
```json
{
  "hash_value": "...base64 encoded hash...",
  "algorithm": "SHA-256"
}
```

### 3. Verify a Hash
#### **POST** `/verify-hash`
Verifies if the given plaintext matches a previously generated hash.

**Request Body:**
```json
{
  "data": "You are a wizard, Harry!",
  "hash_value": "...previously generated hash...",
  "algorithm": "SHA-256"
}
```
**Response:**
```json
{
  "is_valid": true,
  "message": "Hash matches the data."
}
```

### 4. Encrypt Data
#### **POST** `/encrypt`
Encrypts a plaintext using AES or RSA.

**Request Body (AES Example):**
```json
{
  "key_id": "1",
  "plaintext": "Hello, world!",
  "algorithm": "AES"
}
```
**Response:**
```json
{
  "ciphertext": "...base64 encoded ciphertext..."
}
```

### 5. Decrypt Data
#### **POST** `/decrypt`
Decrypts a ciphertext using AES or RSA.

**Request Body (AES Example):**
```json
{
  "key_id": "1",
  "ciphertext": "...base64 encoded ciphertext...",
  "algorithm": "AES"
}
```
**Response:**
```json
{
  "plaintext": "Hello, world!"
}
```

## Deployment Instructions
This API was originally built with **FastAPI**, but it was later converted to **Flask** for easier deployment on **PythonAnywhere**.

### Steps to Deploy on PythonAnywhere:
1. Upload the **Flask application files** to the PythonAnywhere file system.
2. Create a **virtual environment** and install dependencies:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Configure the **WSGI settings** on PythonAnywhere's web app configuration page.
4. Restart the web app and test the API using Postman or a Python script.

## Testing
The API was tested using **Postman** and a Python Notebook. Below are some testing results:
- AES encryption produces different ciphertexts for the same input due to a random IV.
- RSA encryption produces different ciphertexts due to OAEP padding.
- Hash verification correctly detects mismatches.

## Repository
🔗 **GitHub Repository:** [https://github.com/D-Vinod/Cryptographic-API-Implementation](https://github.com/D-Vinod/Cryptographic-API-Implementation)

## Contributors
- **Amarasekara A.T.P.** ([https://github.com/thisariii01](https://github.com/thisariii01))
- **Bandara D.M.D.V.** ([https://github.com/D-Vinod](https://github.com/D-Vinod))
- **Samarasekera A.M.P.S.** ([https://github.com/PaSe-Sam](https://github.com/PaSe-Sam))
- **Wijetunga W.L.N.K.** ([https://github.com/namiwijeuom](https://github.com/namiwijeuom})
