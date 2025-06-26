import json
import os
import sys

def extract_values_from_json_folder(input_folder, start_file, step, max_files, output_txt):
    try:
        # Apre il file di output in modalità scrittura
        with open(output_txt, 'w') as out_file:
            count = 0
            current_file_num = int(start_file)  # Parte dal file iniziale (es. 1 -> "000001.json")
            
            while count < max_files:
                # Formatta il nome del file (es. "000001.json")
                filename = f"{current_file_num:06d}.json"
                filepath = os.path.join(input_folder, filename)
                
                # Verifica se il file esiste
                if not os.path.exists(filepath):
                    print(f"File {filename} non trovato. Saltato.")
                    current_file_num += step
                    continue
                
                # Legge il file JSON
                with open(filepath, 'r') as f:
                    data = json.load(f)
                
                # Estrae i primi 3 valori dell'8° vettore di handr3d
                ottavo_vettore = data[0]["handr3d"][8]
                primi_tre_valori = ottavo_vettore[:3]
                
                # Scrive i valori nel file CSV (formato: x,y,z)
                out_file.write(",".join(map(str, primi_tre_valori)) + "\n")
                print(f"Processato {filename}: {primi_tre_valori}")
                
                count += 1
                current_file_num += step  # Passa al file successivo (es. step=3: 1, 4, 7...)
        
        print(f"Operazione completata. Salvati {count} valori in {output_txt}")
    
    except Exception as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Utilizzo: python process_json_folder.py <cartella_input> <start_file> <step> <max_files> <output.txt>")
        print("Esempio: python process_json_folder.py ./data 1 3 100 output.csv")
    else:
        input_folder = sys.argv[1]
        start_file = sys.argv[2]  # Es. "1" (per "000001.json")
        step = int(sys.argv[3])   # Incremento tra i file (es. 3)
        max_files = int(sys.argv[4])  # Numero massimo di file da processare
        output_txt = sys.argv[5]
        
        extract_values_from_json_folder(input_folder, start_file, step, max_files, output_txt)