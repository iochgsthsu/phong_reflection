import math
#python .\scripts\make_sphere.py > .\objects\sphere.txt                                                                     
r = 10.0
stacks = 20
slices = 40 

verts = []

verts.append((0.0, r, 0.0))

for i in range(1, stacks):
    theta = math.pi * i / stacks
    sin_t = math.sin(theta)
    cos_t = math.cos(theta)
    for j in range(slices):
        phi = 2.0 * math.pi * j / slices
        x = r * sin_t * math.cos(phi)
        y = r * cos_t
        z = r * sin_t * math.sin(phi)
        verts.append((x, y, z))

verts.append((0.0, -r, 0.0))

def ring_index(i, j):
    return 1 + (i - 1) * slices + j

top = 0
bottom = len(verts) - 1
for v in verts:
    print(f"v {v[0]:.6f} {v[1]:.6f} {v[2]:.6f}")

for j in range(slices):
    v1 = ring_index(1, j)
    v2 = ring_index(1, (j + 1) % slices)
    print(f"f {v1+1} {top+1} {v2+1}")

for i in range(1, stacks - 1):
    for j in range(slices):
        a = ring_index(i, j)
        b = ring_index(i + 1, j)
        d = ring_index(i, (j + 1) % slices)
        c = ring_index(i + 1, (j + 1) % slices)
        print(f"f {a+1} {d+1} {b+1}")
        print(f"f {d+1} {c+1} {b+1}")

for j in range(slices):
    v1 = ring_index(stacks - 1, j)
    v2 = ring_index(stacks - 1, (j + 1) % slices)
    print(f"f {v1+1} {v2+1} {bottom+1}")