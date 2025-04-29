import os

def cleanextri():
    ##CANCELLA DATI INTRI
    import os, shutil; [(shutil.rmtree if os.path.isdir(p) else os.remove)(p) 
      for p in ('EasyMocap/extri_data/'+n 
                for n in os.listdir('EasyMocap/extri_data') if n!='videos')]

if __name__ == "__main__":
    cleanextri()
