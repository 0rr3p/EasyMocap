import os
import sys

def update_new_tuning_file(directory):
    # Percorso completo del file new tuning
    file_path = os.path.join(directory, 'newtuning.txt')
    
    # Contenuto che vogliamo scrivere nel file
    new_content ="""O: 0.0, 0.0, 0.0
X: 0.5, 0.0, 0.0 
Y: 0.0, 0.5, 0.0"""
    
    # Verifica se il file esiste
    if os.path.exists(file_path):
        # Apre il file in modalità scrittura (sovrascrive il contenuto)
        with open(file_path, 'w') as file:
            file.write(new_content)
        print(f"Il file '{file_path}' è stato aggiornato con il nuovo contenuto.")
    else:
        print(f"Il file '{file_path}' non esiste nella directory '{directory}'.")

# Se lo script è eseguito da linea di comando
if __name__ == "__main__":
    # Controlla se è stato passato un argomento
    if len(sys.argv) != 2:
        print("Uso: python ripristinatuning.py path/")
        sys.exit(1)
    
    # Prende il percorso della directory come argomento
    directory = sys.argv[1]
    
    # Chiama la funzione con il percorso della directory
    update_new_tuning_file(directory)
