import binascii

from Crypto.Cipher import AES


def encrypt_trade_info(message: str, key: str, iv: str) -> bytes:
    # Generate a cipher object using the key
    cipher = AES.new(key.encode(), AES.MODE_CBC, iv.encode())

    # Pad the message to be a multiple of 16 bytes
    message += (AES.block_size - len(message) % AES.block_size) * chr(
        AES.block_size - len(message) % AES.block_size
    )
    return binascii.hexlify(cipher.encrypt(message.encode()))


def decrypt_trade_info(message: str, key: str, iv: str) -> str:
    # Generate a cipher object using the key
    cipher = AES.new(key.encode(), AES.MODE_CBC, iv.encode())
    decrypted_data = cipher.decrypt(binascii.unhexlify(message)).decode()

    # Remove pad
    n = len(decrypted_data)
    for i in range(n):
        if decrypted_data[n - i - 1] == "}":
            break
    return decrypted_data[: n - i]
