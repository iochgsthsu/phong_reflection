import pygame
from typing import Tuple, Optional
from .camera import Camera
from .bsp import BSPTreeNode
from .polygon import Polygon
from .light import Light
import numpy as np
LIGHT_BLUE = (173, 216, 230)
BLACK = (0, 0, 0)
EPSILON = 1e-12
class Renderer():
    def __init__(self, 
                 screen: pygame.Surface,
                 camera: Camera,
                 bsp_root: BSPTreeNode,
                 light: Light = Light(),
                 intensity: float = 1,
                 bg_color: Tuple[int, int, int] = LIGHT_BLUE,
                 draw_wireframe: bool = False,
                 wireframe_color: Tuple[int, int, int] = BLACK,
                 wireframe_width: int = 1
                ):
        
        self.screen = screen
        self.height = self.screen.get_height()
        self.width = self.screen.get_width()
        self.camera = camera
        self.bsp_root = bsp_root
        self.bg_color = bg_color
        
        self.light = light
        self.intensity = intensity

        
        self.draw_wireframe = draw_wireframe
        self.wireframe_color = wireframe_color
        self.wireframe_width = wireframe_width

    def phong(self, p: Polygon) -> None:
        
        N = p.normal
        N_norm = np.linalg.norm(N)
        if N_norm < EPSILON:
            return p.material.color
        N = N / N_norm

        P = np.mean([v[:3] for v in p.vertices], axis=0)

        L = self.light.position - P
        L_norm = np.linalg.norm(L)
        if L_norm < EPSILON:
            return p.material.color
        L = L/L_norm

        V = self.camera.position - P
        V_norm = np.linalg.norm(V)
        if V_norm < EPSILON:
            return p.material.color
        V = V/V_norm

        ndotl = max(np.dot(N, L), 0.0)


        spec = 0.0
        if ndotl > 0.0:
            R = 2.0 * ndotl * N - L
            R_norm = np.linalg.norm(R)
            if R_norm >= EPSILON:
                R = R / R_norm
                rdotv = max(np.dot(R, V), 0.0)
                spec = rdotv ** p.material.n

        background = self.intensity * p.material.ka
        diffuse = self.light.intensity * p.material.kd * ndotl
        directional = self.light.intensity * p.material.ks * spec
        I = background + self.light.f_att(P) * (diffuse + directional)
        I = np.maximum(I, 0.0)

        base = np.array(p.material.color, dtype=float) / 255.0
        rgb = np.clip(base * I, 0.0, 1.0) * 255.0
        return (int(rgb[0]), int(rgb[1]), int(rgb[2]))

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
                color = self.phong(poly)
                pygame.draw.polygon(self.screen, color, projected_points)
                if self.draw_wireframe:
                    pygame.draw.polygon(self.screen, self.wireframe_color, projected_points, self.wireframe_width)
