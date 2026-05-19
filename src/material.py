from typing import List, Tuple, Optional
class Material():
    def __init__(self, ka : float, kd : float, ks : float, n : float, color: Tuple[int, int, int] = (128, 128, 128)):
        self.ka = ka
        self.kd = kd
        self.ks = ks
        self.n = n
        self.color = color