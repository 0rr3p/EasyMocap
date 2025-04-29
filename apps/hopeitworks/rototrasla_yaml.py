#QUESTA FUNZIONE PASSA DA UNO YAML IN CUI R e T sono riferiti a CAMERA->GLOBALE A UNO YAML IN CUI GLOBALE->CAMERA
import cv2
import numpy as np
import argparse
import os

def invert_roto_trans(input_yaml, output_yaml):
    # Lettura del file YAML
    fs = cv2.FileStorage(input_yaml, cv2.FILE_STORAGE_READ)
    # Estrazione dei nomi dei sistemi di riferimento
    names_node = fs.getNode('names')
    names = [names_node.at(i).string() for i in range(names_node.size())]

    invs = {}
    for name in names:
        # Caricamento dei dati originali
        rvec = fs.getNode(f'R_{name}').mat()
        rot  = fs.getNode(f'Rot_{name}').mat()
        tvec = fs.getNode(f'T_{name}').mat()

        # Calcolo dell'inversa della rotazione e della traslazione
        rot_inv = rot.T
        t_inv   = -rot_inv @ tvec
        # Conversione in vettore di Rodrigues
        rvec_inv, _ = cv2.Rodrigues(rot_inv)

        invs[name] = (rvec_inv, rot_inv, t_inv)
    fs.release()

    # Scrittura del nuovo file YAML con le trasformazioni inverse
    fsw = cv2.FileStorage(output_yaml, cv2.FILE_STORAGE_WRITE)
    # Ricreo la lista dei nomi
    fsw.startWriteStruct('names', cv2.FILE_NODE_SEQ)
    for name in names:
        fsw.write('', name)
    fsw.endWriteStruct()

    # Scrivo vettori e matrici inverse
    for name, (rvi, ri, ti) in invs.items():
        fsw.write(f'R_{name}',   rvi)
        fsw.write(f'Rot_{name}', ri)
        fsw.write(f'T_{name}',   ti)
    fsw.release()


def main():
    parser = argparse.ArgumentParser(
        description='Invert roto-translations in a YAML file')
    parser.add_argument('input', help='Input YAML file path')
    parser.add_argument('output', nargs='?', help='Output YAML file path (optional)')
    args = parser.parse_args()

    input_path = args.input
    # Se non specificato, aggiungo '_inv' al nome del file
    if args.output:
        output_path = args.output
    else:
        base, ext = os.path.splitext(input_path)
        output_path = f"{base}_inv{ext}"

    invert_roto_trans(input_path, output_path)
    print(f"Inversed YAML saved to {output_path}")

if __name__ == '__main__':
    main()
