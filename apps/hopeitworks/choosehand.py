import yaml

def choosehand():
    # Chiedi all'utente se è destro o mancino
    handedness = input("Is the operator right-handed (r) or left-handed (l)? ").strip().lower()
    
    # Path al file YAML
    yaml_file_path = 'EasyMocap/config/recon/triangulator-mv1p-total.yml'
    # Nuovo valore per dist_max
    new_dist_max = 0.035
    
    # Carica il file YAML
    with open(yaml_file_path, 'r') as file:
        data = yaml.safe_load(file)
    
    # Modifica il valore in base alla mano scelta
    if 'args' in data and 'config' in data['args']:
        config = data['args']['config']
        if handedness == 'r' and 'handr2d' in config:
            config['handr2d']['dist_max'] = new_dist_max
            config['handl2d']['dist_max'] = 0.015
            print("Updated right hand config.")
        elif handedness == 'l' and 'handl2d' in config:
            config['handl2d']['dist_max'] = new_dist_max
            config['handr2d']['dist_max'] = 0.015
            print("Updated left hand config.")
        else:
            print("Hand config not found or invalid input.")
    
    # Salva il file modificato
    with open(yaml_file_path, 'w') as file:
        yaml.dump(data, file)
        
if __name__ == "__main__":
    choosehand()