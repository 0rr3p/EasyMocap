import FreeCAD, Mesh, os, yaml

doc = FreeCAD.ActiveDocument

# Raccoglie tutte le mesh splittate (Mesh::Feature)
meshes = [o for o in doc.Objects if o.TypeId == 'Mesh::Feature']

boxes = []
for m in meshes:
    bb = m.Mesh.BoundBox
    boxes.append({
        "id": m.Name,
        "min": [bb.XMin, bb.YMin, bb.ZMin],
        "max": [bb.XMax, bb.YMax, bb.ZMax]
    })

# Percorso di output (cambia pure se preferisci un'altra cartella)
out_path = os.path.join(os.path.expanduser("~"), "boxes.yml")
with open(out_path, 'w') as f:
    yaml.safe_dump({"boxes": boxes}, f, default_flow_style=False)

print(f"Esportate {len(boxes)} bounding‐boxes in:\n  {out_path}")
