def merkle_root(leaves: list[bytes]) -> bytes:
    if not leaves:
        raise ValueError("leaves must not be empty")

    level = list(leaves)

    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])

        level = [
            H(level[i] + level[i + 1])
            for i in range(0, len(level), 2)
        ]

    return level[0]

def merkle_proof(
    leaves: list[bytes],
    index: int
) -> list[tuple[bytes, bool]]:
    if not leaves:
        raise ValueError("leaves must not be empty")

    if index < 0 or index >= len(leaves):
        raise IndexError("leaf index out of range")

    level = list(leaves)
    proof = []
    current_index = index

    while len(level) > 1:
        if len(level) % 2 == 1:
            level.append(level[-1])

        if current_index % 2 == 0:
            sibling_index = current_index + 1
        else:
            sibling_index = current_index - 1

        sibling_is_left = sibling_index < current_index

        proof.append(
            (level[sibling_index], sibling_is_left)
        )

        level = [
            H(level[i] + level[i + 1])
            for i in range(0, len(level), 2)
        ]

        current_index //= 2

    return proof



def verify_proof(
    leaf_hash: bytes,
    proof: list[tuple[bytes, bool]],
    root: bytes
) -> bool:
    current = leaf_hash

    for sibling_hash, sibling_is_left in proof:
        if sibling_is_left:
            current = H(sibling_hash + current)
        else:
            current = H(current + sibling_hash)

    return current == root