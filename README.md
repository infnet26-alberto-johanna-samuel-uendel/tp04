# TP4 - Análise e Segurança de Agentes de IA

**Projeto de Bloco | Instituto Infnet**

Sistema de atendimento ao cliente alimentado por inteligência artificial. Este quarto TP dá continuidade ao
TP3 e implementa a **fase preditiva** e o **agente**: treina o classificador de intenções, integra-o à API
como um endpoint protegido por JWT, constrói um agente de IA que usa o classificador como ferramenta e inicia
o **teste adversarial** (pentest parcial) com ataques de JWT.

Grupo

- Alberto Frasson
- Johanna Liza
- Samuel Hermany
- Uendel Ives

---

## Objetivo do projeto

O bloco tem duas fases. Na primeira, constrói-se um sistema de atendimento ao cliente alimentado por IA; na
segunda, o sistema é atacado para identificar as falhas de segurança nele deixadas. Por isso a segurança é
tratada desde o primeiro commit, e não como camada adicionada ao final.

Este TP4 corresponde à competência **"Integrar o classificador de intenções e o agente autônomo à API com
pentest parcial"** e entrega:

1. **Classificador de intenções treinado** - pipeline `TF-IDF` + `LogisticRegression`, avaliado com **matriz
   de confusão**, **precision**, **recall** e **F1 por classe** e **ROC-AUC**, comparado com uma **baseline**
   (classe mais frequente). No notebook **[eda/eda_tp4.ipynb](eda/eda_tp4.ipynb)**.
2. **Busca de hiperparâmetros com `GridSearchCV`** - dois parâmetros (`C` e `solver`), com os melhores
   parâmetros e o ganho de desempenho documentados no mesmo notebook.
3. **Endpoint `POST /classify`** na API - recebe um texto, **exige autenticação JWT**, passa pelo modelo
   treinado e retorna a **intenção prevista com a probabilidade**. O modelo é serializado (`joblib`) e
   carregado na inicialização da API.
4. **Agente de IA** - construído com o **OpenAI Agents SDK** (modelo via **Groq**), com uma `@function_tool`
   que chama o `/classify`, executado com `Runner.run`, demonstrando uma conversa de **3 turnos**.
5. **Pentest parcial** - ataques de **JWT** com a ferramenta **`jwt_tool`** (None attack, Algorithm Confusion
   e crack do segredo HS256), documentados num log na pasta **[pentest/](pentest/)**.

Continuam valendo os controles de segurança do TP3: banco SQLite consultado somente via **SQLModel**, modelos
Pydantic com `extra='forbid'`, controle de acesso por ownership (BOLA), headers de segurança HTTP, CORS com
allowlist explícita e rate limiting com SlowAPI no `POST /auth/token`.

> A rota `/classify` usa o modelo treinado. A rota `/predict` continua retornando uma **intenção fixa**
> (legado do TP3, mantida para compatibilidade).

> ⚠️ **Observação sobre o modelo:** o dataset é **sintético** e o texto não tem relação com o rótulo. Por
> isso o classificador fica **no nível do acaso** (~20%, igual à baseline). Isso está documentado com
> transparência no notebook e já era esperado desde os testes de hipótese do TP3 - a limitação é do dado, não
> do pipeline.

---

## Sobre o dataset

**Customer Support Ticket Dataset** - Kaggle, publicado por Suraj (`suraj520`), licença **CC0: Public
Domain**.
🔗 https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset

> A análise exploratória e o treino do classificador estão no notebook **[eda/eda_tp4.ipynb](eda/eda_tp4.ipynb)**.

### Principais características

|                         |                                                                                                                                                           |
| ----------------------- | --------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Dimensões**           | 8.469 registros × 17 atributos                                                                                                                            |
| **Variável de entrada** | `Ticket Description` - relato do cliente em texto livre (em inglês)                                                                                       |
| **Variável-alvo**       | `Ticket Type` - 5 categorias praticamente balanceadas (`Billing inquiry`, `Cancellation request`, `Product inquiry`, `Refund request`, `Technical issue`) |
| **Natureza**            | Dados **sintéticos** - o rótulo não tem relação direta com o texto                                                                                        |

> ⚠️ O modelo foi treinado com mensagens em **inglês**, então o `/classify` deve ser testado com mensagens em
> inglês (ex.: `I want to cancel my order`). Mensagens em português caem fora do vocabulário e viram um chute.

---

## Instruções de instalação

### Pré-requisitos

- Python 3.10 ou superior
- `pip`
- **Somente no Windows:** liberar a execução de scripts na sessão atual do PowerShell (uma única vez)

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
```

### Passo a passo

**1. Clone o repositório e acesse a pasta da API**

```bash
git clone https://github.com/infnet26-alberto-johanna-samuel-uendel/tp04.git
cd tp04/fastapi
```

**2. Crie e ative o ambiente virtual**

```bash
python -m venv .venv
```

```powershell
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
```

```bash
# Linux / macOS
source .venv/bin/activate
```

**3. Instale as dependências**

```bash
python -m pip install -r requirements.txt
```

> O `requirements.txt` do TP4 já inclui o `scikit-learn` e o `joblib` (carregam o modelo na API), o
> `openai-agents`, o `openai` e o `requests` (usados pelo agente) e o `python-dotenv` (carrega o `.env`).

**4. Configure as variáveis de ambiente (`.env` na pasta `fastapi/`)**

O agente usa o Groq, então é preciso uma chave (grátis em `https://console.groq.com/keys`):

