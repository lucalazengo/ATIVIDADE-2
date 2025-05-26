# AT2_Modeling_Experimentation/Codigos/common/prepare_yolo_dataset.py
import os
import shutil
from pathlib import Path
import sys

sys.path.append(str(Path(__file__).resolve().parent.parent))

from common.data_loader import load_image_paths_and_numeric_labels, CLASSES

BASE_OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent
YOLO_DATASET_DIR = BASE_OUTPUT_DIR / "yolo_classification_dataset"

TEST_SIZE_FOR_YOLO_VAL = 0.25 
RANDOM_STATE = 42

def create_yolo_dataset_structure(delete_existing=True):
    """
    Cria a estrutura de pastas para o dataset YOLO (train/val) e copia as imagens.
    """
    if YOLO_DATASET_DIR.exists() and delete_existing:
        print(f"Removendo diretório de dataset YOLO existente: {YOLO_DATASET_DIR}")
        shutil.rmtree(YOLO_DATASET_DIR)
    
    YOLO_DATASET_DIR.mkdir(parents=True, exist_ok=True)
    
    # Carregar os caminhos e rótulos já divididos
    print(f"Carregando caminhos de imagem usando data_loader (test_size={TEST_SIZE_FOR_YOLO_VAL})...")
    (train_image_paths, train_labels), (val_image_paths, val_labels) = \
        load_image_paths_and_numeric_labels(test_size=TEST_SIZE_FOR_YOLO_VAL, random_state=RANDOM_STATE)

    train_dir = YOLO_DATASET_DIR / "train"
    val_dir = YOLO_DATASET_DIR / "val" 

    datasets_to_process = {
        "train": (train_dir, train_image_paths, train_labels),
        "val": (val_dir, val_image_paths, val_labels)
    }

    for split_name, (split_dir, image_paths, labels) in datasets_to_process.items():
        print(f"\nProcessando split: {split_name} (Total de imagens: {len(image_paths)})")
        split_dir.mkdir(parents=True, exist_ok=True)
        
        for class_name in CLASSES:
            (split_dir / class_name).mkdir(parents=True, exist_ok=True)
            
        copied_count = 0
        for i, img_path_str in enumerate(image_paths):
            img_path = Path(img_path_str)
            label_numeric = labels[i]
            class_name = CLASSES[label_numeric] 
            
            destination_path = split_dir / class_name / img_path.name
            
            try:
                shutil.copy(img_path, destination_path)
                copied_count += 1
            except Exception as e:
                print(f"Erro ao copiar {img_path} para {destination_path}: {e}")
        print(f"Copiadas {copied_count} imagens para {split_dir}")

    print(f"\nEstrutura do dataset YOLO criada em: {YOLO_DATASET_DIR}")
    print("Verifique a estrutura e o número de arquivos em cada pasta.")

if __name__ == "__main__":
    create_yolo_dataset_structure()