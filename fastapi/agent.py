from dotenv import load_dotenv
load_dotenv()   # carrega o GROQ_API_KEY 
import os
import requests                                                # 
from openai import AsyncOpenAI
from agents import function_tool, Agent, Runner, ModelSettings, OpenAIChatCompletionsModel  # OpenAI Agents SDK (compatível com o Groq)

# System prompt: regras fixas de comportamento do agente
instructions = """
Você é um agente de atendimento ao cliente.

1. Sempre classifique a intenção do usuário utilizando a ferramenta disponível.
2. Utilize a classificação com a mensagem do usuário para retornar a intenção daquela mensagem.
3. Responda de maneira educada e objetiva.
4. Não invente informações.
"""

# FERRAMENTA (tool) do agente
@function_tool
def classificar_intencao(texto: str) -> str:
    """Classifica a intenção de uma mensagem de atendimento ao cliente."""

    # A rota /classify exige JWT, necessário login pra pegar o token
    login = requests.post(
        "http://127.0.0.1:8000/auth/token",
        data={"username": "admin", "password": "admin"},   # usuario de teste
        timeout=5
    )
    login.raise_for_status()
    token = login.json()["access_token"]

    # chama a rota /classify mandando o token no header
    response = requests.post(
        "http://127.0.0.1:8000/classify",
        json={"message": texto},
        headers={"Authorization": f"Bearer {token}"},
        timeout=5
    )
    response.raise_for_status()
    dados = response.json()       # {intent, probability}
    
    # devolve uma string com a intenção e a probabilidade
    return f"Intenção: {dados['intent']}. Probability: {dados['probability']}"


# Monta o agente com a ferramenta e os parâmetros que forçam a resposta determinística
def configurar_agent():
    # cria o cliente apontando pro Groq (chave + url base)
    client = AsyncOpenAI(
        api_key=os.environ["GROQ_API_KEY"],
        base_url="https://api.groq.com/openai/v1"
    )
    # cria o modelo do Groq
    model = OpenAIChatCompletionsModel(
        model="openai/gpt-oss-20b",
        openai_client=client
    )
    agent = Agent(
        name="Atendente",
        model=model,
        instructions=instructions,
        tools=[classificar_intencao],
        tool_use_behavior="stop_on_first_tool",                 # devolve o resultado da tool direto
        model_settings=ModelSettings(tool_choice="classificar_intencao")  # obriga a chamar a tool
    )
    return agent


# Função que roda o agente: recebe a mensagem, roda e devolve a resposta
def classificar(prompt_user):
    agent = configurar_agent()
    resposta = Runner.run_sync(agent, prompt_user)   # roda de forma sincrona
    return resposta

# Demonstracao de uma conversa com 3 turnos (gera a evidencia da Tarefa 4)
if __name__ == "__main__":
    mensagens = [
        "I need a refund for my purchase",
        "My bill is wrong",
        "Tell me about this product features",
    ]

    for i, msg in enumerate(mensagens, start=1):
        resposta = classificar(msg)
        print(f"\n--- Turno {i} ---")
        print("Usuário:", msg)
        print("Agente :", resposta.final_output)