import requests
import asyncio
import logging
from telegram import Bot
from datetime import datetime, timezone

# Configurações do seu Robô
API_KEY = "359e1e0ab654e3eb56c7cec930de5d3e"
TOKEN = "8856369868:AAGjBMrFLZRTMGA_XZpPxB3bGGRX48ErXFc"
CHAT_ID = "805165304"
# IDs das ligas (Brasil, Libertadores, Sul-Americana, Premier League, La Liga, Champions)
LIGAS_ELITE = [71, 13, 11, 39, 140, 2] 

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def analisar_confronto(id_jogo, time_casa, time_fora):
    headers = {'x-apisports-key': API_KEY}
    try:
        url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={id_jogo}"
        resp = requests.get(url, headers=headers, timeout=10).json()
        
        if not resp.get('response') or len(resp['response']) < 2:
            return None

        casa = {s['type']: s['value'] for s in resp['response'][0]['statistics']}
        fora = {s['type']: s['value'] for s in resp['response'][1]['statistics']}

        # Lógica de análise combinada
        shots = int(casa.get('Total Shots', 0)) + int(fora.get('Total Shots', 0))
        corners = int(casa.get('Corner Kicks', 0)) + int(fora.get('Corner Kicks', 0))
        cards = int(casa.get('Yellow Cards', 0)) + int(fora.get('Yellow Cards', 0))

        return (f"🔔 *ALERTA DE OPORTUNIDADE*\n\n⚽ *{time_casa} x {time_fora}*\n"
                f"🎯 Gols: {'Over 2.5' if shots > 25 else 'Over 1.5'} (Chutes: {shots})\n"
                f"🚩 Cantos: {'Mais de 10.5' if corners > 12 else 'Mais de 8.5'} (Cantos: {corners})\n"
                f"🟨 Cartões: {'Mais de 4.5' if cards > 4 else 'Mais de 3.5'} (Cartões: {cards})")
    except Exception as e:
        logger.error(f"Erro na análise: {e}")
        return None

async def main():
    bot = Bot(token=TOKEN)
    logger.info("Robô iniciado com sucesso na nuvem!")
    while True:
        try:
            hoje = datetime.now().strftime('%Y-%m-%d')
            url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"
            resp = requests.get(url, headers={'x-apisports-key': API_KEY}, timeout=10).json()
            
            for j in resp.get('response', []):
                if j['league']['id'] in LIGAS_ELITE:
                    hora_jogo = datetime.strptime(j['fixture']['date'], '%Y-%m-%dT%H:%M:%S+00:00')
                    tempo_restante = (hora_jogo - datetime.now(timezone.utc).replace(tzinfo=None)).total_seconds() / 60
                    
                    if 0 < tempo_restante < 60:
                        msg = await analisar_confronto(j['fixture']['id'], j['teams']['home']['name'], j['teams']['away']['name'])
                        if msg: 
                            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
            
            await asyncio.sleep(1800) # Checa a cada 30 minutos
        except Exception as e:
            logger.error(f"Erro no loop principal: {e}")
            await asyncio.sleep(60)

if __name__ == '__main__':
    asyncio.run(main())
