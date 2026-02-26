# Monitoramento Postural com Visão Computacional

## Objetivo

Desenvolvimento de sistema baseado em visão computacional e aprendizado de máquina para monitorar o comportamento postural de indivíduos em ambientes controlados, como quartos hospitalares.

O sistema é capaz de:

- Processar vídeos enviados.
- Detectar e contabilizar o número de vezes que uma pessoa esteve deitada, em pé ou em movimento.
- Armazenar os resultados e disponibilizá-los via consultas autenticadas.
- Integrar diferentes modelos (pipelines com algoritmos zero-shot como YOLO e MediaPipe).

## Tecnologias

- **Backend:** Python + FastAPI
- **Processamento (Visão):** YOLOv8 e/ou MediaPipe (inferência direta zero-shot).
- **Banco de Dados:** PostgreSQL
- **Frontend:** Next.js + React + Tailwind CSS
- **Infraestrutura:** Docker e Docker Compose

## Como o Sistema Funciona

- Uma API REST (**FastAPI**) é utilizada para receber uploads de vídeos. Ao receber o vídeo, ela aciona uma rotina em Background que roda a inferência sobre os frames e extrai o comportamento.
- Um Frontend Web interativo em **Next.js** consome essa API de modo autenticado por JWT (Jason Web Tokens) e persiste um cadastro seguro de dados do modelo e usuários na base **PostgreSQL**.
- Arquivos sensíveis de inteligência ou mídias são salvos nos file-systems mapeados via Docker volumes (`models/` e `videos/`).

## Guia de Instalação e Execução (Docker Compose)

### Pré-requisitos

- Docker Engine e Docker Compose instalados.
- Aproximadamente 5GB livres no disco (imagens do Postgres e Python pesam um pouco).

### Subindo o servidor

1. Na raiz do projeto, execute:
   ```bash
   docker-compose up --build
   ```
2. Acesse:
   - **Frontend:** http://localhost:3000
   - **Backend API (Swagger Docs):** http://localhost:8000/docs

## Pipelines e Modelos (Zero-shot)

O backend suporta a inferência usando `ultralytics` (YOLO) e `mediapipe`. Estes modelos capturam coordenadas faciais/corporais e determinam, através de scripts especializados, posturas de forma imediata (zero-shot).
O banco de validação de algoritmos (comparativo MPII vs Leeds) deverá ser guiado por Notebooks em ambientes controlados offline ou scripts de experimentação anexos ao projeto (a construir).
