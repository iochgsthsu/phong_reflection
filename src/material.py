import os
from typing import List, Tuple, Optional
class Material():
    def __init__(self, ka : float, kd : float, ks : float, n : float, color: Tuple[int, int, int] = (128, 128, 128)):
        self.ka = ka
        self.kd = kd
        self.ks = ks
        self.n = n
        self.color = color

    def __init__(self, filename):
        self.directory = "./materials/"
        self.path = self.directory + filename
        self.ka = None
        self.kd = None
        self.ks = None
        self.n = None
        self.color = None

        if not os.path.exists(self.path):
            raise FileNotFoundError(f"Nie znaleziono pliku materiału: {self.path}")

        with open(self.path, "r", encoding="utf-8") as file:
            for idx, line in enumerate(file):
                line = line.strip()

                if not line or line.startswith('#'):
                    continue

                elements = line.split()
                type = elements[0]

                if type == "ka":
                    self.ka = float(elements[1])
                elif type == "kd":
                    self.kd = float(elements[1])
                elif type == "ks":
                    self.ks = float(elements[1])
                elif type == "n":
                    self.n = float(elements[1])
                elif type == "color":
                    self.color = tuple(int(i) for i in elements[1:])
                else:
                    raise ValueError(f"Nieprawidłowy typ elementu '{type}' w linii {idx+1}.")


