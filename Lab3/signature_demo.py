from eth_account import Account
from eth_account.messages import encode_defunct


# ==========================================================
# BƯỚC 1: Tạo một tài khoản Ethereum ngẫu nhiên
# ==========================================================

# Chỉ dùng cho bài lab, không dùng tài khoản này để giữ tiền thật
acct = Account.create()

print("=== ACCOUNT ===")
print("Original address:", acct.address)


# ==========================================================
# BƯỚC 2: Tạo thông điệp cần ký
# ==========================================================

message_text = "I attended Session 3 / Toi da hoc Buoi 3"

msg = encode_defunct(text=message_text)

print("\n=== ORIGINAL MESSAGE ===")
print("Message:", message_text)


# ==========================================================
# BƯỚC 3: Ký cùng thông điệp hai lần bằng cùng private key
# ==========================================================

sig1 = Account.sign_message(msg, acct.key)
sig2 = Account.sign_message(msg, acct.key)

print("\n=== SIGNATURE ===")
print("r:", hex(sig1.r))
print("s:", hex(sig1.s))
print("v:", sig1.v)
print("Signature:", sig1.signature.hex())

print(
    "Two signatures are identical:",
    sig1.signature == sig2.signature
)


# ==========================================================
# BƯỚC 4: Khôi phục địa chỉ từ thông điệp và chữ ký
# ==========================================================

recovered_address = Account.recover_message(
    msg,
    signature=sig1.signature
)

print("\n=== RECOVERY ===")
print("Recovered address:", recovered_address)
print(
    "Recovered matches original:",
    recovered_address == acct.address
)


# ==========================================================
# BƯỚC 5: Sửa một ký tự trong thông điệp
# ==========================================================

tampered_text = "I attended Session 3 / Toi da hoc Buoi 4"

tampered_msg = encode_defunct(text=tampered_text)

tampered_address = Account.recover_message(
    tampered_msg,
    signature=sig1.signature
)

print("\n=== TAMPERED MESSAGE ===")
print("Tampered message:", tampered_text)
print("Tampered recovered address:", tampered_address)
print(
    "Tampered matches original:",
    tampered_address == acct.address
)