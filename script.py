import os
import time
import random
import decimal
import requests
from dotenv import load_dotenv
from eth_account import Account

recipient_addresses = [
    "address1",
    "address2"
]

load_dotenv()

# Настройки
RPC_URL = 'https://rpc-testnet.unit0.dev'
CHAIN_ID = 88817
SEND_AMOUNT = 0.00001  # amount in ETH
SENDER_ADDRESS = os.getenv("SENDER_ADDRESS")  # real address of sender!!
PRIVATE_KEY = os.getenv("PRIVATE_KEY")  # real private key of sender!!
NUM_TRANSACTIONS = 1000  # transaction count
GAS_LIMIT = 21000  # gas limit
GAS_PRICE = int(1.2 * 10**9)  # gas price in wei (1.2 gwei)

def check_balance(address):
    response = requests.post(RPC_URL, json={
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [address, "latest"],
        "id": 1
    })
    balance = int(response.json()['result'], 16)
    return decimal.Decimal(balance) / 10**18

def get_random_recipient_address():
    return random.choice(recipient_addresses)

def send_transaction(nonce, recipient_address):
    transaction = {
        'nonce': nonce,
        'to': recipient_address,
        'value': int(SEND_AMOUNT * 10**18),
        'gas': GAS_LIMIT,
        'gasPrice': GAS_PRICE,
        'chainId': CHAIN_ID
    }

    signed_txn = Account.sign_transaction(transaction, PRIVATE_KEY)
    tx_data = signed_txn.rawTransaction.hex()

    response = requests.post(RPC_URL, json={
        "jsonrpc": "2.0",
        "method": "eth_sendRawTransaction",
        "params": [tx_data],
        "id": 1
    })
    return response.json().get('result')

def check_transaction_status(tx_hash, transaction_number):
    tx_receipt = None
    while tx_receipt is None:
        try:
            response = requests.post(RPC_URL, json={
                "jsonrpc": "2.0",
                "method": "eth_getTransactionReceipt",
                "params": [tx_hash],
                "id": 1
            })
            tx_receipt = response.json()['result']
            if tx_receipt is None:
                time.sleep(2)
            else:
                print(f"{transaction_number} transaction receipt received")
        except Exception as e:
            print(f"Waiting for transaction {transaction_number} to be mined...")
            time.sleep(2)
    return tx_receipt

nonce_response = requests.post(RPC_URL, json={
    "jsonrpc": "2.0",
    "method": "eth_getTransactionCount",
    "params": [SENDER_ADDRESS, "latest"],
    "id": 1
})
nonce = int(nonce_response.json()['result'], 16)

for i in range(1, NUM_TRANSACTIONS + 1):
    balance = check_balance(SENDER_ADDRESS)
    required_amount = decimal.Decimal(SEND_AMOUNT) + decimal.Decimal(GAS_LIMIT) * decimal.Decimal(GAS_PRICE) / 10**18
    if balance < required_amount:
        print(f"Not enough balance for transaction {i}. Current balance: {balance} ETH")
        break

    recipient_address = get_random_recipient_address()

    try:
        tx_hash = send_transaction(nonce, recipient_address)
        if tx_hash:
            print(f"Transaction {i} sent. Nonce: {nonce}, Hash: {tx_hash}")
            receipt = check_transaction_status(tx_hash, i)
            if receipt and receipt['status'] == '0x1':
                print(f"Transaction {i} was successful")
            else:
                print(f"Transaction {i} failed")
            nonce += 1
        else:
            print(f"Error sending transaction {i}: No transaction hash received.")
            break
    except Exception as e:
        print(f"Error sending transaction {i}: {e}. Nonce: {nonce}")
        break
