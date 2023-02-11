<?php

$data=$argv[1];
$key=$argv[2];
$iv=$argv[3];

$decrypted_data=openssl_decrypt(hex2bin($data), "AES-256-CBC", $key, OPENSSL_RAW_DATA|OPENSSL_ZERO_PADDING, $iv);
echo $decrypted_data;

?>