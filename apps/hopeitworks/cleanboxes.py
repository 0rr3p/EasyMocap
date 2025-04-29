import os
import shutil

def cleanboxes():
    
    path_data = 'EasyMocap/data/boxes'
    file_boxes = os.path.join(path_data, 'boxes.yml')
    file_extri = os.path.join(path_data, 'extri.yml')
    file_intri = os.path.join(path_data, 'intri.yml')
    
    
    # Elenco dei file e cartelle da mantenere
    files_to_keep = [file_boxes, file_extri, file_intri]
    
    for item in os.listdir(path_data):
        item_path = os.path.join(path_data, item)
        # Se l'elemento non è nella lista di file/cartelle da mantenere, eliminarlo
        if item_path not in files_to_keep:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Rimuove una directory non vuota
            else:
                os.remove(item_path)  # Rimuove un file

if __name__ == "__main__":
    cleanboxes()