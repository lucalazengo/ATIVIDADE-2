# AT2_Modeling_Experimentation/Codigos/model_B_yolo_classifier/train_yolo_classifier.py
from ultralytics import YOLO
from pathlib import Path
import shutil
import json
import os

# --- Configurações ---
BASE_PROJECT_DIR = Path(__file__).resolve().parent.parent.parent
YOLO_DATASET_DIR = BASE_PROJECT_DIR / "yolo_classification_dataset" # Criado pelo script prepare_yolo_dataset.py
SAVED_MODEL_DIR = BASE_PROJECT_DIR / "saved_models"
OUTPUTS_DIR = BASE_PROJECT_DIR / "outputs" # Para métricas e logs do YOLO

YOLO_MODEL_NAME = 'yolov8n-cls.pt' 
TRAINED_YOLO_MODEL_FILENAME = SAVED_MODEL_DIR / "model_B_yolo_classifier.pt" 
METRICS_FILENAME = OUTPUTS_DIR / "model_B_yolo_metrics.json"

# Parâmetros de Treinamento YOLO
EPOCHS = 20
IMG_SIZE_YOLO = 128 
BATCH_SIZE = 16 

def train_yolo_classifier():
    """
    Treina um modelo YOLO para classificação de posturas.
    """
    SAVED_MODEL_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUTS_DIR.mkdir(parents=True, exist_ok=True)

    if not YOLO_DATASET_DIR.is_dir() or \
       not (YOLO_DATASET_DIR / "train").is_dir() or \
       not (YOLO_DATASET_DIR / "val").is_dir():
        print(f"ERRO: Diretório do dataset YOLO não encontrado ou incompleto em {YOLO_DATASET_DIR}")
        print("Por favor, execute o script 'prepare_yolo_dataset.py' primeiro.")
        return

    # 1. Carregar o modelo YOLO pré-treinado para classificação
    print(f"Carregando modelo YOLO pré-treinado: {YOLO_MODEL_NAME}")
    try:
        model = YOLO(YOLO_MODEL_NAME)
    except Exception as e:
        print(f"Erro ao carregar o modelo YOLO: {e}")
        print("Verifique se o nome do modelo está correto e se você tem conexão com a internet para o download inicial,")
        print(f"ou se o arquivo '{YOLO_MODEL_NAME}' existe localmente.")
        return

    # 2. Treinar o modelo
    print(f"\nIniciando treinamento do YOLO por {EPOCHS} épocas...")
    # A biblioteca Ultralytics salva os resultados em uma pasta 'runs/classify/trainX'
    try:
        results = model.train(
            data=str(YOLO_DATASET_DIR), 
            epochs=EPOCHS,
            imgsz=IMG_SIZE_YOLO,
            batch=BATCH_SIZE,
            patience=10, # Parar cedo se não houver melhora após N épocas (early stopping)
            project=str(OUTPUTS_DIR / "yolo_runs"), 
            name="classify_train", 
            exist_ok=True 
        )
    except Exception as e:
        print(f"Erro durante o treinamento do YOLO: {e}")
        return

    print("\nTreinamento YOLO concluído.")
    

    
    if hasattr(results, 'save_dir'):
        run_dir = Path(results.save_dir)
    else: 
        project_runs_dir = OUTPUTS_DIR / "yolo_runs" / "classify_train"
        if not project_runs_dir.exists(): # Se o nome padrão não foi criado, tenta encontrar o último
            possible_runs = sorted([d for d in (OUTPUTS_DIR / "yolo_runs").iterdir() if d.is_dir() and d.name.startswith("classify_train")], reverse=True)
            if possible_runs:
                run_dir = possible_runs[0]
            else:
                print("ERRO: Não foi possível determinar o diretório da execução do YOLO.")
                return
        else:
            run_dir = project_runs_dir
            
    path_to_best_weights = run_dir / "weights" / "best.pt"

    if path_to_best_weights.exists():
        print(f"Melhor modelo salvo em: {path_to_best_weights}")
        # Copiar o melhor modelo para a pasta saved_models do projeto
        shutil.copy(path_to_best_weights, TRAINED_YOLO_MODEL_FILENAME)
        print(f"Melhor modelo copiado para: {TRAINED_YOLO_MODEL_FILENAME}")
    else:
        print(f"ERRO: Modelo 'best.pt' não encontrado em {run_dir / 'weights'}")
        print("Verifique os logs de treinamento do YOLO.")
        return

    # 3. Avaliar o modelo 
    # Para avaliação, carregamos o modelo treinado (best.pt)
    print("\nCarregando modelo treinado para avaliação...")
    try:
        trained_model = YOLO(TRAINED_YOLO_MODEL_FILENAME)
    except Exception as e:
        print(f"Erro ao carregar o modelo treinado '{TRAINED_YOLO_MODEL_FILENAME}': {e}")
        return

    print("Avaliando o modelo YOLO no conjunto de validação...")
    try:
        
        val_metrics = trained_model.val(data=str(YOLO_DATASET_DIR), split='val') 
    except Exception as e:
        print(f"Erro durante a avaliação do YOLO: {e}")
        return

    print("Avaliação YOLO concluída.")
    
    accuracy_top1 = val_metrics.top1 if hasattr(val_metrics, 'top1') else (val_metrics.metrics.top1 if hasattr(val_metrics, 'metrics') and hasattr(val_metrics.metrics, 'top1') else None) # Acessa top1 accuracy
    accuracy_top5 = val_metrics.top5 if hasattr(val_metrics, 'top5') else (val_metrics.metrics.top5 if hasattr(val_metrics, 'metrics') and hasattr(val_metrics.metrics, 'top5') else None) # Acessa top5 accuracy
    
    confusion_matrix_data = None
    if hasattr(val_metrics, 'confusion_matrix'):
        if hasattr(val_metrics.confusion_matrix, 'matrix'):
             confusion_matrix_data = val_metrics.confusion_matrix.matrix.tolist() # .matrix é o array numpy
   
    print(f"Acurácia Top-1 no conjunto de validação: {accuracy_top1 if accuracy_top1 else 'N/A'}")
    print(f"Acurácia Top-5 no conjunto de validação: {accuracy_top5 if accuracy_top5 else 'N/A'}")
    if confusion_matrix_data:
        print(f"Matriz de Confusão (dados): {confusion_matrix_data}")
    else:
        print("Matriz de confusão não encontrada diretamente no objeto de métricas. Verifique a pasta de 'runs'.")

    # Salvar um resumo das métricas em JSON
    yolo_metrics_summary = {
        "model_name": "YOLOv8n-cls (fine-tuned)",
        "epochs": EPOCHS,
        "image_size": IMG_SIZE_YOLO,
        "batch_size": BATCH_SIZE,
        "accuracy_top1": accuracy_top1,
        "accuracy_top5": accuracy_top5,
        "confusion_matrix_data (from_val)": confusion_matrix_data,
        "notes": f"Resultados da execução do YOLO salvos em: {run_dir}",
        "path_to_best_weights": str(TRAINED_YOLO_MODEL_FILENAME)
    }

    with open(METRICS_FILENAME, 'w') as f:
        json.dump(yolo_metrics_summary, f, indent=4)
    print(f"\nResumo das métricas do YOLO salvo em: {METRICS_FILENAME}")
    print(f"Verifique a pasta {run_dir} para gráficos detalhados e logs do YOLO.")

if __name__ == "__main__":

    # Verifica se o diretório do dataset YOLO existe
    if not YOLO_DATASET_DIR.is_dir() or \
       not (YOLO_DATASET_DIR / "train").is_dir() or \
       not (YOLO_DATASET_DIR / "val").is_dir():
        print(f"ERRO: Diretório do dataset YOLO não preparado em {YOLO_DATASET_DIR}")
        print("Execute 'Codigos/common/prepare_yolo_dataset.py' primeiro.")
    else:
        train_yolo_classifier()