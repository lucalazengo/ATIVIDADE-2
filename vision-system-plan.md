# Plano do Sistema de Visão Computacional de Monitoramento

## Goal

Desenvolver uma aplicação Web (FastAPI + Next.js + PostgreSQL) com Docker Compose para monitorar o comportamento postural (deitado, em pé, em movimento) de indivíduos em vídeos usando inferência direta (zero-shot) com modelos de visão computacional.

## Tasks

### Backend (FastAPI + PostgreSQL)

- [ ] Task 1: Setup da base do Backend (FastAPI, SQLAlchemy, Pydantic, Alembic) e configuração do PostgreSQL via Docker. → Verify: `docker-compose up backend db` sobe sem erros e `localhost:8000/docs` acessível.
- [ ] Task 2: Implementar módulo de Autenticação (JWT) e CRUD de Usuários (nome, email, senha com hash bcrypt). → Verify: Endpoints `/auth/token`, `/users/` criam, listam, editam e removem usuários com sucesso.
- [ ] Task 3: Implementar gerenciamento de Modelos (Upload de `.pt`/`.pkl` para volume e designação do modelo "ativo"). → Verify: Upload via endpoint `/models/upload` salva arquivo no disco e banco registra modelo como ativo.
- [ ] Task 4: Criar o Pipeline de Inferência via visão computacional (MediaPipe / YOLOv8) capaz de processar os vídeos salvos. → Verify: Script consegue abrir vídeo, classificar os frames em deitado/em pé/movimento e extrair o tempo total individual.
- [ ] Task 5: Implementar lógica de Pipeline de Experimentação (Script de avaliação de 2 abordagens com métricas P/R/F1-score em uma amostra teste offline). → Verify: Notebook/Script gera output comparando dois métodos.
- [ ] Task 6: Desenvolver endpoint de Upload de Vídeo e acionamento assíncrono (Background Tasks do FastAPI) da inferência, salvando os resultados no formato JSON solicitado. → Verify: Endpoints de envio e consulta de resultados (`/videos/:id/results`) retornam o JSON detalhado corretamente.

### Frontend (Next.js + Tailwind CSS)

- [ ] Task 7: Setup do Frontend (Next.js App Router, TailwindCSS, axios/fetch) integrado ao Docker Compose. → Verify: Interface servida localmente e comunicando com Backend via container / proxy.
- [ ] Task 8: Implementar telas de Autenticação (Login) e sub-sistema de Gerenciamento de Usuários (Painel Admin CRUD). → Verify: Login funciona com token salvo (cookies/localAuth) e CRUD de usuários flui.
- [ ] Task 9: Implementar interface para Gerenciamento de Modelos (Upload file) e Upload de Vídeos de monitoramento. → Verify: Arquivos são enviados com sucesso e listados na tela.
- [ ] Task 10: Construção do Dashboard de Resultados, consumindo a consulta gerada para cada vídeo com indicadores de tempo. → Verify: Cards e/ou tabelas mostram os tempos em pé/deitado/movimento por pessoa.

### Infraestrutura e Documentação

- [ ] Task 11: Finalizar `docker-compose.yml` mapeando Volumes corretamente (Postgres, vídeos, modelos) e gerar README.md completo. → Verify: Sistema todo sobe apenas com `docker-compose up --build`.

## Done When

- [ ] O usuário consegue se autenticar, gerenciar usuários da clínica, subir um modelo treinado e enviar um vídeo de um quarto.
- [ ] O sistema processa o vídeo usando inferência (YOLO/MediaPipe), conta o número de pessoas e os tempos nas posturas exigidas, disponibilizando resultado através de consulta.
- [ ] Existe um pipeline documentado comparando dois métodos distintos para os datasets citados.
- [ ] Tudo é executável de forma limpa usando a configuração documentada no README com Docker Compose.
