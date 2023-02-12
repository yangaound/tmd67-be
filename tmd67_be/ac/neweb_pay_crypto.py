import subprocess


def encrypt_trade_info(message: str, key: str, iv: str) -> bytes:
    from rest_framework.exceptions import ValidationError

    # Encrypt trade_info with php
    _cmd = [
        "php",
        "tmd67_be/newebpay_encrypt/encrypt.php",
        message,
        key,
        iv,
    ]
    _process = subprocess.Popen(_cmd, stdout=subprocess.PIPE)
    stdout, ret_code = _process.communicate(timeout=1)
    if ret_code is not None:
        raise ValidationError(f"execute '{_cmd}' fail: {stdout}")

    return stdout


def decrypt_trade_info(message: str, key: str, iv: str) -> str:
    from rest_framework.exceptions import ValidationError

    # Decrypt trade_info with php
    _cmd = [
        "php",
        "tmd67_be/newebpay_encrypt/decrypt.php",
        message,
        key,
        iv,
    ]
    _process = subprocess.Popen(_cmd, stdout=subprocess.PIPE)
    _stdout, ret_code = _process.communicate(timeout=2)
    decrypted_data = _stdout.decode()
    if ret_code is not None:
        raise ValidationError(f"execute '{_cmd}' fail: {decrypted_data}")

    # remove pad
    n = len(decrypted_data)
    for i in range(n):
        if decrypted_data[n - i - 1] == "}":
            break

    return decrypted_data[: n - i]
