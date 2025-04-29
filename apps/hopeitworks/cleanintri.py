import os

def cleanintri():
    ##CANCELLA DATI INTRI
    import os, shutil; [(shutil.rmtree if os.path.isdir(p) else os.remove)(p) 
      for p in ('EasyMocap/intri_data/'+n 
                for n in os.listdir('EasyMocap/intri_data') if n!='videos')]

if __name__ == "__main__":
    cleanintri()
