from web3 import Web3


try:
    from web3.middleware import ExtraDataToPOAMiddleware

    POA_MIDDLEWARE = ExtraDataToPOAMiddleware
except ImportError:
    from web3.middleware import geth_poa_middleware

    POA_MIDDLEWARE = geth_poa_middleware


RPC_URL = "https://l1testnet.trustkeys.network"

# Thay nội dung trong dấu ngoặc kép
TX_HASH = "0x1234..."


w3 = Web3(
    Web3.HTTPProvider(
        RPC_URL,
        request_kwargs={"timeout": 30}
    )
)

w3.middleware_onion.inject(
    POA_MIDDLEWARE,
    layer=0
)

if not w3.is_connected():
    raise ConnectionError(
        "Không kết nối được TrustKeys RPC"
    )


receipt = w3.eth.get_transaction_receipt(
    TX_HASH
)

tx = w3.eth.get_transaction(
    TX_HASH
)

block = w3.eth.get_block(
    receipt["blockNumber"]
)


base_fee = block["baseFeePerGas"]
gas_used = receipt["gasUsed"]
effective_price = receipt["effectiveGasPrice"]

paid = gas_used * effective_price
burned = gas_used * base_fee

tip = gas_used * (
    effective_price - base_fee
)


print("=== TRANSACTION ===")
print("Hash:", TX_HASH)
print("Type:", tx["type"])
print("Block:", receipt["blockNumber"])
print("Status:", receipt["status"])

print()
print("=== GAS ===")
print("Gas used:", gas_used)
print("Base fee:", base_fee, "wei")
print(
    "Effective gas price:",
    effective_price,
    "wei"
)

print()
print("=== FEE DECOMPOSITION ===")
print("Paid:", paid, "wei")
print("Burned:", burned, "wei")
print("Tip:", tip, "wei")

print()
print(
    "Paid in coin:",
    w3.from_wei(paid, "ether")
)

print(
    "Burned in coin:",
    w3.from_wei(burned, "ether")
)

print(
    "Tip in coin:",
    w3.from_wei(tip, "ether")
)

print()
print(
    "CHECK - paid == burned + tip:",
    "OK" if paid == burned + tip else "FAIL"
)

print(
    "CHECK - transaction type == 2:",
    "OK" if tx["type"] == 2 else "FAIL"
)

print(
    "CHECK - successful transaction:",
    "OK" if receipt["status"] == 1 else "FAIL"
)