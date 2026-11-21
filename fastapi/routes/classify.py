import joblib
from agent import classificar   # funcao que roda o agente (do agent.py na raiz)
from fastapi import APIRouter, Depends, HTTPException, Path
from sqlmodel import Session, select
from database.connection import get_session
from models.error_models import RESPOSTA_401_TOKEN, RESPOSTA_404_PREDICTION
from models.prediction_request_model import PredictionRequest
from models.prediction_response_model import PredictionResponse
from models.prediction_sql_model import Prediction
from models.user_sql_model import User
from security.dependencies import get_current_user


router = APIRouter(tags=["Classificações"])  # Grupo de rotas de classificação

# carrega o modelo e o vetorizador salvos no notebook 
# carrega uma vez so, quando a API sobe
modelo = joblib.load("melhor_classificador_intent.joblib")
vectorizer = joblib.load("vectorizer.joblib")

# ROTA - Classifica a intencao usando o modelo treinado (protegida por JWT)
@router.post(
    "/classify",
    summary="Classificar a intenção da mensagem do usuário",
    description="""
Descobre qual é a **intenção** da mensagem usando o modelo treinado no notebook.

**Autenticação:** precisa de token JWT (clique em **Authorize** antes).

**Como testar:**
1. Faça login no **Authorize** (ex.: `admin` / `admin`)
2. Clique em **Try it out**
3. Mande uma mensagem em inglês, por exemplo:
   - `{"message": "My product is broken"}`
   - `{"message": "How much do I have to pay?"}`
4. Clique em **Execute**

**Respostas:**
- `200`: a intenção e a probabilidade
- `401`: sem token, token inválido ou expirado
- `422`: mensagem vazia ou faltando
""",
    responses=RESPOSTA_401_TOKEN,
)
def classify(
    request: PredictionRequest,
    current_user: User = Depends(get_current_user)   # exige o JWT
):    

    texto = request.message.strip()       # tira os espacos do comeco e do fim
    if not texto:
        raise HTTPException(
            status_code=422,
            detail="A mensagem não pode estar vazia"
        )

    X = vectorizer.transform([texto])     # matriz com 1 linha (a mensagem)
    intent = modelo.predict(X)[0]         # a intencao prevista
    probability = modelo.predict_proba(X).max()   # a probabilidade da classe

    return {
        "intent": str(intent),
        "probability": float(probability)
    }


# ROTA - Usa o agente de IA, que chama o /classify como ferramenta
@router.post("/classify_comllm",
            summary="(Com LLM) Classificar a intenção usando o agente de IA",
            description="""
Usa um **agente de IA** (OpenAI Agents SDK + Groq) pra descobrir a intenção.
O agente usa o nosso `/classify` como ferramenta.

**Autenticação:** não precisa de token aqui (o agente faz o login sozinho pra chamar o `/classify`).

**Atenção:** precisa da `GROQ_API_KEY` no `.env`.

**Como testar:**
1. Clique em **Try it out**
3. Mande uma mensagem em inglês, por exemplo:
   - `{ "message": "I need a refund for my purchase" }`
   - `{ "message": "My bill is wrong" }`
   - `{ "message": "Tell me about this product features" }`
3. Clique em **Execute** e veja a resposta do agente

**Respostas:**
- `200`: a resposta do agente
- `422`: mensagem faltando
- `500`: erro na IA (chave errada, sem internet, etc.)
""")
def classify_comllm(predictionRequest: PredictionRequest):
    resposta = classificar(predictionRequest.message)   # roda o agente com a mensagem

    # mostra o consumo de tokens no terminal (igual a aula)
    uso = resposta.context_wrapper.usage
    print(
        f"[tokens] entrada={uso.input_tokens} "
        f"saida={uso.output_tokens} "
        f"total={uso.total_tokens} "
        f"chamadas={uso.requests}"
    )

    return {"response": resposta.final_output}   # a resposta final do agente