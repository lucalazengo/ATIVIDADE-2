# AT2_Modeling_Experimentation/Codigos/model_A_mediapipe_classifier/mediapipe_utils.py
import cv2
import mediapipe as mp
import numpy as np
from pathlib import Path

mp_pose = mp.solutions.pose
pose_detector = mp_pose.Pose(static_image_mode=True,
                             model_complexity=1, 
                             min_detection_confidence=0.5)

NUM_POSE_LANDMARKS = 33
NUM_COORDS_PER_LANDMARK = 4 # x, y, z, visibility

def extract_pose_landmarks_from_image(image_path_str):
    """
    Extrai landmarks de pose de uma única imagem usando MediaPipe Pose.

    Args:
        image_path_str (str): Caminho para o arquivo de imagem.

    Returns:
        np.array: Array NumPy com os landmarks (NUM_POSE_LANDMARKS * NUM_COORDS_PER_LANDMARK)
                  ou None se nenhuma pose for detectada ou ocorrer um erro.
    """
    image_path = Path(image_path_str)
    if not image_path.is_file():
        print(f"Erro: Imagem não encontrada em {image_path_str}")
        return None

    try:
        image = cv2.imread(str(image_path))
        if image is None:
            print(f"Erro: Não foi possível ler a imagem {image_path_str} com OpenCV.")
            return None

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        results = pose_detector.process(image_rgb)

        if results.pose_landmarks:
            landmarks_data = []
            for landmark in results.pose_landmarks.landmark:
                landmarks_data.extend([landmark.x, landmark.y, landmark.z, landmark.visibility])
            
            if len(landmarks_data) == NUM_POSE_LANDMARKS * NUM_COORDS_PER_LANDMARK:
                return np.array(landmarks_data)
            else:
                print(f"Erro: Número inesperado de dados de landmarks em {image_path_str}")
                return None
        else:
            return None
    except Exception as e:
        print(f"Exceção ao processar a imagem {image_path_str} com MediaPipe: {e}")
        return None

def batch_extract_features(image_paths):
    """
    Extrai features (landmarks de pose) para uma lista de caminhos de imagem.

    Args:
        image_paths (list): Lista de strings contendo os caminhos das imagens.

    Returns:
        tuple: (list_of_features, list_of_valid_indices)
               list_of_features: Lista de arrays NumPy, cada um representando os landmarks de uma imagem.
               list_of_valid_indices: Lista de índices das imagens para as quais os features foram extraídos com sucesso.
    """
    all_features = []
    valid_indices = []
    
    total_images = len(image_paths)
    print(f"Iniciando extração de features para {total_images} imagens...")

    for i, img_path in enumerate(image_paths):
        if (i + 1) % 50 == 0: # Log de progresso
            print(f"Processando imagem {i+1}/{total_images}...")
            
        features = extract_pose_landmarks_from_image(img_path)
        if features is not None:
            all_features.append(features)
            valid_indices.append(i)

    print(f"Extração de features concluída. {len(all_features)}/{total_images} imagens processadas com sucesso.")
    return all_features, valid_indices


if __name__ == '__main__':
    import sys
    sys.path.append(str(Path(__file__).resolve().parent.parent))
    from common.data_loader import load_image_paths_for_mediapipe

    print("Testando extração de features do MediaPipe...")
    (train_paths, train_labels), (test_paths, test_labels) = load_image_paths_for_mediapipe(test_size=0.1) 
    if train_paths:
        print(f"\nExtraindo features para algumas imagens de treino (máximo 5):")
        sample_train_paths = train_paths[:5]
        
        features_list, valid_idx_list = batch_extract_features(sample_train_paths)
        
        for i, features in enumerate(features_list):
            original_idx = valid_idx_list[i]
            print(f"  Imagem: {Path(sample_train_paths[original_idx]).name}, Features Shape: {features.shape}, Rótulo: {train_labels[original_idx]}")
        
        if features_list:
            print(f"\nDimensão de um vetor de features: {features_list[0].shape[0]}") # Deve ser 33*4 = 132
    else:
        print("Nenhum caminho de treino carregado para testar a extração de features.")