##METTIMI IN CONTENT-> EASYMOCAP-> APPS->CALIBRATION!!!

import json
import os
from glob import glob

def read_json(path):
    with open(path, 'r') as f:
        return json.load(f)

def save_json(path, data):
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def rotate_corners_180(camera_name):
    """
    Ruota i corner 2D di 180° per tutti i file JSON di una telecamera.
    
    :param camera_name: Es. "X1Y0Z-1"
    """
    base_path = 'EasyMocap/extri_data/chessboard'
    camera_path = os.path.join(base_path, camera_name)

    json_files = sorted(glob(os.path.join(camera_path, '*.json')))
    if not json_files:
        print(f" Nessun file JSON trovato in {camera_path}")
        return

    print(f" Ruotando 180° i corner per: {camera_name}")

    count = 0
    for jf in json_files:
        data = read_json(jf)
        kps = data.get('keypoints2d', [])
        if not kps or kps[0][-1] < 0.5:
            continue
        data['keypoints2d'] = kps[::-1]  # Rotazione 180°
        save_json(jf, data)
        count += 1

    print(f" Completato: {count}/{len(json_files)} file aggiornati per {camera_name}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('camera_name', type=str, help='Nome della telecamera (es: X1Y0Z-1)')
    args = parser.parse_args()
    rotate_corners_180(args.camera_name)
