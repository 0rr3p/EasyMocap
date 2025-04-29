#!/usr/bin/env python3
import os
import sys
import yaml
import json
import csv
import numpy as np

def evaluate_boxes(boxes_path, keypoints_dir):
    """
    Valuta la presenza dei finger-tip negli AABB definiti in boxes_path
    per ogni frame (file JSON) in keypoints_dir.

    Ritorna:
      - matrix: numpy array (n_frames, n_boxes) di 1/0
      - frames: lista dei nomi dei file JSON (frame)
      - box_ids: lista degli ID dei box, nello stesso ordine delle colonne
    """
    # 1) Carica i box dal YAML
    with open(boxes_path, "r") as f:
        data = yaml.safe_load(f)
    boxes = data.get("boxes", [])
    if not boxes:
        raise ValueError(f"Nessuna box trovata in {boxes_path}")

    box_ids = [b.get("id", f"box{j}") for j, b in enumerate(boxes)]

    # 2) fingertip indices
    tip_indices = [4, 8, 12, 16, 20]

    # 3) elenco e ordinamento dei file di keypoints
    files = sorted([
        fn for fn in os.listdir(keypoints_dir)
        if fn.lower().endswith(".json")
    ])

    n_frames = len(files)
    n_boxes  = len(boxes)
    matrix   = np.zeros((n_frames, n_boxes), dtype=int)

    for i, fname in enumerate(files):
        frame_path = os.path.join(keypoints_dir, fname)
        with open(frame_path, "r") as f:
            arr = json.load(f)
        if not isinstance(arr, list) or len(arr) == 0:
            continue
        frame = arr[0]

        for j, box in enumerate(boxes):
            mn = np.array(box["min"], dtype=float)
            mx = np.array(box["max"], dtype=float)
            box_hit = False

            for hand_key in ("handl3d", "handr3d"):
                pts = frame.get(hand_key, [])
                tips = []
                for idx in tip_indices:
                    if idx < len(pts):
                        p = pts[idx]
                        if any(abs(coord) > 1e-6 for coord in p[:3]):
                            tips.append(np.array(p[:3], dtype=float))
                if not tips:
                    continue
                inside = sum(1 for p in tips
                             if np.all(p >= mn) and np.all(p <= mx))
                if inside / len(tips) >= 0.8:
                    box_hit = True
                    break

            matrix[i, j] = 1 if box_hit else 0

    return matrix, files, box_ids

def main():
    # ora accetta 2 o 3 argomenti
    if len(sys.argv) not in (3, 4):
        print("Usage: python evaluate_boxes.py <boxes.yml> <keypoints_folder> [<output_csv>]")
        sys.exit(1)

    boxes_path    = sys.argv[1]
    keypoints_dir = sys.argv[2]
    csv_path      = sys.argv[3] if len(sys.argv) == 4 else "results.csv"

    mat, frames, box_ids = evaluate_boxes(boxes_path, keypoints_dir)

    # 1) Stampa frame e riga corrispondente
    for i, frame in enumerate(frames):
        row = mat[i].tolist()
        print(f"{frame}: {row}")

    # 2) Salva in CSV (nel percorso scelto o default)
    header = ["frame"] + box_ids
    with open(csv_path, "w", newline="") as csvfile:
        writer = csv.writer(csvfile)
        writer.writerow(header)
        for i, frame in enumerate(frames):
            writer.writerow([frame] + mat[i].tolist())

    print(f"\nTutti i risultati sono stati salvati in: {csv_path}")

if __name__ == "__main__":
    main()
