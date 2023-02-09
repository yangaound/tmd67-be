<?php

$data=$argv[1];
$key=$argv[2];
$iv=$argv[3];

$encrypted_data=bin2hex(openssl_encrypt($data, "AES-256-CBC", $key, OPENSSL_RAW_DATA, $iv));
echo $encrypted_data;

?>