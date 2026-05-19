import numpy as np
from typing import Optional, Tuple
class Camera:
    def __init__(self) -> None:
        self.position = np.array([0.0, 0.0, 0.0], dtype=float)
        self.orientation = np.eye(3, dtype=float)
        self.focal = 0.5

    def translate_world(self, v: np.ndarray) -> None:
        v = np.asarray(v, dtype=float)
        if v.shape[0] < 3:
            raise ValueError("Wektor translacji musi mieć 3 składowe")
        self.position += v[:3]

    def translate_local(self, v: np.ndarray) -> None:
        v = np.asarray(v, dtype=float)
        if v.shape[0] < 3:
            raise ValueError("Wektor translacji musi mieć 3 składowe")
        self.position += self.orientation @ v[:3]

    def rotate(self, deg: float, axis: str) -> None:
        ax = axis.lower()
        rad = np.deg2rad(deg)
        c, s = np.cos(rad), np.sin(rad)

        if ax == "x":
            r = np.array([
                [1.0, 0.0, 0.0],
                [0.0, c, -s],
                [0.0, s,  c],
            ], dtype=float)
        elif ax == "y":
            r = np.array([
                [ c, 0.0, s],
                [0.0, 1.0, 0.0],
                [-s, 0.0, c],
            ], dtype=float)
        elif ax == "z":
            r = np.array([
                [c, -s, 0.0],
                [s,  c, 0.0],
                [0.0, 0.0, 1.0],
            ], dtype=float)
        else:
            raise ValueError("Axis to 'x', 'y' albo 'z'")
        self.orientation = self.orientation @ r


    def view_matrix(self) -> np.ndarray:
        rt = self.orientation.T
        t = -rt @ self.position

        v = np.eye(4, dtype=float)
        v[:3, :3] = rt
        v[:3, 3] = t
        return v
    
    def projection_matrix(self, d: float) -> np.ndarray:
        return np.array([
            [1.0, 0.0, 0.0, 0.0],
            [0.0, 1.0, 0.0, 0.0],
            [0.0, 0.0, 1.0, 0.0],
            [0.0, 0.0, 1.0/d, 0.0],
        ], dtype=float)
    
    def projection(self, point: np.ndarray, width: int, height: int, scale: float = 400.0) -> Optional[Tuple[int, int]]:
        if point.shape == (3,):
            p = np.array([point[0], point[1], point[2], 1.0], dtype=float)
        elif point.shape == (4,):
            p = point.astype(float)
        else:
            raise ValueError("Point musi mieć kształt (3,) albo (4,)")
        
        view_p = self.view_matrix() @ p
        z_cam = view_p[2]
        if z_cam < 1e-12:
            return None

        result = self.projection_matrix(self.focal) @ view_p

        zd = result[3] #z/d

        if abs(zd) < 1e-12:
            return None

        #Normalizacja
        x_proj = result[0] / zd
        y_proj = result[1] / zd

        screen_x = int(width * 0.5 + x_proj * scale)
        screen_y = int(height * 0.5 - y_proj * scale)

        return (screen_x, screen_y)


if __name__ == "__main__":
    c = Camera()
