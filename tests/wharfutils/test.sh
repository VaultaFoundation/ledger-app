#!/bin/bash

print_red() {
    printf "\e[31m$1\e[0m\n"
}

print_green() {
    printf "\e[32m$1\e[0m\n"
}

npm install 
if [ $? != 0 ]; then print_red "npm install failed"; exit 1; fi 
npx tsc serialize.ts
if [ $? != 0 ]; then print_red "conversion to javascript failed"; exit 1; fi 

# args json-data json-abi ouput-format abi-type 
simple_output=$(node serialize.js ./test-data/action-data.json ./test-data/action-data.abi.json utf8-string my_struct | cat -v)
if [ $simple_output == "^Cbar" ]; then 
    print_green "Passed Simple Test: UTF8 String"
else 
    print_red "Failed Simple Test: UTF8 String"
fi

hex_output=$(node serialize.js ./test-data/action-data.json ./test-data/action-data.abi.json hex my_struct)
if [ $hex_output == "03626172" ]; then 
    print_green "Passed Simple Test: Hex Format"
else 
    print_red "Failed Simple Test: Hex Format"
fi
python_byte_output=$(node serialize.js ./test-data/action-data.json ./test-data/action-data.abi.json python-byte-string my_struct)
if [ $python_byte_output == "b'\x03\x62\x61\x72'" ]; then 
    print_green "Passed Simple Test: Python Byte Format"
else 
    print_red "Failed Simple Test: Python Byte Format"
fi

expected_output="32342268befe0240e6e40000000001004c8eda6ca02e45000000572d3ccdcd013044c85865855c3400000000a8ed3232243044c85865855c34405dcc5865855c34a08601000000000004410000000000000374783200"
transaction_output=$(node serialize.js ./test-data/transfer-action.json ./abi/transaction.abi.json hex)
if [ $transaction_output == $expected_output ]; then
    print_green "Passed Transaction Test: Hex Format"
else
    print_red "Failed Transaction Test: Hex Format"
fi
transaction_hexdata_output=$(node serialize.js ./test-data/transfer-action-hexdata.json ./abi/transaction.abi.json hex)
if [ $transaction_output == $transaction_hexdata_output ]; then
    print_green "Passed Equalivant Test: JSon and Hex Action Data"
else
    print_red "Failed Equalivant Test: JSon and Hex Action Data"
fi