import os

def create_directories():
    dirs = [
        'EasyMocap/extri_data/videos',
        'EasyMocap/extri_data/images',
        'EasyMocap/extri_data/output/calibration',
        'EasyMocap/intri_data/videos',
        'EasyMocap/intri_data/images',
        'EasyMocap/intri_data/output/calibration',
    ]
    for d in dirs:
        os.makedirs(d, exist_ok=True)

if __name__ == "__main__":
    create_directories()