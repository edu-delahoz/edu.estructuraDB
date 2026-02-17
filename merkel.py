import hashlib

def sha256(data):
    """Computes the SHA-256 hash of the given data."""
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def build_merkle_tree_4_inputs(data_nodes):
    """Builds a Merkle tree for exactly 4 inputs."""
    if len(data_nodes) != 4:
        raise ValueError("This function expects exactly 4 data nodes.")

    # Leaf nodes (L1, L2, L3, L4)
    h0 = sha256(data_nodes[0])
    h1 = sha256(data_nodes[1])
    h2 = sha256(data_nodes[2])
    h3 = sha256(data_nodes[3])

    # First level of internal nodes (H12, H34)
    h01 = sha256(h0 + h1)
    h23 = sha256(h2 + h3)

    # Merkle Root (H1234)
    merkle_root = sha256(h01 + h23)

    tree = {
        'leaves': [h0, h1, h2, h3],
        'level_1': [h01, h23],
        'root': merkle_root
    }
    return tree

# Example usage for 4 inputs: a, b, c, d
inputs = ['a', 'b', 'c', 'd']
merkle_tree = build_merkle_tree_4_inputs(inputs)

print("Merkle Tree for inputs a, b, c, d:")
print(f"  Leaf hashes: {merkle_tree['leaves']}")
print(f"  Level 1 hashes: {merkle_tree['level_1']}")
print(f"  Merkle Root: {merkle_tree['root']}")
