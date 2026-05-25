import pygame
import numpy as np
import os
from src.object import Object
from src.camera import Camera
from src.renderer import Renderer
from src.bsp import BSPTreeNode
from src.polygon import Polygon
from src.material import Material
from src.light import Light
from datetime import datetime
import random

WIDTH, HEIGHT = 800, 600
BG = (0, 0, 0)
MOVE_SPEED = 10.0
ROTATION_SPEED = 100.0
FOCAL_SPEED = 2.0

MAX_FOCAL = 5.0
MIN_FOCAL = 0.05

LIGHT_SPEED = 10.0
MAX_LIGHT = 50.0
MIN_LIGHT = 0.1

FRAMERATE = 60.0
DIV = 1000.0

def main() -> None:
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    pygame.display.set_caption("Phong reflection model")
    clock = pygame.time.Clock()
    sphere = Object("sphere.txt")
    sphere.translate(0, 0, 20)
    materials = ['polished_copper.txt', "bronze.txt", "brass.txt"]
    materials_idx = 0
    material_filename = materials[materials_idx]

    material = Material(material_filename)

    polygons = []
    sphere_t = sphere.transformed_vertices()
    for face in sphere.faces:
        polygon_v = [sphere_t[i] for i in face]
        polygons.append(Polygon(polygon_v,material))
    bsp_root = BSPTreeNode(polygons)

    screenshots_dir = "./screenshots/"
    if not os.path.exists(screenshots_dir):
        os.mkdir(screenshots_dir)

    cam = Camera()
    light = Light()
    ren = Renderer(screen, cam, bsp_root=bsp_root, bg_color=BG, light=light)
    
    running = True
    while running:

        dt = clock.tick(FRAMERATE) / DIV

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_m:
                    materials_idx = (materials_idx + 1) % len(materials)
                    material = Material(materials[materials_idx])
                    for poly in polygons:
                        poly.material = material

        ren.draw_scene()

        keys = pygame.key.get_pressed()
        
        #Translacja
        if keys[pygame.K_w]:
            cam.translate_local(np.array([0.0, 0.0, MOVE_SPEED * dt]))

        if keys[pygame.K_s]:
            cam.translate_local(np.array([0.0, 0.0,  -MOVE_SPEED * dt]))

        if keys[pygame.K_a]:
            cam.translate_local(np.array([-MOVE_SPEED * dt, 0.0, 0.0]))

        if keys[pygame.K_d]:
            cam.translate_local(np.array([ MOVE_SPEED * dt, 0.0, 0.0]))

        if keys[pygame.K_r]:
            cam.translate_local(np.array([0.0,  MOVE_SPEED * dt, 0.0]))

        if keys[pygame.K_f]:
            cam.translate_local(np.array([0.0, -MOVE_SPEED * dt, 0.0]))
            
        #Rotacja
        if keys[pygame.K_LEFT]:
            cam.rotate( -ROTATION_SPEED * dt, "y")

        if keys[pygame.K_RIGHT]:
            cam.rotate(ROTATION_SPEED * dt, "y")

        if keys[pygame.K_UP]:
            cam.rotate( -ROTATION_SPEED * dt, "x")

        if keys[pygame.K_DOWN]:
            cam.rotate(ROTATION_SPEED * dt, "x")

        if keys[pygame.K_q]:
            cam.rotate( ROTATION_SPEED * dt, "z")

        if keys[pygame.K_e]:
            cam.rotate(-ROTATION_SPEED * dt, "z")

        #Ogniskowa
        if keys[pygame.K_z]:
            cam.focal = min(MAX_FOCAL, cam.focal + FOCAL_SPEED * dt)
        if keys[pygame.K_x]:
            cam.focal = max(MIN_FOCAL, cam.focal - FOCAL_SPEED * dt)

        #Intensywność światła

        if keys[pygame.K_KP_PLUS] or (keys[pygame.K_EQUALS] and (keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT])):
            light.intensity = np.clip(light.intensity + LIGHT_SPEED * dt, MIN_LIGHT, MAX_LIGHT)
        if keys[pygame.K_KP_MINUS] or keys[pygame.K_MINUS]:
            light.intensity = np.clip(light.intensity - LIGHT_SPEED * dt, MIN_LIGHT, MAX_LIGHT)

        #Reset i wyjście
        if keys[pygame.K_h]:
            cam.position = np.array([0.0, 0.0, 0.0], dtype=float)
            cam.orientation = np.eye(3, dtype=float)
            cam.focal = 0.5
        
        if keys[pygame.K_ESCAPE]:
            running = False

        #Zrzut ekranu
        if keys[pygame.K_p]:
            name = datetime.now().strftime("vc_%Y%m%d_%H%M%S.png")
            pygame.image.save(screen, screenshots_dir + name)

                
        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()