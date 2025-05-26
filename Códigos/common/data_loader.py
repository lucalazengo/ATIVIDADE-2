# AT2_Modeling_Experimentation/Codigos/common/data_loader.py
import os
from pathlib import Path
from PIL import Image
import numpy as np
from sklearn.model_selection import train_test_split
from tensorflow.keras.utils import to_categorical 


try:
    BASE_DATA_DIR = Path(__file__).resolve().parent.parent.parent / "Dados"
except NameError:
    BASE_DATA_DIR = Path(".").resolve().parent.parent / "Dados"

ORIGINAL_IMAGES_DIR = BASE_DATA_DIR / "images"
SAMPLE_VISUALS_DIR = BASE_DATA_DIR / "sample_visuals" 

CLASSES = ["em_pe", "sentado", "movimento"] 
NUM_CLASSES = len(CLASSES)

IMG_WIDTH_มาตรฐาน, IMG_HEIGHT_มาตรฐาน = 128, 128 

def get_selected_image_paths_and_labels():
    """
    Obtém os caminhos das 100 imagens originais selecionadas para cada classe
    e seus respectivos rótulos numéricos.
    A seleção é baseada nos nomes dos arquivos presentes em SAMPLE_VISUALS_DIR.
    """
    all_image_paths = []
    all_labels = []

    print(f"Buscando imagens originais em: {ORIGINAL_IMAGES_DIR}")
    print(f"Usando listas de arquivos de: {SAMPLE_VISUALS_DIR}")

    if not ORIGINAL_IMAGES_DIR.is_dir():
        raise FileNotFoundError(
            f"Diretório de imagens originais não encontrado: {ORIGINAL_IMAGES_DIR}. "
            "Verifique a configuração de BASE_DATA_DIR."
        )
    if not SAMPLE_VISUALS_DIR.is_dir():
        raise FileNotFoundError(
            f"Diretório 'sample_visuals' não encontrado: {SAMPLE_VISUALS_DIR}. "
            "Verifique a configuração de BASE_DATA_DIR."
        )

    for label_idx, class_name in enumerate(CLASSES):
        drawn_samples_class_dir = SAMPLE_VISUALS_DIR / class_name
        
        if not drawn_samples_class_dir.is_dir():
            print(f"AVISO: Diretório de amostras desenhadas não encontrado para a classe '{class_name}': {drawn_samples_class_dir}")
            continue

        count = 0
        for drawn_img_file in drawn_samples_class_dir.iterdir():
            if drawn_img_file.is_file():
                original_img_path = ORIGINAL_IMAGES_DIR / drawn_img_file.name
                
                if original_img_path.is_file():
                    all_image_paths.append(str(original_img_path))
                    all_labels.append(label_idx)
                    count += 1
                else:
                    print(f"AVISO: Imagem original '{drawn_img_file.name}' não encontrada em {ORIGINAL_IMAGES_DIR} para a classe '{class_name}'.")
        
        print(f"Encontradas {count} imagens originais para a classe '{class_name}'.")

    if not all_image_paths:
        raise FileNotFoundError(
            f"Nenhuma imagem original foi encontrada. "
            "Verifique se os nomes dos arquivos em '{SAMPLE_VISUALS_DIR}/*/` correspondem aos nomes em '{ORIGINAL_IMAGES_DIR}/'."
        )
        
    return all_image_paths, np.array(all_labels)

def preprocess_image_for_classifier(image_path, target_size=(IMG_WIDTH_มาตรฐาน, IMG_HEIGHT_มาตรฐาน)):
    """
    Carrega uma imagem, redimensiona, converte para RGB e normaliza.
    Usado para modelos que esperam um array NumPy de imagem como entrada (ex: CNN, ou alguns backbones YOLO).
    """
    try:
        img = Image.open(image_path).convert("RGB")
        img = img.resize(target_size)
        img_array = np.array(img) / 255.0  # Normaliza para [0, 1]
        return img_array
    except Exception as e:
        print(f"Erro ao processar imagem {image_path}: {e}")
        return None

