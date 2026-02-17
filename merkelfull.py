
import hashlib

def sha256(data):
    if isinstance(data, bytes):
        return hashlib.sha256(data).hexdigest()
    return hashlib.sha256(data.encode('utf-8')).hexdigest()

def build_merkle_tree(data_nodes):
    if not data_nodes:
        raise ValueError("No puede estar vacia.")

    # Compute leaf hashes
    current_level = [sha256(node) for node in data_nodes]
    tree_levels = [current_level]

    while len(current_level) > 1:
        next_level = []
        for i in range(0, len(current_level), 2):
            hash1 = current_level[i]
            hash2 = current_level[i + 1] if i + 1 < len(current_level) else hash1 # Handle odd number of hashes
            next_level.append(sha256(hash1 + hash2))
        current_level = next_level
        tree_levels.append(current_level)

    merkle_root = current_level[0]

    return {
        'leaves': tree_levels[0],
        'levels': tree_levels[1:], 
        'root': merkle_root
    }

inputs_general_1 = ['apple', 'banana', 'cherry', 'date', 'elderberry', 'fig']
merkle_tree_general_1 = build_merkle_tree(inputs_general_1)

print("\n--- Merkle Tree for general inputs (6 items): ---")
print(f"  Original Inputs: {inputs_general_1}")
print(f"  Leaf Hashes: {merkle_tree_general_1['leaves']}")
for i, level in enumerate(merkle_tree_general_1['levels']):
    print(f"  Level {i+1} Hashes: {level}")
print(f"  Merkle Root: {merkle_tree_general_1['root']}")

inputs_general_2 = ['one', 'two', 'three'] # Example with odd number of inputs
merkle_tree_general_2 = build_merkle_tree(inputs_general_2)

print("\n--- Merkle Tree for general inputs (3 items): ---")
print(f"  Original Inputs: {inputs_general_2}")
print(f"  Leaf Hashes: {merkle_tree_general_2['leaves']}")
for i, level in enumerate(merkle_tree_general_2['levels']):
    print(f"  Level {i+1} Hashes: {level}")
print(f"  Merkle Root: {merkle_tree_general_2['root']}")
