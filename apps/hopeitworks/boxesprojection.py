#!/usr/bin/env python3
import os
import yaml
import numpy as np
import cv2
import argparse
import pandas as pd
from os.path import join
from easymocap.mytools import read_camera, Undistort, projectN3

def load_boxes(yml_path):
    """
    Carica i parallelepipedi da YAML:
      boxes:
        - id: <string>
          min: [x_min, y_min, z_min]
          max: [x_max, y_max, z_max]
    Restituisce punti 3D, spigoli e lista di ID.
    """
    with open(yml_path, 'r') as f:
        data = yaml.safe_load(f)
    comps = data.get('boxes')
    if not isinstance(comps, list):
        raise ValueError(f"{yml_path} non contiene una chiave 'boxes' valida")

    ids = []
    all_pts, all_lines = [], []
    for idx, comp in enumerate(comps):
        comp_id = comp.get('id', f'box{idx}')
        ids.append(comp_id)
        mn, mx = comp['min'], comp['max']
        verts = np.array([
            [mn[0], mn[1], mn[2]],
            [mx[0], mn[1], mn[2]],
            [mx[0], mx[1], mn[2]],
            [mn[0], mx[1], mn[2]],
            [mn[0], mn[1], mx[2]],
            [mx[0], mn[1], mx[2]],
            [mx[0], mx[1], mx[2]],
            [mn[0], mx[1], mx[2]],
        ])
        verts = np.hstack((verts, np.ones((8, 1))))
        all_pts.append(verts)

        base = 8 * idx
        edges = np.array([
            [0, 1], [1, 2], [2, 3], [3, 0],
            [4, 5], [5, 6], [6, 7], [7, 4],
            [0, 4], [1, 5], [2, 6], [3, 7],
        ], dtype=np.int64) + base
        all_lines.append(edges)

    points3d = np.vstack(all_pts)
    lines3d  = np.vstack(all_lines)
    return points3d, lines3d, ids

class BoxDrawer:
    def __init__(self, path, out, ext, ids, points3d, lines, write=False):
        self.path = path
        self.ext = ext
        self.ids = ids
        self.points3d = points3d
        self.lines = lines
        self.p3d = points3d[:, :3]
        self.write = write

        cams = read_camera(join(out, 'intri.yml'), join(out, 'extri.yml'))
        cams.pop('basenames', None)
        self.cameras = cams
        self.camnames = sorted(cams.keys())

        # cartella base per le immagini annotate
        self.outdir = join(out, 'boxes')
        os.makedirs(self.outdir, exist_ok=True)
        # creo una sottocartella per ciascuna camera
        if self.write:
            for cam in self.camnames:
                os.makedirs(join(self.outdir, cam), exist_ok=True)

        print('[check] cameras:', self.camnames)

    def draw_frame(self, frame, results_row=None):
        hits = []
        if results_row:
            hits = [cid for cid in self.ids if bool(results_row.get(cid, 0))]

        for cam in self.camnames:
            cam_data = self.cameras[cam]
            img_path = join(self.path, 'images', cam, f"{frame:06d}{self.ext}")
            if not os.path.exists(img_path):
                print(f"[WARN] Immagine non trovata: {img_path}")
                continue

            img = cv2.imread(img_path)
            img = Undistort.image(img, cam_data['K'], cam_data['dist'])
            kpts2d = projectN3(self.p3d, [cam_data['P']])[0]

            for idx, comp_id in enumerate(self.ids):
                start_pt = idx * 8
                end_pt   = start_pt + 8
                pts2d_box = kpts2d[start_pt:end_pt, :2].astype(int)
                edges = self.lines[idx*12:(idx+1)*12] - start_pt
                hit   = comp_id in hits
                color = (0, 255, 0) if hit else (0, 0, 255)
                for e in edges:
                    p1 = tuple(pts2d_box[e[0]])
                    p2 = tuple(pts2d_box[e[1]])
                    cv2.line(img, p1, p2, color, thickness=1)
                center = tuple(pts2d_box.mean(axis=0).astype(int))
                cv2.putText(img, comp_id, center,
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, color,
                            thickness=1, lineType=cv2.LINE_AA)

            if self.write:
                # salvo in <out>/boxes/<cam>/<frame>.jpg
                outname = join(self.outdir, cam, f"{frame:06d}{self.ext}")
                cv2.imwrite(outname, img)

def main():
    parser = argparse.ArgumentParser(
        description="Disegna i parallelepipedi (opzionale colorazione da risultati).")
    parser.add_argument('path',        help='cartella root delle immagini')
    parser.add_argument('--out',       required=True,
                        help='cartella con intri.yml ed extri.yml')
    parser.add_argument('--boxes-yml', required=True,
                        help='YAML con definizione dei parallelepipedi')
    parser.add_argument('--results',   help='CSV o Excel con matrice risultati (frame×box)')
    parser.add_argument('--ext',       default='.jpg', choices=['.jpg', '.png'],
                        help='estensione delle immagini')
    parser.add_argument('--write', action='store_true',
                        help='salva le immagini annotate in <out>/boxes')
    args = parser.parse_args()

    points3d, lines, ids = load_boxes(args.boxes_yml)

    # se --results è passato, carica il DataFrame, altrimenti useremo solo proiezione
    results = None
    if args.results:
        if args.results.lower().endswith(('.xls', '.xlsx')):
            df = pd.read_excel(args.results, index_col=0)
        else:
            df = pd.read_csv(args.results, index_col=0)
        new_idx = [int(os.path.splitext(str(x))[0]) for x in df.index]
        df.index = new_idx
        df.sort_index(inplace=True)
        results = {frame: row.to_dict() for frame, row in df.iterrows()}

    drawer = BoxDrawer(args.path, args.out, args.ext,
                       ids, points3d, lines,
                       write=args.write)

    if results:
        frames = sorted(results.keys())
    else:
        # senza risultati, prendiamo i frame leggendo i file della prima camera
        cam0 = drawer.camnames[0]
        img_dir = join(args.path, 'images', cam0)
        frames = sorted(int(os.path.splitext(f)[0]) 
                        for f in os.listdir(img_dir)
                        if f.endswith(args.ext))

    for frame in frames:
        drawer.draw_frame(frame, results.get(frame) if results else None)

    print("Elaborazione completata.")

if __name__ == "__main__":
    main()