def load_data_for_image_array_models(test_size=0.2, random_state=42, target_size=(IMG_WIDTH_มาตรฐาน, IMG_HEIGHT_มาตรฐาน), one_hot_labels=True):
    """
    Carrega e pré-processa todos os dados para modelos que esperam arrays de imagem (como CNNs).
    Retorna (X_train, y_train_final), (X_test, y_test_final).
    y_final pode ser one-hot encoded ou numérico.
    """
    image_paths, labels_numeric = get_selected_image_paths_and_labels()
    
    X_processed = []
    y_processed_numeric = []

    for img_path, label in zip(image_paths, labels_numeric):
        processed_img = preprocess_image_for_classifier(img_path, target_size=target_size)
        if processed_img is not None:
            X_processed.append(processed_img)
            y_processed_numeric.append(label)
    
    if not X_processed:
        raise ValueError("Nenhuma imagem foi processada com sucesso.")

    X_processed = np.array(X_processed)
    y_processed_numeric = np.array(y_processed_numeric)
    
    # Dividir dados
    X_train, X_test, y_train_numeric, y_test_numeric = train_test_split(
        X_processed, y_processed_numeric, 
        test_size=test_size, 
        random_state=random_state, 
        stratify=y_processed_numeric 
    )
    
    if one_hot_labels:
        y_train_final = to_categorical(y_train_numeric, num_classes=NUM_CLASSES)
        y_test_final = to_categorical(y_test_numeric, num_classes=NUM_CLASSES)
    else:
        y_train_final = y_train_numeric
        y_test_final = y_test_numeric
    
    print(f"Dados (arrays de imagem) carregados: {len(X_train)} treino, {len(X_test)} teste.")
    return (X_train, y_train_final), (X_test, y_test_final)

def load_image_paths_and_numeric_labels(test_size=0.2, random_state=42):
    """
    Carrega os caminhos das imagens e rótulos numéricos, dividindo em treino e teste.
    Ideal para MediaPipe (que processa a imagem do caminho) ou YOLO (que pode ser treinado
    a partir de uma estrutura de pastas ou listas de caminhos).
    Retorna (train_paths, train_labels_numeric), (test_paths, test_labels_numeric)
    """
    image_paths, labels_numeric = get_selected_image_paths_and_labels()
    
    train_paths, test_paths, train_labels_numeric, test_labels_numeric = train_test_split(
        image_paths, labels_numeric,
        test_size=test_size,
        random_state=random_state,
        stratify=labels_numeric
    )
    print(f"Caminhos de imagem e rótulos numéricos carregados: {len(train_paths)} treino, {len(test_paths)} teste.")
    return (train_paths, train_labels_numeric), (test_paths, test_labels_numeric)

if __name__ == '__main__':
    print("--- Testando get_selected_image_paths_and_labels ---")
    paths, labels = get_selected_image_paths_and_labels()
    print(f"Total de imagens encontradas: {len(paths)}, Total de rótulos: {len(labels)}")
    if paths:
        print(f"Exemplo de caminho: {paths[0]}, Exemplo de rótulo: {labels[0]}")

    print("\n--- Testando load_data_for_image_array_models (com one-hot) ---")
    (X_train_arr, y_train_arr_oh), (X_test_arr, y_test_arr_oh) = load_data_for_image_array_models(one_hot_labels=True)
    print(f"Shape X_train: {X_train_arr.shape}, Shape y_train (one-hot): {y_train_arr_oh.shape}")
    if len(y_train_arr_oh) > 0:
        print(f"Exemplo de rótulo (one-hot): {y_train_arr_oh[0]}")

    print("\n--- Testando load_data_for_image_array_models (com numérico) ---")
    (X_train_arr_num, y_train_arr_num), (X_test_arr_num, y_test_arr_num) = load_data_for_image_array_models(one_hot_labels=False)
    print(f"Shape X_train: {X_train_arr_num.shape}, Shape y_train (numérico): {y_train_arr_num.shape}")
    if len(y_train_arr_num) > 0:
        print(f"Exemplo de rótulo (numérico): {y_train_arr_num[0]}")

    print("\n--- Testando load_image_paths_and_numeric_labels ---")
    (train_paths_mp, train_labels_mp), (test_paths_mp, test_labels_mp) = load_image_paths_and_numeric_labels()
    if train_paths_mp:
        print(f"Primeiro caminho de treino: {train_paths_mp[0]}, Rótulo: {train_labels_mp[0]}")
    print(f"Número de amostras de treino: {len(train_paths_mp)}")