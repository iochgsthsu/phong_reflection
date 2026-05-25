import numpy as np
class Light():
    def __init__(self,
                position: np.ndarray =  np.array([0.0, 0.0, 0.0], dtype=float),
                intensity: np.ndarray = np.array([20.0, 20.0, 20.0], dtype=float),):
        self.position = position
        self.intensity = intensity

    def f_att(self, point: np.ndarray) -> float:
        r = np.linalg.norm(point - self.position)
        c = 1.0
        denom = c + r
        return 1.0 / max(denom, 1e-6)