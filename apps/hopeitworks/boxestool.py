#!/usr/bin/env python3
import sys
import argparse
import yaml


def load_boxes(path):
    """Carica la lista di box da file YAML"""
    with open(path, 'r') as f:
        data = yaml.safe_load(f)
    boxes = data.get('boxes')
    if not isinstance(boxes, list):
        print(f"Errore: '{path}' non contiene la chiave 'boxes' valida.")
        sys.exit(1)
    return boxes


def save_boxes(path, boxes):
    """Salva la lista di box su file YAML"""
    with open(path, 'w') as f:
        yaml.safe_dump({'boxes': boxes}, f, default_flow_style=False)


def prompt_or_quit(prompt):
    """Mostra prompt, permette di digitare 'q' per uscire"""
    s = input(prompt).strip()
    if s.lower() in ('q', 'quit', 'exit'):
        print("Uscita dal tool...")
        sys.exit(0)
    return s


def select_indices(n):
    """Chiede all'utente di selezionare indici da 1 a n, oppure 'q' per uscire"""
    while True:
        s = prompt_or_quit(f"Inserisci i numeri dei componenti che vuoi modificare da 1 a {n}, separati da virgola (o 'q' per uscire): ")
        try:
            parts = [int(x.strip()) for x in s.split(',')]
            idxs = [i-1 for i in parts]
            if any(i < 0 or i >= n for i in idxs):
                raise ValueError
            return idxs
        except ValueError:
            print("Input non valido, riprova.")


def select_action():
    """Chiede se allungare (1) o spostare (2), oppure 'q' per uscire"""
    while True:
        s = prompt_or_quit("Vuoi (1) allungare o (2) spostare i componenti? Inserisci 1 o 2 (o 'q' per uscire): ")
        if s == '1': return 'stretch'
        if s == '2': return 'translate'
        print("Scelta non valida, inserisci 1 o 2.")


def select_direction():
    """Chiede la direzione: -x +x -y +y -z +z, oppure 'q' per uscire"""
    valid = ['-x', '+x', '-y', '+y', '-z', '+z']
    while True:
        s = prompt_or_quit("Direzione (-x, +x, -y, +y, -z, +z) (o 'q' per uscire): ")
        if s in valid:
            return s
        print("Direzione non valida, riprova.")


def input_magnitude():
    """Chiede l'entità in cm e converte in metri, oppure 'q' per uscire"""
    while True:
        s = prompt_or_quit("Entità in cm (es. 10) (o 'q' per uscire): ")
        try:
            cm = float(s)
            return cm / 100.0
        except ValueError:
            print("Valore non valido, inserisci un numero.")


def main():
    parser = argparse.ArgumentParser(
        description="Tool per modificare i bounding-box in un file YAML"
    )
    parser.add_argument('boxes_yml',
                        help='Percorso al file boxes.yml da modificare')
    args = parser.parse_args()

    boxes = load_boxes(args.boxes_yml)

    # Stampa lista componenti
    print("Componenti disponibili:")
    for idx, box in enumerate(boxes, start=1):
        print(f"{idx}: {box.get('id', '')}")

    # Selezione
    idxs = select_indices(len(boxes))
    action = select_action()
    direction = select_direction()
    magnitude = input_magnitude()

    # Applica modifiche
    for i in idxs:
        box = boxes[i]
        mn = box['min']
        mx = box['max']
        axis = direction[1]  # 'x', 'y' o 'z'
        sign = 1 if direction[0] == '+' else -1
        if action == 'stretch':
            # allunga modificando solo min o max
            if axis == 'x':
                if sign > 0: mx[0] += magnitude
                else: mn[0] -= magnitude
            elif axis == 'y':
                if sign > 0: mx[1] += magnitude
                else: mn[1] -= magnitude
            elif axis == 'z':
                if sign > 0: mx[2] += magnitude
                else: mn[2] -= magnitude
        else:
            # translate: sposta min e max
            if axis == 'x':
                mn[0] += sign * magnitude
                mx[0] += sign * magnitude
            elif axis == 'y':
                mn[1] += sign * magnitude
                mx[1] += sign * magnitude
            elif axis == 'z':
                mn[2] += sign * magnitude
                mx[2] += sign * magnitude

    # Salva
    save_boxes(args.boxes_yml, boxes)
    print(f"File '{args.boxes_yml}' aggiornato con successo.")

if __name__ == '__main__':
    main()
