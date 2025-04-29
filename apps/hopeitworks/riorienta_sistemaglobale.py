import yaml
import numpy as np
import sys
import os
import cv2

def load_extrinsics(yaml_path):
    fs = cv2.FileStorage(yaml_path, cv2.FILE_STORAGE_READ)

    extrinsics = {}
    names_node = fs.getNode('names')
    names = [str(names_node.at(i).string()) for i in range(names_node.size())]
    extrinsics['names'] = names

    for name in names:
        rot_key = f'Rot_{name}'
        t_key = f'T_{name}'

        Rot = fs.getNode(rot_key).mat()
        T = fs.getNode(t_key).mat()

        extrinsics[name] = {'Rot': Rot, 'T': T}

    fs.release()
    return extrinsics


def load_points(points_txt_path):
    points = {}
    with open(points_txt_path, 'r') as f:
        lines = f.readlines()
        for line in lines:
            if ':' in line:
                key, value = line.split(':')
                coords = np.array(list(map(float, value.strip().split(','))))
                points[key.strip()] = coords
    return points['O'], points['X'], points['Y']

def build_new_basis(O, X, Y):
    x_axis = X - O
    x_axis = x_axis / np.linalg.norm(x_axis)

    temp_y = Y - O
    temp_y = temp_y / np.linalg.norm(temp_y)

    z_axis = np.cross(x_axis, temp_y)
    z_axis = z_axis / np.linalg.norm(z_axis)

    y_axis = np.cross(z_axis, x_axis)
    y_axis = y_axis / np.linalg.norm(y_axis)

    R_new = np.stack([x_axis, y_axis, z_axis], axis=1)
    return R_new, O

def transform_camera(R_cam_old, T_cam_old, R_new_basis, T_new_origin):
    R_cam_new = R_new_basis.T @ R_cam_old
    T_cam_new = R_new_basis.T @ (T_cam_old.flatten() - T_new_origin)
    return R_cam_new, T_cam_new.reshape(3, 1)

def save_extrinsics(extrinsics, output_path):
    fs = cv2.FileStorage(output_path, cv2.FILE_STORAGE_WRITE)

    # Scrivi la lista dei nomi
    fs.startWriteStruct('names', cv2.FILE_NODE_SEQ)
    for name in extrinsics['names']:
        fs.write('', name)
    fs.endWriteStruct()

    for name in extrinsics['names']:
        Rot = extrinsics[name]['Rot']
        T = extrinsics[name]['T']

        # Calcola vettore R (Rodrigues inverso della matrice di rotazione)
        R_vec, _ = cv2.Rodrigues(Rot)

        # Scrivi R_CAM come matrice OpenCV
        fs.write(f'R_{name}', R_vec)

        # Scrivi Rot_CAM come matrice OpenCV
        fs.write(f'Rot_{name}', Rot)

        # Scrivi T_CAM come matrice OpenCV
        fs.write(f'T_{name}', T)

    fs.release()


def main():
    if len(sys.argv) != 3:
        print("Usage: python reorient.py path_to_extri.yml path_to_points.txt")
        sys.exit(1)

    yaml_path = sys.argv[1]
    points_path = sys.argv[2]

    extrinsics = load_extrinsics(yaml_path)
    O, X, Y = load_points(points_path)

    R_new_basis, T_new_origin = build_new_basis(O, X, Y)

    new_extrinsics = {'names': extrinsics['names']}

    for name in extrinsics['names']:
        R_old = extrinsics[name]['Rot']
        T_old = extrinsics[name]['T']

        R_new, T_new = transform_camera(R_old, T_old, R_new_basis, T_new_origin)

        new_extrinsics[name] = {
            'Rot': R_new,
            'T': T_new
        }

    output_path = os.path.splitext(yaml_path)[0] + '_reoriented.yml'
    save_extrinsics(new_extrinsics, output_path)

    print(f"Nuovo file salvato in {output_path}")

if __name__ == "__main__":
    main()
