# EXCUTAR APLICAÇÃO COMPLETO

```bash
# Na pasta da "\fastapi" , criar o .venv com as dependências e iniciara a aplicação
py -m venv .venv --upgrade-deps
.venv\Scripts\Activate.ps1
py -m pip install -r requirements.txt
# executar
uvicorn main:app --reload

# ou executar
uvicorn main:app --port 8000 --reload

# ou executar
fastapi dev main.py
```

## Rodar Testes Automatizados

```bash
# Dentro do ambinte virtual .venv
py -m pytest -v
```

## Rodar arquivo ipynb

```bash
# Na pasta da "tp4\eda", dentro do ambiente virtual .venv
jupyter nbconvert --execute --inplace "eda_tp4.ipynb"

# Dentro do ambiente virtual .venv de forma interativa(da pra visualizar as celulas que ja foram executados com o resultado parcial)
papermill "eda_tp4.ipynb" "eda_tp4.ipynb" --log-output

# Confirmar que excutou tudo sem erro
$LASTEXITCODE
```

## Instruções de instalação

1. Abra o projeto e acesse a pasta da API:

```bash
cd .\fastapi
```

2. Crie e ative um ambiente virtual:
   - Verifique se está dentro da pasta "fastapi"

```bash
python -m venv .venv

# Windows - Ative o ambiente virtual
.venv\Scripts\Activate.ps1

# Linux/Mac - Ative o ambiente virtual
source .venv/bin/activate
```

4. Instale as dependências a partir do arquivo requirements.txt:

```bash
python -m pip install -r requirements.txt

# Verifique se foi instalado corretamente (deve aparecer name, location e outras informações sobre o pacote)
python -m pip show fastapi
```

## Instruções de execução

1. Acesse a pasta da API e certifique-se de que o ambiente virtual está ativado (veja passo 3 da instalação, caso tenha aberto um novo terminal):

```bash
cd .\fastapi
```

2. Execute a aplicação:

```bash
fastapi dev main.py
# ou
uvicorn main:app --reload
```

3. A API estará disponível em:
   http://127.0.0.1:8000/docs

# Extras

1. Apagar tudo e recriar o ambiente virtual

   **Windows (PowerShell):**

```bash
deactivate
Remove-Item -Recurse -Force .venv
# Apagar pastas __pycache__
Get-ChildItem -Path . -Recurse -Directory -Filter "__pycache__" | Remove-Item -Recurse -Force
```

**Linux/Mac:**

```bash
deactivate
rm -rf .venv
```

2. Criar requirements.txt

```bash
py -m pip freeze > requirements.txt
```

# Instalação do JWT TOOL

```bash
# FAZER TUDO DENTRO DO .venv
# segundo terminal: clonar e instalar a ferramenta
git clone https://github.com/ticarpi/jwt_tool.git
cd jwt_tool

# instalar as dependências dentro do jwt_tool
py -m pip install -r requirements.txt

# conferir se instalou (mostra a ajuda)
py jwt_tool.py -h
```

# Gerar Token (python)

```bash
python -c "import secrets; print(secrets.token_urlsafe(64))"
```
