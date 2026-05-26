import requests
import asyncio
import logging
from telegram import Bot
from datetime import datetime, timezone

API_KEY = "359e1e0ab654e3eb56c7cec930de5d3e"
TOKEN = "8856369868:AAGjBMrFLZRTMGA_XZpPxB3bGGRX48ErXFc"
CHAT_ID = "805165304"

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
        
        # Lógica de Taxa de Acerto Estimada
        score = 0
        if shots > 20: score += 40
        if corners > 10: score += 40
        if score == 0: score = 30 # Mínimo de chance
        
        return (f"🔥 *SINAL DE ENTRADA*\n\n⚽ *{time_casa} x {time_fora}*\n"
                f"📈 Taxa de Acerto Estimada: {score}%\n\n"
                f"🎯 Total Chutes: {shots}\n"
                f"🚩 Total Cantos: {corners}\n"
                f"⚠️ *Analise antes de entrar!*")
    except Exception as e:
        return None

async def main():
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text="🚀 Robô em MODO FULL (Todas as ligas)!")
    
    while True:
        try:
            hoje = datetime.now().strftime('%Y-%m-%d')
            url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"
            resp = requests.get(url, headers={'x-apisports-key': API_KEY}, timeout=10).json()
            
            for j in resp.get('response', []):
                # Monitora todas as ligas, sem filtrar ID
                msg = await analisar_confronto(j['fixture']['id'], j['teams']['home']['name'], j['teams']['away']['name'])
                if msg: 
                    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
            
            await asyncio.sleep(600) # Checagem a cada 10 min
        except Exception as e:
            await asyncio.sleep(60)

if __name__ == '__main__':
    asyncio.run(main())
