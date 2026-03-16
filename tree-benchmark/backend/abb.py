"""Implementación simple de un Árbol Binario de Búsqueda (ABB) para usuarios."""

from __future__ import annotations


class ABBNode:
    """Nodo del ABB que almacena un usuario y referencias a hijos."""

    def __init__(self, user: dict) -> None:
        self.user = user
        self.left: ABBNode | None = None
        self.right: ABBNode | None = None


class ABBTree:
    """Árbol Binario de Búsqueda ordenado por el campo `id`."""

    def __init__(self) -> None:
        self.root: ABBNode | None = None

    def insert(self, user: dict) -> None:
        """Inserta un usuario en el árbol, validando IDs duplicados."""
        user_id = self._validate_user(user)

        if self.root is None:
            self.root = ABBNode(user)
            return

        current = self.root
        while current is not None:
            current_id = int(current.user["id"])
            if user_id < current_id:
                if current.left is None:
                    current.left = ABBNode(user)
                    return
                current = current.left
            elif user_id > current_id:
                if current.right is None:
                    current.right = ABBNode(user)
                    return
                current = current.right
            else:
                raise ValueError(f"ID duplicado detectado: {user_id}")

    def search(self, user_id: int) -> dict | None:
        """Busca un usuario por ID exacto y retorna su diccionario o None."""
        current = self.root
        while current is not None:
            current_id = int(current.user["id"])
            if user_id == current_id:
                return current.user
            if user_id < current_id:
                current = current.left
            else:
                current = current.right
        return None

    def inorder(self) -> list[dict]:
        """Retorna los usuarios recorridos en orden ascendente de ID."""
        ordered_users: list[dict] = []
        self._inorder_recursive(self.root, ordered_users)
        return ordered_users

    def bulk_insert(self, users: list[dict]) -> None:
        """Inserta múltiples usuarios desde una lista de diccionarios."""
        for user in users:
            self.insert(user)

    def _inorder_recursive(self, node: ABBNode | None, result: list[dict]) -> None:
        """Recorrido in-order recursivo interno."""
        if node is None:
            return
        self._inorder_recursive(node.left, result)
        result.append(node.user)
        self._inorder_recursive(node.right, result)

    def _validate_user(self, user: dict) -> int:
        """Valida estructura mínima del usuario y retorna su ID como entero."""
        required_keys = {"id", "nombre", "email", "edad"}
        missing = required_keys - set(user.keys())
        if missing:
            missing_fields = ", ".join(sorted(missing))
            raise ValueError(f"Usuario inválido, faltan campos: {missing_fields}")

        try:
            return int(user["id"])
        except (TypeError, ValueError) as error:
            raise ValueError("El campo 'id' debe ser un entero válido.") from error


def main() -> None:
    """Prueba simple de inserción, búsqueda y recorrido in-order."""
    users = [
        {"id": 3, "nombre": "Usuario 3", "email": "u3@example.com", "edad": 25},
        {"id": 1, "nombre": "Usuario 1", "email": "u1@example.com", "edad": 21},
        {"id": 4, "nombre": "Usuario 4", "email": "u4@example.com", "edad": 29},
        {"id": 2, "nombre": "Usuario 2", "email": "u2@example.com", "edad": 23},
    ]

    tree = ABBTree()
    tree.bulk_insert(users)

    found = tree.search(2)
    not_found = tree.search(10)
    ordered = tree.inorder()

    print("search(2):", found)
    print("search(10):", not_found)
    print("inorder IDs:", [user["id"] for user in ordered])


if __name__ == "__main__":
    main()