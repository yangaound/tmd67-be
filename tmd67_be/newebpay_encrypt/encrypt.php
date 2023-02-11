<?php

$data1=$argv[1];
$key=$argv[2];
$iv=$argv[3];

$edata1=bin2hex(openssl_encrypt($data1, "AES-256-CBC", $key,
OPENSSL_RAW_DATA, $iv));

echo $edata1;

?>