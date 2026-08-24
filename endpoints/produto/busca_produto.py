import requests as re

porta = 5000
base = f"http://127.0.0.1:{porta}"

def busca_produto():
    url = f"{base}/busca_produto"
    
    try:
        response = re.get(url)
        
        # Garante que vai disparar exceção em caso de erro 4xx ou 5xx
        response.raise_for_status() 
        
        # Se a API retornou resposta totalmente vazia (204 No Content, por exemplo)
        if not response.text.strip():
            return []
            
        return response.json()
        
    except re.exceptions.HTTPError as http_err:
        print(f"[ERRO HTTP {response.status_code}]: O backend retornou:")
        print(response.text)  # Exibe no terminal a mensagem/stacktrace real do Flask/FastAPI
        return []
        
    except re.exceptions.RequestException as e:
        print(f"[ERRO CONEXÃO]: Não foi possível conectar na porta {porta}. O backend está rodando?")
        return []
        
    except ValueError:
        print(f"[ERRO JSON]: A rota retornou algo que não é um JSON válido:")
        print(response.text)
        return []