```
GROQ_API_KEY=cole-sua-chave-aqui
```

> Mantenha o `.env` no `.gitignore` para não subir a chave no repositório.

---

## Criação e população do banco de dados

O banco `fastapi/database.db` já está no repositório. Para recriá-lo do zero, a partir da pasta `fastapi/`,
com o ambiente virtual ativado:

```bash
python sqlite_database.py
```

Cada prediction tem um `owner_id` que identifica seu proprietário:

| Prediction | Texto                       | Proprietário |
| ---------- | --------------------------- | ------------ |
| 1          | Meu pedido não chegou       | `admin`      |
| 2          | Quero cancelar minha compra | `admin`      |
| 3          | Qual o prazo de entrega?    | `jose`       |

> SQL direto (`sqlite3`) é usado **somente** nesses scripts. Dentro da API, todas as consultas são feitas com
> **SQLModel**.

---

## Instruções de execução

### API

A partir da pasta `fastapi/`, com o ambiente virtual ativado:

```bash
# desenvolvimento (HTTP)
uvicorn main:app --reload
# ou
fastapi dev main.py
```

A documentação interativa (Swagger UI) fica em **http://127.0.0.1:8000/docs**.

> Para servir com HTTPS local (certificado autoassinado), use `python run_https.py` (sobe em
> `https://127.0.0.1:8443`). Em produção (Render) o HTTPS é fornecido pela plataforma:
> **https://tp04-pb.onrender.com/docs**.

#### Endpoints

| Método | Rota                | Autenticação   | Descrição                                                              |
| ------ | ------------------- | -------------- | ---------------------------------------------------------------------- |
| `GET`  | `/health`           | Pública        | Verifica se a API está ativa                                           |
| `POST` | `/auth/token`       | Pública        | Autentica o usuário e devolve um token JWT (validade de 30 minutos)    |
| `POST` | `/predict`          | **Bearer JWT** | Recebe uma mensagem e retorna uma intenção **fixa** (legado do TP3)    |
| `POST` | `/classify`         | **Bearer JWT** | Classifica a intenção com o **modelo treinado** (intent + probability) |
| `POST` | `/classify_comllm`  | Pública        | Roda o **agente de IA**, que usa o `/classify` como ferramenta         |
| `GET`  | `/predictions`      | **Bearer JWT** | Lista somente as predictions do usuário logado                         |
| `GET`  | `/predictions/{id}` | **Bearer JWT** | Retorna a prediction somente se ela pertencer ao usuário logado        |

#### Credenciais

| Usuário | Senha   |
| ------- | ------- |
| `admin` | `admin` |
| `jose`  | `1234`  |
| `maria` | `1234`  |

> ⚠️ Usuários e senhas de exemplo existem **somente para fins acadêmicos**.

---

## Classificador de intenções (notebook)

O notebook **[eda/eda_tp4.ipynb](eda/eda_tp4.ipynb)** continua a análise do TP3 e adiciona a parte do modelo:

- **Tarefa 1** - treina o classificador (`TF-IDF` + `LogisticRegression`), avalia com matriz de confusão,
  métricas por classe e ROC-AUC, e compara com a baseline (`DummyClassifier`).
- **Tarefa 3** - `GridSearchCV` buscando os melhores hiperparâmetros (`C` e `solver`), com os melhores
  parâmetros e o ganho documentados.
- Ao final, salva o modelo e o vetorizador em **`melhor_classificador_intent.joblib`** e
  **`vectorizer.joblib`** (os dois arquivos que a API carrega).

---

## Agente de IA

O **[fastapi/agent.py](fastapi/agent.py)** constrói o agente com o **OpenAI Agents SDK** (modelo via Groq):

- `Agent` com um **system prompt** de atendimento ao cliente.
- `@function_tool` `classificar_intencao` - faz login, pega o token JWT e chama o `/classify`.
- `Runner.run_sync` executa o ciclo do agente.
- O bloco de demonstração roda **3 turnos** com mensagens diferentes.

Para rodar a demonstração (precisa da API no ar e da `GROQ_API_KEY` no `.env`):

```bash
# terminal 1: API
fastapi dev main.py
# terminal 2: agente
py agent.py
```

Também dá para disparar o agente pela rota `POST /classify_comllm` no Swagger.

---

## Pentest parcial - ataques de JWT

O teste adversarial do TP4 usa a ferramenta **`jwt_tool`** (ticarpi) para atacar a API e verificar se as
defesas de JWT funcionam. Os resultados ficam documentados em **[pentest/](pentest/)**.

