import json
import sys

def estrai_primi_tre_valori(input_json, output_txt):
    try:
        # Leggi il file JSON
        with open(input_json, 'r') as f:
            data = json.load(f)
        
        # Estrai l'ottavo vettore (indice 7) da handr3d
        ottavo_vettore = data[0]["handr3d"][8]
        primi_tre_valori = ottavo_vettore[:3]  # Prendi i primi 3 valori
        
        # Scrivi i valori nel file di output in formato CSV
        with open(output_txt, 'w') as f:
            f.write(",".join(map(str, primi_tre_valori)) + "\n")
        
        print(f"Dati salvati in {output_txt}: {primi_tre_valori}")
    
    except Exception as e:
        print(f"Errore: {e}")

if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Utilizzo: python funzione.py file.json output.txt")
    else:
        estrai_primi_tre_valori(sys.argv[1], sys.argv[2])