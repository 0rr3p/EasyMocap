##ELIMINA DATA tranne video e yaml e new cordinate e smplx
import os
import shutil

def cleanhandmocap():
    
    path_data = 'EasyMocap/data'
    file_extri = os.path.join(path_data, 'extri.yml')
    file_intri = os.path.join(path_data, 'intri.yml')
    file_newcordinate = os.path.join(path_data, 'newcordinate.txt')
    path_smplx = os.path.join(path_data, 'smplx')
    path_newtuning = os.path.join(path_data, 'newtuning.txt')
    path_boxes = os.path.join(path_data, 'boxes')
    
    # Elenco dei file e cartelle da mantenere
    files_to_keep = [file_extri, file_intri, file_newcordinate, path_smplx, path_newtuning, path_boxes]
    
    # Elimina tutto in 'data' tranne 'videos', 'extri.yml', e 'intri.yml'
    for item in os.listdir(path_data):
        item_path = os.path.join(path_data, item)
        # Se l'elemento non è nella lista di file/cartelle da mantenere, eliminarlo
        if item_path not in files_to_keep:
            if os.path.isdir(item_path):
                shutil.rmtree(item_path)  # Rimuove una directory non vuota
            else:
                os.remove(item_path)  # Rimuove un file
    
    os.makedirs('EasyMocap/data/videos', exist_ok=True)
if __name__ == "__main__":
    cleanhandmocap()
