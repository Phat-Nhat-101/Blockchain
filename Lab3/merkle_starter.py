from __future__ import annotations

import hashlib


def H(b: bytes) -> bytes:
    """
    Băm dữ liệu bằng SHA-256.
    Kết quả trả về là 32 byte, không phải chuỗi hex.
    """
    return hashlib.sha256(b).digest()


def merkle_root(leaves: list[bytes]) -> bytes:
    """
    Dựng cây Merkle từ dưới lên và trả về Merkle root.
    """

    # Không thể tạo cây nếu danh sách lá rỗng
    if not leaves:
        raise ValueError("Danh sách leaves không được rỗng")

    # Tạo bản sao để không thay đổi danh sách ban đầu
    level = list(leaves)

    # Tiếp tục gộp cho đến khi chỉ còn một node
    while len(level) > 1:

        # Nếu tầng có số node lẻ, nhân đôi node cuối
        if len(level) % 2 == 1:
            level.append(level[-1])

        next_level = []

        # Ghép từng cặp trái-phải để tạo node cha
        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1]

            parent = H(left + right)
            next_level.append(parent)

        # Chuyển lên tầng tiếp theo
        level = next_level

    # Node duy nhất còn lại là Merkle root
    return level[0]


def merkle_proof(
    leaves: list[bytes],
    index: int
) -> list[tuple[bytes, bool]]:
    """
    Tạo Merkle proof cho lá ở vị trí index.

    Mỗi phần tử trong proof có dạng:
    (sibling_hash, sibling_is_left)

    sibling_is_left = True:
        sibling nằm bên trái node hiện tại.

    sibling_is_left = False:
        sibling nằm bên phải node hiện tại.
    """

    if not leaves:
        raise ValueError("Danh sách leaves không được rỗng")

    if index < 0 or index >= len(leaves):
        raise IndexError("index nằm ngoài danh sách leaves")

    level = list(leaves)
    current_index = index
    proof = []

    while len(level) > 1:

        # Quy tắc Bitcoin: tầng lẻ thì nhân đôi node cuối
        if len(level) % 2 == 1:
            level.append(level[-1])

        # Tìm vị trí node anh em
        if current_index % 2 == 0:
            # Node hiện tại ở bên trái
            sibling_index = current_index + 1
        else:
            # Node hiện tại ở bên phải
            sibling_index = current_index - 1

        sibling_hash = level[sibling_index]
        sibling_is_left = sibling_index < current_index

        proof.append(
            (sibling_hash, sibling_is_left)
        )

        # Tạo tầng cha
        next_level = []

        for i in range(0, len(level), 2):
            left = level[i]
            right = level[i + 1]

            parent = H(left + right)
            next_level.append(parent)

        level = next_level

        # Chỉ số node cha
        current_index = current_index // 2

    return proof


def verify_proof(
    leaf_hash: bytes,
    proof: list[tuple[bytes, bool]],
    root: bytes
) -> bool:
    """
    Dùng leaf hash và proof để tính lại Merkle root.
    """

    current_hash = leaf_hash

    for sibling_hash, sibling_is_left in proof:

        if sibling_is_left:
            # Sibling bên trái nên phải ghép sibling trước
            current_hash = H(
                sibling_hash + current_hash
            )
        else:
            # Sibling bên phải nên ghép current trước
            current_hash = H(
                current_hash + sibling_hash
            )

    return current_hash == root


# ==========================================================
# Phần kiểm tra
# ==========================================================

if __name__ == "__main__":

    # Tạo tám giao dịch mẫu
    txs = [
        f"tx{i}: A->B {i} coin".encode()
        for i in range(8)
    ]

    # Băm từng giao dịch để tạo tám lá
    leaves = [H(tx) for tx in txs]

    # Tính Merkle root
    root = merkle_root(leaves)

    print("root:", root.hex())

    # CHECK 1:
    # Proof phải hợp lệ cho cả tám lá
    all_proofs_valid = all(
        verify_proof(
            leaves[i],
            merkle_proof(leaves, i),
            root
        )
        for i in range(8)
    )

    print(
        "CHECK 1 (all 8 proofs valid):",
        "OK" if all_proofs_valid else "FAIL"
    )

    # CHECK 2:
    # Cây có tám lá nên proof dài log2(8) = 3
    proof_for_leaf_4 = merkle_proof(leaves, 4)

    print(
        "CHECK 2 (proof length == 3):",
        "OK" if len(proof_for_leaf_4) == 3 else "FAIL"
    )

    # CHECK 3:
    # Sửa nội dung giao dịch thì proof phải thất bại
    fake_leaf = H(b"tx4: A->B 999999 coin")

    fake_is_valid = verify_proof(
        fake_leaf,
        merkle_proof(leaves, 4),
        root
    )

    print(
        "CHECK 3 (tampered leaf fails):",
        "OK" if not fake_is_valid else "FAIL"
    )

    # CHECK 4:
    # Kiểm tra cây có số lá lẻ
    leaves_7 = leaves[:7]
    root_7 = merkle_root(leaves_7)

    odd_count_works = all(
        verify_proof(
            leaves_7[i],
            merkle_proof(leaves_7, i),
            root_7
        )
        for i in range(7)
    )

    print(
        "CHECK 4 (odd count works):",
        "OK" if odd_count_works else "FAIL"
    )