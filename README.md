
# AT2 - Modelagem e Experimentação para Classificação de Posturas Humanas

Este diretório contém os códigos e resultados da **Atividade 2 (AT2)** do case de Visão Computacional, focada na modelagem e experimentação de diferentes abordagens para a classificação de posturas humanas.

##  Visão Geral

A AT2 envolve o treinamento e avaliação de dois modelos distintos para classificar imagens nas seguintes posturas:

- **Em Pé**
- **Sentado**
- **Em Movimento**

O dataset foi preparado na **AT1** a partir do **MPII Human Pose Dataset**.

### Modelos implementados:

1. **Modelo A: MediaPipe + RandomForest**  
   Extrai keypoints de pose com MediaPipe e os utiliza como features para um classificador RandomForest.

2. **Modelo B: YOLOv8-cls**  
   Realiza fine-tuning de um modelo YOLOv8 Nano pré-treinado para classificação de imagens inteiras.

## 📁 Estrutura de Arquivos

```
AT2/
├── Codigos/
│   ├── common/
│   │   ├── __init__.py
│   │   ├── data_loader.py
│   │   └── prepare_yolo_dataset.py
│   ├── model_A_mediapipe_classifier/
│   │   ├── __init__.py
│   │   ├── mediapipe_utils.py
│   │   └── train_mp_classifier.py
│   └── model_B_yolo_classifier/
│       ├── __init__.py
│       └── train_yolo_classifier.py
│   └── run_experiments.py  # (Opcional)
├── Dados/
│   ├── images/
│   ├── posture_classes/
│   └── sample_visuals/
│       ├── em_pe/
│       ├── sentado/
│       └── movimento/
├── Relatorio/
│   └── AT2_Modeling_Report.pdf
├── saved_models/
│   ├── model_A_mp_classifier.pkl
│   ├── scaler_model_A.pkl
│   ├── label_encoder_model_A.pkl
│   └── model_B_yolo_classifier.pt
├── outputs/
│   ├── model_A_mp_metrics.json
│   ├── model_B_yolo_metrics.json
│   └── yolo_runs/
├── yolo_classification_dataset/
│   ├── train/
│   │   ├── em_pe/
│   │   ├── sentado/
│   │   └── movimento/
│   └── val/
│       ├── em_pe/
│       ├── sentado/
│       └── movimento/
```

**Nota:**  
O diretório `Dados/` é referenciado pelo script `Codigos/common/data_loader.py`. Ajuste o caminho `BASE_DATA_DIR` conforme a localização real.

##  Pré-requisitos

- **Python**: 3.10 ou superior (recomendado: 3.12).
- **Ambiente virtual** (recomendado):

```bash
python -m venv .venv
source .venv/bin/activate  # Linux/macOS
# .venv\Scripts\activate   # Windows
```

- **Dataset da AT1**: Pastas `Dados/images/` e `Dados/sample_visuals/` disponíveis.

- **Dependências**:

```bash
pip install opencv-python numpy pandas scikit-learn mediapipe joblib ultralytics tensorflow
```

 *TensorFlow é usado para `to_categorical` no `data_loader.py`, mas pode ser opcional.*

##  Instruções de Execução

###  Preparação dos Dados

O Modelo B (YOLO) requer estrutura de pastas específica. Para isso, execute:

```bash
python Codigos/common/prepare_yolo_dataset.py
```

 Isso criará a pasta `yolo_classification_dataset/` com as imagens organizadas por classe (`em_pe`, `sentado`, `movimento`) para treino e validação.

###  Treinamento e Avaliação dos Modelos

### Modelo A: MediaPipe + RandomForest

Execute:

```bash
python Codigos/model_A_mediapipe_classifier/train_mp_classifier.py
```

**Este script:**

- Carrega imagens e rótulos via `data_loader.py`.
- Extrai features de pose com `mediapipe_utils.py`.
- Divide os dados em treino e teste.
- Normaliza as features com `StandardScaler`.
- Treina um RandomForest.
- Salva:
  - Modelo (`model_A_mp_classifier.pkl`)
  - Scaler (`scaler_model_A.pkl`)
  - Label Encoder (`label_encoder_model_A.pkl`)
- Avalia e salva métricas: `outputs/model_A_mp_metrics.json`.

### Modelo B: YOLOv8-cls

Antes: certifique-se de ter executado `prepare_yolo_dataset.py`.

Execute:

```bash
python Codigos/model_B_yolo_classifier/train_yolo_classifier.py
```

**Este script:**

- Carrega YOLOv8 Nano pré-treinado (`yolov8n-cls.pt`).
- Realiza fine-tuning usando `yolo_classification_dataset/`.
- Salva:
  - Resultados em `outputs/yolo_runs/`.
  - Melhor modelo em `saved_models/model_B_yolo_classifier.pt`.
- Avalia e salva métricas: `outputs/model_B_yolo_metrics.json`.

 *Na primeira execução, haverá download automático dos pesos (`yolov8n-cls.pt`) e da fonte `Arial.ttf`.*

###  Verificação dos Resultados

- **Modelos treinados** → `saved_models/`
- **Métricas** → `outputs/`
- **Resultados detalhados do YOLO** → `outputs/yolo_runs/` (gráficos, loss, accuracy, etc.)
- **Relatório** → `Relatorio/AT2_Modeling_Report.pdf`

## Estrutura dos Scripts Principais

- `Codigos/common/data_loader.py`: Carrega imagens e rótulos, divide em treino e teste.
- `Codigos/common/prepare_yolo_dataset.py`: Prepara dados na estrutura requerida pelo YOLO.
- `Codigos/model_A_mediapipe_classifier/mediapipe_utils.py`: Extrai landmarks com MediaPipe.
- `Codigos/model_A_mediapipe_classifier/train_mp_classifier.py`: Treina e avalia Modelo A.
- `Codigos/model_B_yolo_classifier/train_yolo_classifier.py`: Treina e avalia Modelo B com Ultralytics.

## Considerações Adicionais

- Scripts testados em ambiente **Linux**.
- Ajustes de caminho podem ser necessários para **Windows**.
- Treinamento, especialmente do **Modelo B**, pode ser **demorado em CPU**.
- Hiperparâmetros podem ser ajustados conforme necessidade:  
  - RandomForest (`n_estimators`)  
  - YOLO (`epochs`, `lr`, etc.)

##  Referências

- [MediaPipe](https://google.github.io/mediapipe/)
- [Ultralytics YOLO](https://docs.ultralytics.com/)
- [MPII Human Pose Dataset](http://human-pose.mpi-inf.mpg.de/)

##  Contribuição

Para melhorias, sugestões ou correção de bugs, fique à vontade para abrir um *issue* ou *pull request*.

##  Licença

Este projeto é acadêmico e está licenciado sob os termos da instituição responsável.
