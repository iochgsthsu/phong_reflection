import pygame
from typing import Tuple, Optional
from .camera import Camera
from .bsp import BSPTreeNode
from .polygon import Polygon
import numpy as np
LIGHT_BLUE = (173, 216, 230)
BLACK = (0, 0, 0)

class Renderer():
    def __init__(self, 
                 screen: pygame.Surface,
                 camera: Camera,
                 bsp_root: BSPTreeNode,
                 bg_color: Tuple[int, int, int] = LIGHT_BLUE,
                 draw_wireframe: bool = True,
                 wireframe_color: Tuple[int, int, int] = BLACK,
                 wireframe_width: int = 1
                ):
        
        self.screen = screen
        self.height = self.screen.get_height()
        self.width = self.screen.get_width()
        self.camera = camera
        self.bsp_root = bsp_root
        self.bg_color = bg_color
        
        self.draw_wireframe = draw_wireframe
        self.wireframe_color = wireframe_color
        self.wireframe_width = wireframe_width

    def draw_scene(self) -> None:
        self.screen.fill(self.bg_color)

        sorted_polygons: list[Polygon] = []
        self.bsp_root.traverse(self.camera.position, sorted_polygons)

        for poly in sorted_polygons:
            view_vector = poly.vertices[0][:3] - self.camera.position
            if np.dot(poly.normal, view_vector) >= 0:
                continue
            projected_points = []
            for vertex in poly.vertices:
                p = self.camera.projection(vertex, self.width, self.height)
                if p is None:
                    
                    projected_points = []
                    break
                projected_points.append(p)
            
            if len(projected_points) >= 3:
                pygame.draw.polygon(self.screen, poly.color, projected_points)
                if self.draw_wireframe:
                    pygame.draw.polygon(self.screen, self.wireframe_color, projected_points, self.wireframe_width)
