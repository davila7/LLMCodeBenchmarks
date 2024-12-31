import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
import gzip
import json

def create_session_with_retries():
    session = requests.Session()
    retries = Retry(
        total=5,
        backoff_factor=1,
        status_forcelist=[500, 502, 503, 504],
        allowed_methods=["GET", "POST"]
    )
    adapter = HTTPAdapter(max_retries=retries)
    session.mount('http://', adapter)
    session.mount('https://', adapter)
    return session

url = "https://api.nike.com/cic/grand/v1/graphql/getlistpaginatedlistitems/v3"

headers = {
    "accept": "application/json",
    "accept-encoding": "gzip, deflate, br",
    "accept-language": "en-US,en;q=0.9",
    "appid": "com.nike.commerce.nikedotcom.web",
    "authorization": "Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6ImQyYWY1YTkzLTNlODktNDc2OS04NTIyLTg1NDVhNzgyYzcyNXNpZyJ9.eyJpYXQiOjE3MzIzOTgyMzcsImV4cCI6MTczMjQwMTgzNywiaXNzIjoib2F1dGgyYWNjIiwianRpIjoiNmM4Mjk2ZGItZDRlYS00NTNhLTkzZjQtOWJmMGI5NjdmZGQzIiwiYXVkIjoiY29tLm5pa2UuZGlnaXRhbCIsInNidCI6Im5pa2U6YXBwIiwidHJ1c3QiOjEwMCwibGF0IjoxNzMyMzk0NTEwLCJzY3AiOlsibmlrZS5kaWdpdGFsIl0sInN1YiI6ImNvbS5uaWtlLmNvbW1lcmNlLm5pa2Vkb3Rjb20ud2ViIiwicHJuIjoiMTQ4NTE2NzA1MjciLCJwcnQiOiJuaWtlOnBsdXMiLCJscnNjcCI6Im9wZW5pZCBuaWtlLmRpZ2l0YWwgcHJvZmlsZSBlbWFpbCBwaG9uZSBmbG93IGNvdW50cnkifQ.A10GzW2JJzGoq3OUOPRSSAnxAgGKSzpLpBTUGv_tyeOWQW4SAhkkCgRGkAEjCx2y2uHEbCeJ6EzhvgM38_cPh_4Fj8Y3Xe5x1c8CyfPFTvFd89wZ7OD2c7sCpHuKgfDhWIK8tcGaAn3suBJQlE04pKqzfHcV0UjF4uYl3FPdF3u7iCIvBPon0G_eTwx2Kbv50dpbTKDbEWUXC5BhGPgdjDPc3R6oxKQoODIJItBlDE9Wp-qqFL2ZUNuSEpQxQ_Ui069NWgyWvNvhi8_g5Hl_c-GINenNhfrJNOIlCn0YoBaGQ66o6IBHy5c0qKuJ_CbqxMS5s_L2Mj6gvk1QtEriTg",
    "content-type": "application/json",
    "nike-api-caller-id": "@nike/shop-components@1.201.2",
    "origin": "https://www.nike.com",
    "referer": "https://www.nike.com/",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
    "x-b3-traceid": "08c5128ec3516251",
    "x-kpsdk-ct": "0C3oXyEjvmCzHY1H8cDzFusSkNvpFY31wTnOKBFwHh4tq7pkz4nQHrmcQoqNssjqmqsJigRNQnfmqxPvxVH6QZ5eihmsdpi3tTiRKa7kxAJ5zIwwjeE8kdmuKwofyjTF1TLnPxiUMerh73FHtEM3q95gWPyQ8XnSjjOBD0Ia"
}

# Cookies necesarias
cookies = {
    "NIKE_COMMERCE_COUNTRY": "SE",
    "NIKE_COMMERCE_LANG_LOCALE": "en_GB",
    "nike_locale": "se/en_gb"
}

payload = {
    "variables": {
        "country": "SE",
        "id": "e1291e77-e518-4e3a-b88e-79dd6e34ff85",
        "first": 1,
        "after": 0
    }
}

def decompress_response(response):
    if response.headers.get('content-encoding') == 'gzip':
        return gzip.decompress(response.content).decode('utf-8')
    return response.text

def make_request():
    try:
        session = create_session_with_retries()
        
        # Agregar cookies a la sesión
        for key, value in cookies.items():
            session.cookies.set(key, value)
        
        # Configurar el stream para manejar grandes respuestas
        response = session.post(
            url, 
            headers=headers, 
            json=payload, 
            timeout=30,
            stream=True,
            verify=True
        )
        
        response.raise_for_status()
        
        # Leer y decodificar la respuesta
        content = decompress_response(response)
        return json.loads(content) if content else None
        
    except requests.exceptions.RequestException as e:
        print(f"Error en la solicitud: {e}")
        if hasattr(e.response, 'text'):
            print(f"Respuesta del servidor: {e.response.text}")
        return None
    finally:
        session.close()

def main():
    max_attempts = 3
    attempt = 0

    while attempt < max_attempts:
        try:
            print(f"Intento {attempt + 1} de {max_attempts}")
            response_data = make_request()
            
            if response_data is not None:
                print("Respuesta exitosa:")
                print(json.dumps(response_data, indent=2))
                break
            
            attempt += 1
            if attempt < max_attempts:
                time.sleep(2)
        except Exception as e:
            print(f"Error inesperado: {e}")
            attempt += 1
            if attempt < max_attempts:
                time.sleep(2)

    if attempt >= max_attempts:
        print("Se alcanzó el número máximo de intentos sin éxito")

if __name__ == "__main__":
    main()
