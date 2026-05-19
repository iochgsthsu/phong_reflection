import numpy as np
import os
from typing import List, Tuple

class Object:
    def __init__(self, filename: str):
        self.vertices: List[np.ndarray] = []
        self.faces: List[Tuple[int, ...]] = []

        self.directory = "./objects/"
        self.path = self.directory + filename

        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Nie znaleziono pliku obiektu: {self.path}")

        with open(self.path, "r", encoding="utf-8") as file:
            for idx, line in enumerate(file):
                line = line.strip()

                if not line or line.startswith('#'):
                    continue

                elements = line.split()
                type = elements[0]

                if type == "v":
                    if len(elements) != 4:
                        raise ValueError(f"Błąd w linii {idx+1}: wierzchołek 'v' wymaga 3 współrzędnych (x, y, z).")
                    
                    x, y, z = map(float, elements[1:4])
                    #print(x,y,z)
                    self.vertices.append(np.array([x, y, z, 1.0], dtype=float))

                elif type == "f":
                    if len(elements) < 4:
                        raise ValueError(f"Błąd w linii {idx+1}: ściana 'f' wymaga co najmniej 3 indeksów wierzchołków.")
                    indices = tuple(int(i) - 1 for i in elements[1:])
                    self.faces.append(indices)
                else:
                    raise ValueError(f"Nieprawidłowy typ elementu '{type}' w linii {idx+1}.")


        self.position = np.array([0.0, 0.0, 0.0], dtype=float)
        self.rotation = np.array([0.0, 0.0, 0.0], dtype=float) 
        self.scale = np.array([1.0, 1.0, 1.0], dtype=float)

    def translate(self, dx: float = 0.0, dy: float = 0.0, dz: float = 0.0) -> None:
        self.position += np.array([dx, dy, dz], dtype=float)

    def set_scale(self, sx: float = 1.0, sy: float = 1.0, sz: float = 1.0) -> None:
        self.scale = np.array([sx, sy, sz], dtype=float)

    def rotate(self, degree: float, axis: str) -> None:
        axis = axis.lower()
        if axis == "x":
            self.rotation[0] += degree
        elif axis == "y":
            self.rotation[1] += degree
        elif axis == "z":
            self.rotation[2] += degree
        else:
            raise ValueError("Oś obrotu musi być 'x', 'y' lub 'z'")

    def model_matrix(self) -> np.ndarray:
        rx, ry, rz = np.deg2rad(self.rotation)
        cx, sx = np.cos(rx), np.sin(rx)
        cy, sy = np.cos(ry), np.sin(ry)
        cz, sz = np.cos(rz), np.sin(rz)

        S = np.array([
            [self.scale[0], 0.0, 0.0, 0.0],
            [0.0, self.scale[1], 0.0, 0.0],
            [0.0, 0.0, self.scale[2], 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ], dtype=float)

        Rx = np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, cx, -sx, 0.0],
            [0.0, sx,  cx, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ], dtype=float)

        Ry = np.array([
            [ cy, 0.0, sy, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [-sy, 0.0, cy, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ], dtype=float)

        Rz = np.array([
            [cz, -sz, 0.0, 0.0],
            [sz,  cz, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 0.0, 1.0],
        ], dtype=float)

        T = np.array([
            [1.0, 0.0, 0.0, self.position[0]],
            [0.0, 1.0, 0.0, self.position[1]],
            [0.0, 0.0, 1.0, self.position[2]],
            [0.0, 0.0, 0.0, 1.0],
        ], dtype=float)

        return T @ Rz @ Ry @ Rx @ S

    def transformed_vertices(self) -> List[np.ndarray]:
        M = self.model_matrix()
        return [M @ v for v in self.vertices]

if __name__ == "__main__":
    pass