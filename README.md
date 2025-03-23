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
### 1. Generate a Hash
#### **POST** `/generate-hash`
Creates a hash digest using SHA-256 or SHA-512.

**Request Body:**
```json
{
  "data": "Hello, world!",
  "algorithm": "SHA-256" # OR "SHA-512"
}
```
**Response:**
```json
{
  "hash_value": "...base64 encoded hash...",
  "algorithm": "SHA-256"
}
```

### 2. Verify a Hash
#### **POST** `/verify-hash`
Verifies if the given plaintext matches a previously generated hash.

**Request Body:**
```json
{
  "data": "Hello, world!",
  "hash_value": "...previously generated hash...", # use correct digest with the data
  "algorithm": "SHA-256" # OR "SHA-512"
}
```
**Response:**
```json
{
  "is_valid": true,
  "message": "Hash matches the data."
}
```
### 3. Generate a Key
#### **POST** `/generate-key`
Generates an AES or RSA key.

**Request Body:**
```json
{
  "key_type": "RSA", # OR AES
  "key_size": 2048 # Any valid size mentioned above
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

### 4. Encrypt Data
#### **POST** `/encrypt`
Encrypts a plaintext using AES or RSA.

**Request Body (AES Example):**
```json
{
  "key_id": "1", # Change according to generated key ID
  "plaintext": "Hello, world!",
  "algorithm": "AES" # OR RSA
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
  "key_id": "1", # Change according to generated key ID
  "ciphertext": "...base64 encoded ciphertext...", # Use generated ciphertext
  "algorithm": "AES" # OR RSA
}
```
**Response:**
```json
{
  "plaintext": "Hello, world!"
}
```

## Testing
The API was tested using **Postman** and a Python Notebook. 

```
BASE_URL = "https://pase.pythonanywhere.com"
```

For the required function you can use following as **url** to POST requests. Make sure that your json is in the correct format as mentioned above.
- **Hashing** `url = f"{ BASE_URL }/generate-hash`
- **Verify hash** `url = f"{ BASE_URL }/verify-hash`
- **Key generation** `url = f"{ BASE_URL }/generate-key`
- **Encryption** `url = f"{ BASE_URL }/encrypt`
- **Decryption** `url = f"{ BASE_URL }/decrypt`

Then create the **json** file as mentioned above (ex: `data {"key_type": "RSA", "key_size": 2048 }}`) depending on your request. And finally post the request as,

```
response = requests.post (url , json = data )
print(response.json())
```

## Repository
🔗 **GitHub Repository:** [https://github.com/D-Vinod/Cryptographic-API-Implementation](https://github.com/D-Vinod/Cryptographic-API-Implementation)

## Contributors
- **Amarasekara A.T.P.** ([https://github.com/thisariii01](https://github.com/thisariii01))
- **Bandara D.M.D.V.** ([https://github.com/D-Vinod](https://github.com/D-Vinod))
- **Samarasekera A.M.P.S.** ([https://github.com/PaSe-Sam](https://github.com/PaSe-Sam))
- **Wijetunga W.L.N.K.** ([https://github.com/namiwijeuom](https://github.com/namiwijeuom})
