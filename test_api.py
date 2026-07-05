
import pytest
from fastapi.testclient import TestClient as FastAPIClient # Use um alias para evitar conflitos
from main import app # Importa a instância da aplicação FastAPI

# Criar um cliente de teste para a aplicação FastAPI
@pytest.fixture(scope="module")
def test_client():
    # Usar FastAPIClient do FastAPI que aceita o argumento 'app'
    with FastAPIClient(app) as client:
        yield client

def test_predict_valid_request(test_client):
    response = test_client.post(
        "/predict",
        json={
            "marca": "Fiat",
            "anoModelo": 2018,
            "mesReferencia": 7,
            "anoReferencia": 2021
        }
    )
    assert response.status_code == 200
    assert "preco_estimado_reais" in response.json()
    assert isinstance(response.json()["preco_estimado_reais"], (float, int))
    print(f"\nTeste de requisição válida: OK. Preço estimado: {response.json()['preco_estimado_reais']}")

def test_predict_invalid_brand(test_client):
    response = test_client.post(
        "/predict",
        json={
            "marca": "MarcaInvalida", # Marca que não está no dataset
            "anoModelo": 2018,
            "mesReferencia": 7,
            "anoReferencia": 2021
        }
    )
    assert response.status_code == 422 # Erro de validação Pydantic
    assert "detail" in response.json()
    assert "Marca 'MarcaInvalida' não é válida" in response.json()["detail"][0]["msg"]
    print("Teste de marca inválida: OK.")

def test_predict_invalid_year_out_of_range(test_client):
    response = test_client.post(
        "/predict",
        json={
            "marca": "Fiat",
            "anoModelo": 1800, # Ano do modelo fora do range válido
            "mesReferencia": 7,
            "anoReferencia": 2021
        }
    )
    assert response.status_code == 422
    assert "detail" in response.json()
    # Pydantic 2.x pode ter mensagens mais genéricas, verificar substring
    assert "Input should be greater than or equal to" in response.json()["detail"][0]["msg"]
    print("Teste de ano de modelo fora do range: OK.")

def test_predict_missing_field(test_client):
    response = test_client.post(
        "/predict",
        json={
            "marca": "Fiat",
            "mesReferencia": 7,
            "anoReferencia": 2021
        } # 'anoModelo' está faltando
    )
    assert response.status_code == 422
    assert "detail" in response.json()
    # Pydantic 2.x retorna 'Field required' com 'F' maiúsculo
    assert "Field required" in response.json()["detail"][0]["msg"]
    print("Teste de campo obrigatório ausente: OK.")

# Teste para simular um erro interno (modelo não carregado, por exemplo)
# Nota: Este teste pode exigir manipulação do ambiente para forçar o erro,
# mas para a estrutura atual da API, um erro de carregamento impediria o startup.
# Uma forma de simular isso seria renomear o arquivo do modelo e rodar a API.
# Aqui, vamos verificar que, se o carregamento falhar, a API levanta um erro ao iniciar.
# Isso já é tratado pelo try-except no main.py, então não é um cenário de /predict.
# Em vez disso, testaremos um cenário onde o `prediction` poderia falhar se os dados fossem malformados internamente após validação Pydantic.

# Para este exemplo, o 'model not found' será coberto se a API não iniciar.
# Se o endpoint /predict for chamado e o modelo não estiver carregado por algum motivo interno, ele resultará em 500.
# Não há um caso de 'modelo não encontrado' que a API trate especificamente APÓS o startup,
# a menos que haja múltiplos modelos e a requisição especifique um que não existe.
# Dado que é um único modelo, vamos focar nos testes de validação de input.
