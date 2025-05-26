# AT2_Modeling_Experimentation/Codigos/model_A_mediapipe_classifier/train_mp_classifier.py
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, accuracy_score, confusion_matrix
import joblib 
from pathlib import Path
import json

import sys
sys.path.append(str(Path(__file__).resolve().parent.parent))

from common.data_loader import load_image_paths_and_numeric_labels, CLASSES 
from model_A_mediapipe_classifier.mediapipe_utils import batch_extract_features

# --- Configurações ---
BASE_OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent
SAVED_MODEL_DIR = BASE_OUTPUT_DIR / "saved_models"
OUTPUTS_DIR = BASE_OUTPUT_DIR / "outputs"

MODEL_FILENAME = SAVED_MODEL_DIR / "model_A_mp_classifier.pkl"
SCALER_FILENAME = SAVED_MODEL_DIR / "scaler_model_A.pkl"
LABEL_ENCODER_FILENAME = SAVED_MODEL_DIR / "label_encoder_model_A.pkl"
METRICS_FILENAME = OUTPUTS_DIR / "model_A_mp_metrics.json"

TEST_SIZE = 0.25 
RANDOM_STATE = 42

def train_and_evaluate_mp_classifier():
    """
    Pipeline completo: carrega dados, extrai features, treina classificador e avalia.
    """
    SAVED_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    # 1. Carregar caminhos de imagem e rótulos (já divididos em treino e teste)
    print("Carregando caminhos de imagem e rótulos para treino e teste...")
    (train_paths, y_train_numeric), (test_paths, y_test_numeric) = load_image_paths_and_numeric_labels(
        test_size=TEST_SIZE, random_state=RANDOM_STATE
    )

    # 2. Extrair features do MediaPipe para o conjunto de TREINO
    print("\nExtraindo features do MediaPipe para o conjunto de TREINO...")
    list_of_train_feature_arrays, train_valid_indices = batch_extract_features(train_paths)

    if not list_of_train_feature_arrays:
        print("Nenhuma feature foi extraída para o conjunto de treino. Não é possível continuar.")
        return
    
    X_train_features = np.array(list_of_train_feature_arrays)
    # Filtrar os rótulos de treino para corresponder apenas às imagens com features extraídas
    y_train = y_train_numeric[train_valid_indices] 

    # 3. Extrair features do MediaPipe para o conjunto de TESTE
    print("\nExtraindo features do MediaPipe para o conjunto de TESTE...")
    list_of_test_feature_arrays, test_valid_indices = batch_extract_features(test_paths)

    if not list_of_test_feature_arrays:
        print("Nenhuma feature foi extraída para o conjunto de teste. A avaliação pode não ser possível ou completa.")
        X_test_features = np.array([]) 
        y_test = np.array([])        
    else:
        X_test_features = np.array(list_of_test_feature_arrays)
        # Filtrar os rótulos de teste
        y_test = y_test_numeric[test_valid_indices]

    print(f"\nShape do array de features X_train: {X_train_features.shape}")
    print(f"Shape do array de rótulos y_train: {y_train.shape}")
    
    if X_test_features.size > 0:
        print(f"Shape do array de features X_test: {X_test_features.shape}")
        print(f"Shape do array de rótulos y_test: {y_test.shape}")
    else:
        print("Nenhuma feature válida extraída para o conjunto de teste. A avaliação será pulada.")


    # 4. Normalizar as features (APENAS se tivermos dados de treino)
    if X_train_features.size == 0:
        print("Não há dados de treino para normalizar ou treinar o modelo.")
        return
        
    print("\nNormalizando features...")
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train_features)
    joblib.dump(scaler, SCALER_FILENAME)
    print(f"Scaler salvo em: {SCALER_FILENAME}")

    if X_test_features.size > 0:
        X_test_scaled = scaler.transform(X_test_features)
    else:
        X_test_scaled = np.array([]) 


    le = LabelEncoder()
    le.fit(CLASSES)
    joblib.dump(le, LABEL_ENCODER_FILENAME)
    print(f"LabelEncoder (com classes: {le.classes_}) salvo em: {LABEL_ENCODER_FILENAME}")

    # 5. Treinar o classificador
    print("\nTreinando o classificador RandomForest...")
    classifier = RandomForestClassifier(n_estimators=200, random_state=RANDOM_STATE, class_weight='balanced')
    
    classifier.fit(X_train_scaled, y_train) 
    joblib.dump(classifier, MODEL_FILENAME)
    print(f"Modelo classificador salvo em: {MODEL_FILENAME}")

    if X_test_scaled.size > 0 and y_test.size > 0 :
        print("\nAvaliando o modelo no conjunto de teste...")
        y_pred = classifier.predict(X_test_scaled)
        
        accuracy = accuracy_score(y_test, y_pred)
        report_dict = classification_report(y_test, y_pred, target_names=le.classes_, output_dict=True, zero_division=0)
        report_str = classification_report(y_test, y_pred, target_names=le.classes_, zero_division=0)


        print(f"\nAcurácia no teste: {accuracy:.4f}")
        print("\nRelatório de Classificação:")
        print(report_str) 

        print("\nMatriz de Confusão:")
        conf_matrix = confusion_matrix(y_test, y_pred, labels=np.arange(len(le.classes_)))
        print(conf_matrix)
        
        # Salvar métricas
        metrics_data = {
            "model_name": "MediaPipe_Pose_Features + RandomForestClassifier",
            "accuracy": accuracy,
            "classification_report": report_dict,
            "confusion_matrix": conf_matrix.tolist(),
            "classes_order": list(le.classes_) # Garante que é uma lista serializável
        }
    else:
        print("\nAVALIAÇÃO PULADA: Não há dados de teste válidos com features extraídas.")
        metrics_data = {
            "model_name": "MediaPipe_Pose_Features + RandomForestClassifier",
            "notes": "Avaliação pulada devido à ausência de features de teste válidas."
        }

    with open(METRICS_FILENAME, 'w') as f:
        json.dump(metrics_data, f, indent=4)
    print(f"\nMétricas salvas em: {METRICS_FILENAME}")

if __name__ == '__main__':
    train_and_evaluate_mp_classifier()