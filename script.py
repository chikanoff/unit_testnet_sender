import time
import os
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

# Settings
SENDING_TIMEOUT = 1  # timeout between each transaction, 0 - without timeout(instantly)
RETRY_TIMEOUT = 3 # timeout between each retry if trans was failure
MAX_RETRIES = 5  # maximum number of retries

SEND_AMOUNT = 0.000001  # amount
NUM_TRANSACTIONS = 1000  # transaction count
GAS_LIMIT = 21000  # gas limit
GAS_PRICE = int(2 * 10**9)  # 1 Gwei in wei


RPC_URL = 'https://rpc-testnet.unit0.dev'
CHAIN_ID = 88817

SENDER_ADDRESS = os.getenv("SENDER_ADDRESS")  # real address of sender!!
PRIVATE_KEY = os.getenv("PRIVATE_KEY")  # real private key of sender!!

# Check if SENDER_ADDRESS and PRIVATE_KEY are set
if not SENDER_ADDRESS or not PRIVATE_KEY:
    print("Error: SENDER_ADDRESS and PRIVATE_KEY environment variables must be set.")
    exit(1)

def request_with_retries(data, retries=15, delay=3):
    for attempt in range(retries):
        try:
            response = requests.post(RPC_URL, json=data)
            response.raise_for_status()  # Raise an exception for HTTP errors
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"HTTP error: {e}")
            if attempt < retries - 1:
                print(f"Retrying in {delay} seconds...")
                time.sleep(delay)
            else:
                raise

def check_balance(address):
    data = {
        "jsonrpc": "2.0",
        "method": "eth_getBalance",
        "params": [address, "latest"],
        "id": 1
    }
    try:
        response_json = request_with_retries(data)
        if "result" in response_json:
            balance = int(response_json["result"], 16)
            return decimal.Decimal(balance) / 10**18
        else:
            print(f"Unexpected response format: {response_json}")
            raise Exception("No result field in JSON response")
    except Exception as e:
        print(f"Error checking balance: {e}")
        raise

def get_random_recipient_address():
    return random.choice(recipient_addresses)

def get_nonce(address):
    data = {
        "jsonrpc": "2.0",
        "method": "eth_getTransactionCount",
        "params": [address, "pending"],
        "id": 1
    }
    response_json = request_with_retries(data)
    return int(response_json["result"], 16)

def send_transaction(nonce, recipient_address):
    tx = {
        'nonce': nonce,
        'to': recipient_address,
        'value': hex(int(SEND_AMOUNT * 10**18)),
        'gas': hex(GAS_LIMIT),
        'gasPrice': hex(GAS_PRICE),
        'chainId': CHAIN_ID
    }

    signed_tx = Account.sign_transaction(tx, PRIVATE_KEY)
    tx_data = signed_tx.rawTransaction.hex()

    data = {
        "jsonrpc": "2.0",
        "method": "eth_sendRawTransaction",
        "params": [tx_data],
        "id": 1
    }

    response_json = request_with_retries(data)
    if "result" in response_json:
        return response_json["result"]
    else:
        print(response_json)
        raise Exception("No transaction hash received.")

def check_transaction_status(tx_hash, transaction_number):
    tx_receipt = None
    while tx_receipt is None:
        try:
            data = {
                "jsonrpc": "2.0",
                "method": "eth_getTransactionReceipt",
                "params": [tx_hash],
                "id": 1
            }
            response = requests.post(RPC_URL, json=data).json()
            tx_receipt = response["result"]
            if tx_receipt:
                print(f"{transaction_number} transaction receipt received")
            else:
                print(f"Waiting for transaction {transaction_number} to be mined...")
                time.sleep(3)
        except Exception as e:
            print(f"Exc: {e}")
            time.sleep(2)
    return tx_receipt

def main():
    for i in range(1, NUM_TRANSACTIONS + 1):
        balance = check_balance(SENDER_ADDRESS)
        required_amount = decimal.Decimal(SEND_AMOUNT) + decimal.Decimal(GAS_LIMIT) * decimal.Decimal(GAS_PRICE) / 10**18
        if balance < required_amount:
            print(f"Not enough balance for transaction {i}.Required balance: {required_amount}, Current balance: {balance}.")
            break

        recipient_address = get_random_recipient_address()
        
        for attempt in range(MAX_RETRIES):
            try:
                nonce = get_nonce(SENDER_ADDRESS)
                tx_hash = send_transaction(nonce, recipient_address)
                print(f"Transaction {i} sent. Nonce: {nonce}. Hash: {tx_hash}")
                time.sleep(SENDING_TIMEOUT)
                break
            except Exception as e:
                print(f"Error sending transaction {i} (attempt {attempt + 1}): {e}. Nonce: {nonce}")
                if attempt < MAX_RETRIES - 1:
                    print(f"Retrying transaction {i}...")
                    time.sleep(SENDING_TIMEOUT)
                else:
                    print(f"Max retries reached for transaction {i}.")
                    return

if __name__ == "__main__":
    main()
