from Crypto.Cipher import AES
from Crypto.Util.Padding import pad, unpad
import numpy as np
import hashlib
import cv2
import sys


def hash_key(key):
    hash = hashlib.sha256(key.encode())
    p = hash.digest()
    key = p
    iv = p.ljust(16)[:16]
    nonce = iv[:8]
    return key, iv, nonce


def encrypt_image(imageOrig, key, mode):
    key, iv, nonce = hash_key(key)
    ivSize = len(iv)

    rowOrig, columnOrig, depthOrig = imageOrig.shape

    minWidth = (AES.block_size + AES.block_size) // depthOrig + 1
    if columnOrig < minWidth:
        print(
            "The minimum width of the image must be {} pixels, so that IV and padding can be stored in a single additional row!".format(
                minWidth
            )
        )
        sys.exit()

    imageOrigBytes = imageOrig.tobytes()

    match mode:
        case "ECB":
            cipher = AES.new(key, AES.MODE_ECB)
        case "CTR":
            cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
        case "CFB":
            cipher = AES.new(key, AES.MODE_CFB, iv=iv)
        case "CBC":
            cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    imageOrigBytesPadded = pad(imageOrigBytes, AES.block_size)
    ciphertext = cipher.encrypt(imageOrigBytesPadded)

    paddedSize = len(imageOrigBytesPadded) - len(imageOrigBytes)
    void = columnOrig * depthOrig - ivSize - paddedSize
    ivCiphertextVoid = iv + ciphertext + bytes(void)
    imageEncrypted = np.frombuffer(ivCiphertextVoid, dtype=imageOrig.dtype).reshape(
        rowOrig + 1, columnOrig, depthOrig
    )

    cv2.imwrite("ImageEncrypted.png", imageEncrypted)

    return imageEncrypted


def decrypt_image(imageEncrypted, key, mode):
    key, iv, nonce = hash_key(key)
    ivSize = len(iv)
    rowEncrypted, columnOrig, depthOrig = imageEncrypted.shape
    rowOrig = rowEncrypted - 1
    encryptedBytes = imageEncrypted.tobytes()
    imageOrigBytesSize = rowOrig * columnOrig * depthOrig
    paddedSize = (
        imageOrigBytesSize // AES.block_size + 1
    ) * AES.block_size - imageOrigBytesSize
    encrypted = encryptedBytes[ivSize : ivSize + imageOrigBytesSize + paddedSize]

    match mode:
        case "ECB":
            cipher = AES.new(key, AES.MODE_ECB)
        case "CTR":
            cipher = AES.new(key, AES.MODE_CTR, nonce=nonce)
        case "CFB":
            cipher = AES.new(key, AES.MODE_CFB, iv=iv)
        case "CBC":
            cipher = AES.new(key, AES.MODE_CBC, iv=iv)
    decryptedImageBytesPadded = cipher.decrypt(encrypted)
    decryptedImageBytes = unpad(decryptedImageBytesPadded, AES.block_size)

    decryptedImage = np.frombuffer(decryptedImageBytes, imageEncrypted.dtype).reshape(
        rowOrig, columnOrig, depthOrig
    )

    cv2.imwrite("decryptedImage.png", decryptedImage)

    return decryptedImage
