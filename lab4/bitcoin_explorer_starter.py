def bits_to_target(bits: int) -> int:
    exponent = bits >> 24
    mantissa = bits & 0xFFFFFF

    if exponent <= 3:
        return mantissa >> (8 * (3 - exponent))

    return mantissa << (8 * (exponent - 3))

input_total = sum(
    vin["prevout"]["value"]
    for vin in tx["vin"]
)

output_total = sum(
    vout["value"]
    for vout in tx["vout"]
)

fee = input_total - output_total



def dsha256(data: bytes) -> bytes:
    return hashlib.sha256(
        hashlib.sha256(data).digest()
    ).digest()


def compute_merkle_root(txids: list[str]) -> str:
    if not txids:
        raise ValueError("txids must not be empty")

    # Đổi txid hiển thị sang thứ tự byte nội bộ
    level = [
        bytes.fromhex(txid)[::-1]
        for txid in txids
    ]

    while len(level) > 1:
        # Tầng lẻ: nhân đôi node cuối
        if len(level) % 2 == 1:
            level.append(level[-1])

        next_level = []

        for i in range(0, len(level), 2):
            parent = dsha256(
                level[i] + level[i + 1]
            )
            next_level.append(parent)

        level = next_level

    # Đảo lại để hiển thị giống block header
    return level[0][::-1].hex()