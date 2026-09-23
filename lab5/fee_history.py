from web3 import Web3


# Tương thích web3.py v6 và v7
try:
    from web3.middleware import ExtraDataToPOAMiddleware

    POA_MIDDLEWARE = ExtraDataToPOAMiddleware
except ImportError:
    from web3.middleware import geth_poa_middleware

    POA_MIDDLEWARE = geth_poa_middleware


RPC_URL = "https://l1testnet.trustkeys.network"

# Có thể dán địa chỉ MetaMask của bạn vào đây.
# Không dán private key hoặc seed phrase.
ADDRESS = ""


# ==========================================================
# KẾT NỐI RPC
# ==========================================================

w3 = Web3(
    Web3.HTTPProvider(
        RPC_URL,
        request_kwargs={"timeout": 30}
    )
)

# TrustKeys là mạng PoA clique
w3.middleware_onion.inject(
    POA_MIDDLEWARE,
    layer=0
)

if not w3.is_connected():
    raise ConnectionError(
        "Không kết nối được TrustKeys L1 RPC"
    )

print("CHECK 1 - RPC connection: OK")


# ==========================================================
# ĐỌC BLOCK MỚI NHẤT
# ==========================================================

chain_id = w3.eth.chain_id
latest = w3.eth.get_block("latest")

print()
print("=== NETWORK ===")
print("Chain ID:", chain_id)
print("Latest block:", latest["number"])
print("Gas limit:", latest["gasLimit"])
print("Gas used:", latest["gasUsed"])
print(
    "Transaction count:",
    len(latest["transactions"])
)
print(
    "Base fee:",
    latest["baseFeePerGas"],
    "wei"
)

print(
    "CHECK 2 - chainId == 11968:",
    "OK" if chain_id == 11968 else "FAIL"
)


# ==========================================================
# ĐỌC SỐ DƯ
# ==========================================================

if ADDRESS:
    checksum_address = Web3.to_checksum_address(
        ADDRESS
    )

    balance = w3.eth.get_balance(
        checksum_address
    )

    print()
    print("=== BALANCE ===")
    print("Address:", checksum_address)
    print("Balance:", balance, "wei")
    print(
        "Balance:",
        w3.from_wei(balance, "ether"),
        "coin"
    )
else:
    print()
    print("=== BALANCE ===")
    print(
        "Bỏ qua vì ADDRESS đang để trống."
    )


# ==========================================================
# LẤY LỊCH SỬ PHÍ 20 BLOCK
# ==========================================================

number_of_blocks = 20

fee_history = w3.eth.fee_history(
    number_of_blocks,
    "latest",
    [10, 50, 90]
)

oldest_block = fee_history["oldestBlock"]
base_fees = fee_history["baseFeePerGas"]
gas_ratios = fee_history["gasUsedRatio"]
rewards = fee_history.get("reward", [])

print()
print("=== FEE HISTORY ===")
print(
    f"{'Block':<12}"
    f"{'Base fee (wei)':<20}"
    f"{'Gas used':<15}"
    f"{'Tip p50 (gwei)':<18}"
)

for i in range(number_of_blocks):
    block_number = oldest_block + i
    base_fee = base_fees[i]
    gas_ratio = gas_ratios[i]

    if rewards and i < len(rewards):
        p50_tip = rewards[i][1]

        p50_gwei = float(
            w3.from_wei(p50_tip, "gwei")
        )
    else:
        p50_gwei = 0.0

    print(
        f"{block_number:<12}"
        f"{base_fee:<20}"
        f"{gas_ratio * 100:<14.2f}%"
        f"{p50_gwei:<18.9f}"
    )


# ==========================================================
# KẾT LUẬN CHUỖI BẬN HAY RẢNH
# ==========================================================

next_base_fee = base_fees[-1]

average_ratio = (
    sum(gas_ratios) / len(gas_ratios)
)

if average_ratio >= 0.50:
    verdict = "BUSY"
else:
    verdict = "quiet"

print()
print(
    "Next block projected base fee:",
    next_base_fee,
    "wei"
)

print(
    "Average gasUsedRatio:",
    f"{average_ratio * 100:.2f}%"
)

print("Chain verdict:", verdict)

print(
    "CHECK 3 - 20 gas ratios:",
    "OK" if len(gas_ratios) == 20 else "FAIL"
)

print(
    "CHECK 4 - 21 base fees:",
    "OK" if len(base_fees) == 21 else "FAIL"
)