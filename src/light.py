import numpy as np
class Light():
    def __init__(self,
                position: np.ndarray =  np.array([0.0, 0.0, 0.0], dtype=float),
                intensity: np.ndarray = np.array([1.0, 1.0, 1.0], dtype=float),
                f_a: float = 0.5):
        self.position = position
        self.intensity = intensity
        self.f_a = f_a