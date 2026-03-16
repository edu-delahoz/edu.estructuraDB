"""Implementación académica de un Árbol B+ para usuarios por `id`."""

from __future__ import annotations

from bisect import bisect_left, bisect_right


class BPlusNode:
    """Nodo base del árbol B+ (interno o hoja)."""

    def __init__(self, is_leaf: bool) -> None:
        self.is_leaf = is_leaf
        self.keys: list[int] = []


class BPlusLeafNode(BPlusNode):
    """Nodo hoja que guarda claves y registros completos de usuario."""

    def __init__(self) -> None:
        super().__init__(is_leaf=True)
        self.values: list[dict] = []
        self.next_leaf: BPlusLeafNode | None = None


class BPlusInternalNode(BPlusNode):
    """Nodo interno que guarda claves separadoras e hijos."""

    def __init__(self) -> None:
        super().__init__(is_leaf=False)
        self.children: list[BPlusNode] = []


class BPlusTree:
    """Árbol B+ orientado a búsquedas exactas y por rango de IDs."""

    def __init__(self, order: int = 4) -> None:
        """Crea el árbol.

        `order` define el máximo de hijos por nodo interno.
        Con order=4: máximo 3 claves por nodo, tamaño didáctico y fácil de seguir.
        """
        if order < 3:
            raise ValueError("El orden del árbol debe ser al menos 3.")

        self.order = order
        self.max_keys = order - 1
        self.root: BPlusNode = BPlusLeafNode()

    def insert(self, user: dict) -> None:
        """Inserta un usuario. Rechaza IDs duplicados explícitamente."""
        user_id = self._validate_user(user)

        promoted = self._insert_recursive(self.root, user_id, user)
        if promoted is not None:
            promoted_key, new_right = promoted
            new_root = BPlusInternalNode()
            new_root.keys = [promoted_key]
            new_root.children = [self.root, new_right]
            self.root = new_root

    def search(self, user_id: int) -> dict | None:
        """Busca por ID exacto y retorna el usuario o None."""
        leaf = self._find_leaf(user_id)
        idx = bisect_left(leaf.keys, user_id)
        if idx < len(leaf.keys) and leaf.keys[idx] == user_id:
            return leaf.values[idx]
        return None

    def range_search(self, start_id: int, end_id: int) -> list[dict]:
        """Retorna usuarios con IDs en [start_id, end_id], ordenados."""
        if start_id > end_id:
            return []

        result: list[dict] = []
        leaf = self._find_leaf(start_id)

        while leaf is not None:
            for key, value in zip(leaf.keys, leaf.values):
                if key < start_id:
                    continue
                if key > end_id:
                    return result
                result.append(value)
            leaf = leaf.next_leaf

        return result

    def bulk_insert(self, users: list[dict]) -> None:
        """Inserta múltiples usuarios desde una lista de diccionarios."""
        for user in users:
            self.insert(user)

    def _find_leaf(self, user_id: int) -> BPlusLeafNode:
        """Encuentra la hoja donde debería estar el ID."""
        node = self.root
        while not node.is_leaf:
            internal = node  # type: ignore[assignment]
            assert isinstance(internal, BPlusInternalNode)
            child_index = bisect_right(internal.keys, user_id)
            node = internal.children[child_index]
        assert isinstance(node, BPlusLeafNode)
        return node

    def _insert_recursive(
        self,
        node: BPlusNode,
        user_id: int,
        user: dict,
    ) -> tuple[int, BPlusNode] | None:
        """Inserta recursivamente. Retorna promoción si hubo split."""
        if node.is_leaf:
            assert isinstance(node, BPlusLeafNode)
            return self._insert_into_leaf(node, user_id, user)

        assert isinstance(node, BPlusInternalNode)
        child_index = bisect_right(node.keys, user_id)
        promoted = self._insert_recursive(node.children[child_index], user_id, user)

        if promoted is None:
            return None

        promoted_key, new_right_child = promoted
        node.keys.insert(child_index, promoted_key)
        node.children.insert(child_index + 1, new_right_child)

        if len(node.keys) <= self.max_keys:
            return None

        return self._split_internal(node)

    def _insert_into_leaf(
        self,
        leaf: BPlusLeafNode,
        user_id: int,
        user: dict,
    ) -> tuple[int, BPlusNode] | None:
        """Inserta en hoja y la divide si supera capacidad."""
        idx = bisect_left(leaf.keys, user_id)
        if idx < len(leaf.keys) and leaf.keys[idx] == user_id:
            raise ValueError(f"ID duplicado detectado: {user_id}")

        leaf.keys.insert(idx, user_id)
        leaf.values.insert(idx, user)

        if len(leaf.keys) <= self.max_keys:
            return None

        return self._split_leaf(leaf)

    def _split_leaf(self, leaf: BPlusLeafNode) -> tuple[int, BPlusNode]:
        """Divide una hoja y retorna clave promotora + nuevo nodo derecho."""
        split_index = (len(leaf.keys) + 1) // 2

        right_leaf = BPlusLeafNode()
        right_leaf.keys = leaf.keys[split_index:]
        right_leaf.values = leaf.values[split_index:]

        leaf.keys = leaf.keys[:split_index]
        leaf.values = leaf.values[:split_index]

        right_leaf.next_leaf = leaf.next_leaf
        leaf.next_leaf = right_leaf

        promoted_key = right_leaf.keys[0]
        return promoted_key, right_leaf

    def _split_internal(self, node: BPlusInternalNode) -> tuple[int, BPlusNode]:
        """Divide un nodo interno y retorna clave promotora + nuevo derecho."""
        mid_index = len(node.keys) // 2
        promoted_key = node.keys[mid_index]

        right_node = BPlusInternalNode()
        right_node.keys = node.keys[mid_index + 1 :]
        right_node.children = node.children[mid_index + 1 :]

        node.keys = node.keys[:mid_index]
        node.children = node.children[: mid_index + 1]

        return promoted_key, right_node

    def _validate_user(self, user: dict) -> int:
        """Valida campos mínimos y retorna ID como entero."""
        required = {"id", "nombre", "email", "edad"}
        missing = required - set(user.keys())
        if missing:
            raise ValueError(f"Usuario inválido, faltan campos: {', '.join(sorted(missing))}")

        try:
            return int(user["id"])
        except (TypeError, ValueError) as error:
            raise ValueError("El campo 'id' debe ser un entero válido.") from error


def main() -> None:
    """Prueba simple de inserciones, búsqueda exacta y por rango."""
    users = [
        {"id": 10, "nombre": "Ana", "email": "ana@example.com", "edad": 24},
        {"id": 4, "nombre": "Luis", "email": "luis@example.com", "edad": 30},
        {"id": 7, "nombre": "Marta", "email": "marta@example.com", "edad": 27},
        {"id": 15, "nombre": "Pablo", "email": "pablo@example.com", "edad": 35},
        {"id": 2, "nombre": "Sofía", "email": "sofia@example.com", "edad": 21},
        {"id": 20, "nombre": "Diego", "email": "diego@example.com", "edad": 29},
    ]

    tree = BPlusTree(order=4)
    tree.bulk_insert(users)

    print("search(7):", tree.search(7))
    print("search(99):", tree.search(99))

    in_range = tree.range_search(5, 16)
    print("range_search(5, 16) IDs:", [user["id"] for user in in_range])


if __name__ == "__main__":
    main()