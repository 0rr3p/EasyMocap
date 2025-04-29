import os
import sys

def sostituisciextri(directory):
    # Definisci i percorsi completi dei file da eliminare
    files_to_delete = [
        os.path.join(directory, 'extri.yml'),
        os.path.join(directory, 'extri_inv.yml'),
        os.path.join(directory, 'extri_inv_reoriented.yml')
    ]
    
    # Elimina i file specificati
    for file_path in files_to_delete:
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"File eliminato: {file_path}")
        else:
            print(f"File non trovato: {file_path}")
    
    # Rinomina il file extri_inv_reoriented_inv in extri
    extri_inv_reoriented_inv_path = os.path.join(directory, 'extri_inv_reoriented_inv.yml')
    new_name_path = os.path.join(directory, 'extri.yml')
    
    if os.path.exists(extri_inv_reoriented_inv_path):
        os.rename(extri_inv_reoriented_inv_path, new_name_path)
        print(f"File rinominato: {extri_inv_reoriented_inv_path} -> {new_name_path}")
    else:
        print(f"File 'extri_inv_reoriented_inv' non trovato!")

if __name__ == "__main__":
    # Prende il percorso della directory come argomento da linea di comando
    if len(sys.argv) != 2:
        print("Errore: specificare il percorso della directory come argomento.")
        sys.exit(1)

    directory = sys.argv[1]
    
    # Invoca la funzione con il percorso della directory
    sostituisciextri(directory)
