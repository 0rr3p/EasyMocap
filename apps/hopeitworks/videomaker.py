#!/usr/bin/env python3
import os
import sys
import argparse
import cv2
import numpy as np
import math


def create_grid_layout(images, rows, cols, h, w):
    """
    Dispone le immagini in una griglia rows x cols.
    Spazi extra vengono riempiti di nero.
    """
    grid = np.zeros((rows * h, cols * w, 3), dtype=np.uint8)
    for idx in range(rows * cols):
        r, c = divmod(idx, cols)
        y0, y1 = r * h, (r + 1) * h
        x0, x1 = c * w, (c + 1) * w
        if idx < len(images):
            grid[y0:y1, x0:x1] = images[idx]
    return grid


def create_multi_view_video(boxes_dir, output_path, fps=30, ext='.jpg'):
    """
    Crea un video multiview da N cartelle di immagini in boxes_dir,
    disponendo i frame in una griglia calcolata automaticamente.

    - Ignora sottocartelle nascoste (es. .ipynb_checkpoints).
    - Salta file di checkpoint Jupyter (contenenti '-checkpoint').
    """
    # 1) Elenca sottocartelle camera (escludendo hidden)
    cams = sorted([
        d for d in os.listdir(boxes_dir)
        if os.path.isdir(os.path.join(boxes_dir, d)) and not d.startswith('.')
    ])
    if not cams:
        raise ValueError(f"Nessuna cartella di camere in '{boxes_dir}'")

    # 2) Trova layout rows x cols
    N = len(cams)
    cols = math.ceil(math.sqrt(N))
    rows = math.ceil(N / cols)

    # 3) Unisci tutti i frame disponibili (skip '-checkpoint')
    frames_set = set()
    for cam in cams:
        cam_dir = os.path.join(boxes_dir, cam)
        for f in os.listdir(cam_dir):
            if f.endswith(ext) and '-checkpoint' not in f and not f.startswith('.'):
                frames_set.add(f)
    frames = sorted(frames_set)
    if not frames:
        raise FileNotFoundError(f"Nessun file '{ext}' trovato in '{boxes_dir}'/*/")

    # 4) Prepara VideoWriter basandosi sul primo frame valido
    first_img = None
    for cam in cams:
        path0 = os.path.join(boxes_dir, cam, frames[0])
        img0 = cv2.imread(path0)
        if img0 is not None:
            first_img = img0
            break
    if first_img is None:
        raise FileNotFoundError(f"Impossibile leggere alcun frame in '{boxes_dir}'")
    h, w = first_img.shape[:2]
    out_h, out_w = rows * h, cols * w

    # Scegli codec in base all'estensione di output
    ext_out = os.path.splitext(output_path)[1].lower()
    if ext_out == '.avi':
        fourcc = cv2.VideoWriter_fourcc(*'XVID')
    else:
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

    video_out = cv2.VideoWriter(output_path, fourcc, fps, (out_w, out_h))

    # 5) Costruisci e scrivi ogni frame
    for fn in frames:
        imgs = []
        for cam in cams:
            img_path = os.path.join(boxes_dir, cam, fn)
            img = cv2.imread(img_path)
            if img is None:
                # placeholder nero
                img = np.zeros((h, w, 3), dtype=np.uint8)
            else:
                # ridimensiona se dimensione diversa
                ih, iw = img.shape[:2]
                if (ih, iw) != (h, w):
                    img = cv2.resize(img, (w, h))
            imgs.append(img)
        frame_grid = create_grid_layout(imgs, rows, cols, h, w)
        video_out.write(frame_grid)

    video_out.release()


def main():
    parser = argparse.ArgumentParser(
        description="Crea un video multiview dinamico da cartelle di immagini"
    )
    parser.add_argument('boxes_dir',
                        help="Cartella radice con sottocartelle camera")
    parser.add_argument('--fps', type=int, default=30,
                        help="Frame rate del video di output")
    parser.add_argument('--output', default='multiview.avi',
                        help="File video di output (preferibilmente .avi per Windows)")
    parser.add_argument('--ext', default='.jpg', choices=['.jpg', '.png'],
                        help="Estensione immagini")
    args = parser.parse_args()

    create_multi_view_video(args.boxes_dir,
                            args.output,
                            args.fps,
                            args.ext)
    print(f"Video salvato in '{args.output}'")

if __name__ == '__main__':
    main()
