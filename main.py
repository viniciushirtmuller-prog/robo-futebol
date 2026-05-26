import requests
import asyncio
import logging
from telegram import Bot
from datetime import datetime, timezone

API_KEY = "359e1e0ab654e3eb56c7cec930de5d3e"
TOKEN = "8856369868:AAGjBMrFLZRTMGA_XZpPxB3bGGRX48ErXFc"
CHAT_ID = "805165304"
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

        shots = int(casa.get('Total Shots', 0)) + int(fora.get('Total Shots', 0))
        corners = int(casa.get('Corner Kicks', 0)) + int(fora.get('Corner Kicks', 0))
        cards = int(casa.get('Yellow Cards', 0)) + int(fora.get('Yellow Cards', 0))

        # Filtro mais leve: diminuímos a exigência para disparar mais sinais
        if shots > 18 or corners > 8 or cards > 3:
            return (f"🔔 *ALERTA DE OPORTUNIDADE*\n\n⚽ *{time_casa} x {time_fora}*\n"
                    f"🎯 Gols (Over): {'Sim' if shots > 20 else 'Possível'}\n"
                    f"🚩 Cantos: {corners} (Total)\n"
                    f"🟨 Cartões: {cards} (Total)")
        return None
    except Exception as e:
        return None

async def main():
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text="🤖 Robô em modo ALERTA ATIVO!")
    
    while True:
        try:
            hoje = datetime.now().strftime('%Y-%m-%d')
            url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"
            resp = requests.get(url, headers={'x-apisports-key': API_KEY}, timeout=10).json()
            
            for j in resp.get('response', []):
                if j['league']['id'] in LIGAS_ELITE:
                    hora_jogo = datetime.strptime(j['fixture']['date'], '%Y-%m-%dT%H:%M:%S+00:00')
                    tempo_restante = (hora_jogo - datetime.now(timezone.utc).replace(tzinfo=None)).total_seconds() / 60
                    
                    # Aumentado para 180 min (3 horas) para capturar mais jogos
                    if 0 < tempo_restante < 180:
                        msg = await analisar_confronto(j['fixture']['id'], j['teams']['home']['name'], j['teams']['away']['name'])
                        if msg: 
                            await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
            
            await asyncio.sleep(600) # Checa a cada 10 minutos para ser mais rápido
        except Exception as e:
            await asyncio.sleep(60)

if __name__ == '__main__':
    asyncio.run(main())
