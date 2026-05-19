import numpy as np
from typing import List, Tuple, Optional
EPSILON = 1e-6
class Polygon:
    def __init__(self, ka: float, kd: float, ks: float, n: float,
                 vertices: List[np.ndarray],
                   color: Tuple[int, int, int] = (128, 128, 128)):
        if len(vertices) < 3:
            raise ValueError("Poligon musi mieć co najmniej 3 wierzchołki.")
        
        self.vertices = vertices
        self.color = color
        
        v0 = self.vertices[0][:3]
        v1 = self.vertices[1][:3]
        v2 = self.vertices[2][:3]

        self.ka = ka
        self.kd = kd
        self.ks = ks
        self.n = n
        
        self.normal = np.cross(v1 - v0, v2 - v0)
        norm_len = np.linalg.norm(self.normal)
        if norm_len > EPSILON:
            self.normal /= norm_len
        self.w = -np.dot(self.normal, v0)

    def classify_point(self, point: np.ndarray) -> str:
        dist = np.dot(self.normal, point[:3]) + self.w
        if dist > EPSILON:
            return "front"
        elif dist < -EPSILON:
            return "back"
        else:
            return "coplanar"

    def split(self, other: 'Polygon') -> Tuple[Optional['Polygon'], Optional['Polygon']]:
        point_status = [other.classify_point(v) for v in self.vertices]
        
        front_points, back_points = [], []
        
        num_vertices = len(self.vertices)
        for i in range(num_vertices):
            j = (i + 1) % num_vertices
            p1_status, p2_status = point_status[i], point_status[j]
            p1, p2 = self.vertices[i], self.vertices[j]

            if p1_status != "back": front_points.append(p1)
            if p1_status != "front": back_points.append(p1)

            if p1_status != p2_status and p1_status != "coplanar" and p2_status != "coplanar":
                t = (-(other.normal @ p1[:3]) - other.w) / (other.normal @ (p2[:3] - p1[:3]))
                intersection_point = p1 + t * (p2 - p1)
                front_points.append(intersection_point)
                back_points.append(intersection_point)

        front_poly, back_poly = None, None
        if len(front_points) >= 3:
            front_poly = Polygon(front_points, self.color)
        if len(back_points) >= 3:
            back_poly = Polygon(back_points, self.color)
            
        return front_poly, back_poly