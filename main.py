import requests

API_KEY = "359e1e0ab654e3eb56c7cec930de5d3e"

def verificar_ligas():
    # Esta URL busca as ligas ativas na sua conta
    url = "https://v3.football.api-sports.io/leagues"
    headers = {'x-apisports-key': API_KEY}
    
    resp = requests.get(url, headers=headers).json()
    
    print("--- LIGAS DISPONÍVEIS NA SUA CONTA ---")
    for liga in resp.get('response', []):
        # Filtra apenas o que é do Brasil ou Libertadores
        if "Brazil" in liga['country']['name'] or "Libertadores" in liga['league']['name']:
            print(f"ID: {liga['league']['id']} | NOME: {liga['league']['name']}")

if __name__ == '__main__':
    verificar_ligas()
