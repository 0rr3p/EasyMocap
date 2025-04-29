#!/usr/bin/env python3
import sys
import yaml
import numpy as np
import open3d as o3d

def visualize_boxes(yaml_path):
    # 1. Carica le definizioni delle box
    with open(yaml_path, "r") as f:
        data = yaml.safe_load(f)
    boxes = data.get("boxes", [])
    if not boxes:
        print(f"Nessuna box trovata in {yaml_path}")
        return

    # 2. Prepara colori ciclici per le box
    colors = [
        [1.0, 0.0, 0.0],  # rosso
        [0.0, 1.0, 0.0],  # verde
        [0.0, 0.0, 1.0],  # blu
        [1.0, 1.0, 0.0],  # giallo
        [1.0, 0.0, 1.0],  # magenta
        [0.0, 1.0, 1.0],  # ciano
    ]

    geometries = []
    for i, box in enumerate(boxes):
        mn = np.array(box["min"], dtype=float)
        mx = np.array(box["max"], dtype=float)

        # 2a. Crea l'AABB e il suo LineSet
        aabb = o3d.geometry.AxisAlignedBoundingBox(min_bound=mn, max_bound=mx)
        lines = o3d.geometry.LineSet.create_from_axis_aligned_bounding_box(aabb)
        lines.paint_uniform_color(colors[i % len(colors)])
        geometries.append(lines)

        # 2b. (Opzionale) un piccolo sistema di assi al centro per etichettare
        center = (mn + mx) / 2
        frame = o3d.geometry.TriangleMesh.create_coordinate_frame(
            size=np.linalg.norm(mx - mn) * 0.1,
            origin=center
        )
        geometries.append(frame)

    # 3. Aggiungi un sistema di coordinate globale
    #    (taglia il bounding box più grande per dimensionare opportunamente gli assi)
    all_mins = np.array([b["min"] for b in boxes], dtype=float)
    all_maxs = np.array([b["max"] for b in boxes], dtype=float)
    scene_extent = np.max(all_maxs - all_mins)
    global_axes = o3d.geometry.TriangleMesh.create_coordinate_frame(
        size=scene_extent * 0.2,
        origin=(np.min(all_mins, axis=0))
    )
    geometries.append(global_axes)

    # 4. Visualizzazione interattiva
    o3d.visualization.draw_geometries(
        geometries,
        window_name="3D Bounding Boxes",
        width=1024, height=768,
        left=50, top=50,
        point_show_normal=False
    )

def main():
    if len(sys.argv) != 2:
        print("Usage: python view.py <boxes.yml>")
        sys.exit(1)
    visualize_boxes(sys.argv[1])

if __name__ == "__main__":
    main()
