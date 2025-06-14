# VISUALIZZAZIONE IN UN AMBIENTE 3D DEI SISTEMI DI RIFERIMENTO DELLE TELECAMERE RISPETTO A IL SISTEMA DI RIFERIMENTO GLOBALE
import cv2
import numpy as np
import plotly.graph_objects as go
from itertools import combinations
import argparse


def visualize_reference_frames_interactive(yaml_path: str) -> go.Figure:
    """
    Carica da `yaml_path` le rototraslazioni in stile OpenCV
    (nodi names, Rot_<name>, T_<name>) e mostra un grafico 3D interattivo.

    Restituisce l’oggetto plotly.graph_objects.Figure.
    """
    # 1) Lettura del file YAML
    fs = cv2.FileStorage(yaml_path, cv2.FILE_STORAGE_READ)
    if not fs.isOpened():
        raise FileNotFoundError(f"Impossibile aprire il file: {yaml_path}")
    names_node = fs.getNode('names')
    names = [names_node.at(i).string() for i in range(names_node.size())]

    # 2) Estrazione di Rot e T
    frames = {}
    for name in names:
        R = fs.getNode(f'Rot_{name}').mat()
        T = fs.getNode(f'T_{name}').mat().flatten()
        frames[name] = (R, T)
    fs.release()

    # 3) Calcolo delle scale per gli assi
    max_dist = max(np.linalg.norm(T) for _, T in frames.values())
    axis_len = max_dist * 1.2
    local_len = axis_len * 0.2

    # 4) Preparazione dati per Plotly
    data = []
    # 4a) Assi globali
    axes = {
        'Xg': ([0, axis_len], [0, 0], [0, 0]),
        'Yg': ([0, 0], [0, axis_len], [0, 0]),
        'Zg': ([0, 0], [0, 0], [0, axis_len])
    }
    for label, (xs, ys, zs) in axes.items():
        data.append(go.Scatter3d(
            x=xs, y=ys, z=zs,
            mode='lines+text',
            line=dict(color='black', width=8),
            text=[None, label],
            textposition='top center',
            name=label
        ))

    # 4b) Assi locali e origini
    for name, (R, T) in frames.items():
        # assi locali (rosso, verde, blu)
        for vec, col, axis_name in zip((R[:,0], R[:,1], R[:,2]),
                                      ('red', 'green', 'blue'),
                                      ('X', 'Y', 'Z')):
            data.append(go.Scatter3d(
                x=[T[0], T[0] + vec[0] * local_len],
                y=[T[1], T[1] + vec[1] * local_len],
                z=[T[2], T[2] + vec[2] * local_len],
                mode='lines',
                line=dict(color=col, width=4),
                name=f"{name}_{axis_name}"
            ))
        # etichetta dell'origine
        data.append(go.Scatter3d(
            x=[T[0]], y=[T[1]], z=[T[2]],
            mode='text', text=[name],
            textposition='bottom right', showlegend=False
        ))

    # 4c) Calcolo e stampa distanze tra origini
    print("Distanze tra origini dei frame:")
    for (n1, (_, T1)), (n2, (_, T2)) in combinations(frames.items(), 2):
        d = np.linalg.norm(T1 - T2)
        # usa <-> al posto di caratteri unicode
        print(f"  {n1} <-> {n2}: {d:.4f}")
        mid = (T1 + T2) / 2
        data.append(go.Scatter3d(
            x=[mid[0]], y=[mid[1]], z=[mid[2]],
            mode='text', text=[f"{d:.2f}"],
            textfont=dict(size=10, color='black'), showlegend=False
        ))

    # 5) Costruzione e visualizzazione della figura
    fig = go.Figure(data=data)
    fig.update_layout(
        scene=dict(
            xaxis=dict(title='X', range=[-axis_len, axis_len]),
            yaxis=dict(title='Y', range=[-axis_len, axis_len]),
            zaxis=dict(title='Z', range=[-axis_len, axis_len]),
            aspectmode='cube'
        ),
        title='Sistemi di riferimento interattivi'
    )
    fig.show(renderer="browser")  
    return fig


def main():
    parser = argparse.ArgumentParser(
        description='Visualizza in 3D interattivo i sistemi di riferimento da un file YAML')
    parser.add_argument('input', help='Percorso al file YAML (Rot_*, T_*)')
    args = parser.parse_args()

    visualize_reference_frames_interactive(args.input)

if __name__ == '__main__':
    main()