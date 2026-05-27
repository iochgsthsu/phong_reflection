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

    def shade_vertex(self, P, N, material):
        Nlen = np.linalg.norm(N)
        if Nlen < 1e-12: return np.array(material.color)/255.0
        N = N / Nlen

        L = self.light.position - P
        d = np.linalg.norm(L)
        L = L / (d+1e-12)

        V = self.camera.position - P
        V = V / (np.linalg.norm(V)+1e-12)

        ndotl = max(np.dot(N, L), 0.0)
        spec = 0.0

        if ndotl > 0.0:
            R = 2.0*ndotl*N - L
            rdotv = max(np.dot(R/(np.linalg.norm(R)+1e-12), V), 0.0)
            spec = rdotv ** material.n

        Ia = self.intensity * material.ka
        Id = self.light.intensity * material.kd * ndotl
        Is = self.light.intensity * material.ks * spec

        I = Ia + self.light.f_att(P) * (Id + Is)

        return np.clip((np.array(material.color, dtype=float)/255.0) * I, 0.0, 1.0)

    def phong(self, p: Polygon):
        if hasattr(p, "vertex_normals") and p.vertex_normals:
            cols = []
            for v, n in zip(p.vertices, p.vertex_normals):
                cols.append(self.shade_vertex(v[:3], n, p.material))
            avg = np.mean(cols, axis=0)

        else:
            P = np.mean([v[:3] for v in p.vertices], axis=0)
            avg = self.shade_vertex(P, p.normal, p.material)

        rgb = (avg * 255.0).astype(int)

        return (int(rgb[0]), int(rgb[1]), int(rgb[2]))

    def draw_shaded_triangle(self, pts, cols):
        surf = self.screen
        xs = [p[0] for p in pts]; ys = [p[1] for p in pts]
        
        minx = max(min(xs), 0)
        maxx = min(max(xs), self.width-1)
        miny = max(min(ys), 0)
        maxy = min(max(ys), self.height-1)

        x0,y0 = pts[0]; x1,y1 = pts[1]; x2,y2 = pts[2]

        denom = (y1 - y2)*(x0 - x2) + (x2 - x1)*(y0 - y2)
        if abs(denom) < 1e-6:
            return

        surf.lock()
        for yy in range(miny, maxy+1):
            for xx in range(minx, maxx+1):
                w0 = ((y1 - y2)*(xx - x2) + (x2 - x1)*(yy - y2)) / denom
                w1 = ((y2 - y0)*(xx - x2) + (x0 - x2)*(yy - y2)) / denom
                w2 = 1.0 - w0 - w1
                if w0 >= 0 and w1 >= 0 and w2 >= 0:
                    col = w0*cols[0] + w1*cols[1] + w2*cols[2]
                    surf.set_at((xx, yy), (int(col[0]), int(col[1]), int(col[2])))
        surf.unlock()
    
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
                if hasattr(poly, "vertex_normals") and poly.vertex_normals:
                    vert_colors = []
                    for v, n in zip(poly.vertices, poly.vertex_normals):
                        c = self.shade_vertex(v[:3], n, poly.material)
                        vert_colors.append((c * 255.0).astype(float))
                else:
                    c = self.shade_vertex(np.mean([v[:3] for v in poly.vertices], axis=0), poly.normal, poly.material)
                    vert_colors = [ (c * 255.0).astype(float) ] * len(projected_points)

                n = len(projected_points)
                if n == 3:
                    self.draw_shaded_triangle(projected_points, vert_colors)
                else:
                    for i in range(1, n-1):
                        tri_pts = [projected_points[0], projected_points[i], projected_points[i+1]]
                        tri_cols = [vert_colors[0], vert_colors[i], vert_colors[i+1]]
                        self.draw_shaded_triangle(tri_pts, tri_cols)