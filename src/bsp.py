import numpy as np
from typing import List, Tuple, Optional
from .polygon import Polygon
EPSILON = 1e-6
class BSPTreeNode:
    def __init__(self, polygons: List[Polygon]):
        self.divider: Optional[Polygon] = None
        self.coplanar_polygons: List[Polygon] = []
        self.front: Optional['BSPTreeNode'] = None
        self.back: Optional['BSPTreeNode'] = None
        
        if not polygons:
            return

        self.divider = polygons[0]
        self.coplanar_polygons.append(self.divider)

        front_polys, back_polys = [], []

        for poly in polygons[1:]:
            classification = self.classify_polygon(poly)
            
            if classification == "coplanar":
                self.coplanar_polygons.append(poly)
            elif classification == "front":
                front_polys.append(poly)
            elif classification == "back":
                back_polys.append(poly)
            elif classification == "spanning":
                front_part, back_part = poly.split(self.divider)
                if front_part:
                    front_polys.append(front_part)
                if back_part:
                    back_polys.append(back_part)
        
        if front_polys:
            self.front = BSPTreeNode(front_polys)
        if back_polys:
            self.back = BSPTreeNode(back_polys)

    def classify_polygon(self, polygon: Polygon) -> str:
        num_in_front = 0
        num_in_back = 0
        
        for vertex in polygon.vertices:
            pos = self.divider.classify_point(vertex)
            if pos == "front":
                num_in_front += 1
            elif pos == "back":
                num_in_back += 1
        
        if num_in_front > 0 and num_in_back > 0:
            return "spanning"
        if num_in_front > 0:
            return "front"
        if num_in_back > 0:
            return "back"
        
        return "coplanar"

    def traverse(self, camera_pos: np.ndarray, all_polygons: List[Polygon]) -> List[Polygon]:
        if not self.divider:
            return []

        camera_side = self.divider.classify_point(camera_pos)

        if camera_side == "front":
            if self.back: self.back.traverse(camera_pos, all_polygons)
            all_polygons.extend(self.coplanar_polygons)
            if self.front: self.front.traverse(camera_pos, all_polygons)
        elif camera_side == "back":
            if self.front: self.front.traverse(camera_pos, all_polygons)
            all_polygons.extend(self.coplanar_polygons)
            if self.back: self.back.traverse(camera_pos, all_polygons)
        else:
            if self.front: self.front.traverse(camera_pos, all_polygons)
            if self.back: self.back.traverse(camera_pos, all_polygons)
        
        return all_polygons