| Ataque                          | Hipótese (pelo código)        | Resultado                                                 |
| ------------------------------- | ----------------------------- | --------------------------------------------------------- |
| **JWT None**                    | Rejeitado (só aceita `HS256`) | **401** - seguro                                          |
| **Algorithm Confusion (RS→HS)** | Não aplicável (sem RSA)       | pré-condição ausente                                      |
| **Crack do segredo HS256**      | Depende da força do segredo   | documentado no log                                        |
| **Forja de identidade**         | Ownership protege             | token forjado barra em recurso de outro usuário (**404**) |

> ⚠️ Ataques só devem ser feitos contra a **própria API** ou contra a de um colega **com autorização por
> escrito**. Para instalar a ferramenta, veja o `README` dentro de `fastapi/jwt_tool/`.

---

## Controles de segurança

| Controle             | Como foi implementado                                                                                                    |
| -------------------- | ------------------------------------------------------------------------------------------------------------------------ |
| Campos extras        | Modelos Pydantic com `extra='forbid'`: campo não definido → **422**                                                      |
| Ownership (BOLA)     | As rotas de predictions filtram pelo `owner_id` do usuário logado → **404** para recurso de outro                        |
| Autenticação         | JWT (HS256), validade de 30 minutos, em todas as rotas protegidas                                                        |
| Headers de segurança | Middleware adiciona `Strict-Transport-Security`, `X-Frame-Options`, `X-Content-Type-Options` e `Content-Security-Policy` |
| `/docs` sem CDN      | Swagger UI servido pela própria API em `/static`, com atributo `integrity` (SRI)                                         |
| CORS                 | `CORSMiddleware` com lista explícita de origens (sem `*`)                                                                |
| Rate limiting        | SlowAPI no `POST /auth/token`: **10 requisições por minuto por IP** → **429**                                            |

---

## Execução dos testes

Os testes usam o `TestClient` do FastAPI. A partir da pasta `fastapi/`, com o ambiente virtual ativado:

```bash
python -m pytest tests/ -v
```

Os testes cobrem autenticação, autorização/BOLA, validação de entrada, rate limiting, rota protegida e
headers de segurança. O workflow **[.github/workflows/tests.yml](.github/workflows/tests.yml)** roda o
`pytest` automaticamente a cada push.

---

## Estrutura de pastas

```
TP4/
├── README.md                          # este arquivo
├── render.yaml                        # deploy na Render
├── .gitignore
├── .github/
│   └── workflows/tests.yml            # GitHub Actions: roda pytest a cada push
├── data/
│   └── customer_support_tickets.csv   # dataset
├── docs/                              # imagens (fluxo, endpoints, evidência da Tarefa 4)
├── eda/
│   ├── eda_tp4.ipynb                   # EDA + classificador (Tarefas 1 e 3) + geração dos .joblib
│   ├── customer_support_tickets.csv
│   ├── melhor_classificador_intent.joblib
│   └── vectorizer.joblib
├── zap/                               # relatórios do ZAP (do TP3)
│
├── fastapi/                           # Aplicação FastAPI
│   ├── main.py                        # app, middlewares, rate limit, load_dotenv e routers
│   ├── agent.py                       # agente de IA (Agents SDK + Groq) - Tarefa 4
│   ├── README.md                      # instruções específicas da API
│   ├── requirements.txt
│   ├── run_https.py                   # sobe a API com HTTPS
│   ├── database.db                    # banco SQLite
│   ├── sqlite_database.py             # cria e popula o banco
│   ├── sqlite_populate.py             # popula o banco
│   ├── .env                           # GROQ_API_KEY (não versionar)
│   ├── .env.example
│   ├── melhor_classificador_intent.joblib   # modelo carregado pela API
│   ├── vectorizer.joblib                     # vetorizador TF-IDF
│   │
│   ├── database/                      # connection.py (engine/sessão SQLModel)
│   ├── models/                        # modelos Pydantic e tabelas SQLModel
│   ├── routes/                        # auth.py, predict.py, classify.py, health.py, docs.py
│   ├── security/                      # jwt.py, dependencies.py
│   ├── static/                        # arquivos do Swagger UI
│   ├── tests/                         # testes automatizados (pytest)
│   └── jwt_tool/                      # ferramenta de ataque JWT (Tarefa 5)
│
└── pentest/                            # log do pentest parcial (Tarefas 5 e 6)
```

---

## Referências

- Dataset: https://www.kaggle.com/datasets/suraj520/customer-support-ticket-dataset
- Documentação FastAPI: https://fastapi.tiangolo.com
- OpenAI Agents SDK: https://openai.github.io/openai-agents-python/
- Groq: https://console.groq.com
- jwt_tool: https://github.com/ticarpi/jwt_tool
- RFC 7519 - JSON Web Token (JWT): https://www.rfc-editor.org/rfc/rfc7519
- OWASP Top 10: https://owasp.org/www-project-top-ten/
