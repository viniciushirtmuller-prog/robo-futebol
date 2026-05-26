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

        # Dados extraídos
        shots = int(casa.get('Total Shots', 0) or 0) + int(fora.get('Total Shots', 0) or 0)
        corners = int(casa.get('Corner Kicks', 0) or 0) + int(fora.get('Corner Kicks', 0) or 0)
        cards = int(casa.get('Yellow Cards', 0) or 0) + int(fora.get('Yellow Cards', 0) or 0)

        # Lógica de Taxa de Acerto e Sugestão
        # Cálculo baseado em volume (Thresholds ajustáveis)
        taxa_gols = min(95, (shots / 25) * 100)
        taxa_cantos = min(95, (corners / 12) * 100)
        taxa_cartoes = min(95, (cards / 5) * 100)

        msg = (f"🔥 *SINAL DE ENTRADA*\n\n⚽ *{time_casa} x {time_fora}*\n\n"
               f"🎯 *GOLS (Over 1.5/2.5)*\n"
               f"→ Probabilidade: {taxa_gols:.0f}%\n"
               f"→ Entrada: {'Over 2.5' if shots > 22 else 'Over 1.5'}\n\n"
               f"🚩 *CANTOS (Over)*\n"
               f"→ Probabilidade: {taxa_cantos:.0f}%\n"
               f"→ Entrada: {'Mais de 10.5' if corners > 10 else 'Mais de 8.5'}\n\n"
               f"🟨 *CARTÕES (Over)*\n"
               f"→ Probabilidade: {taxa_cartoes:.0f}%\n"
               f"→ Entrada: {'Mais de 4.5' if cards > 4 else 'Mais de 3.5'}\n\n"
               f"⚠️ *Análise automatizada baseada em volume estatístico.*")
        return msg
    except Exception as e:
        return None

async def main():
    bot = Bot(token=TOKEN)
    await bot.send_message(chat_id=CHAT_ID, text="🚀 Robô em MODO ANALISTA ATIVO!")
    
    while True:
        try:
            hoje = datetime.now().strftime('%Y-%m-%d')
            url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"
            resp = requests.get(url, headers={'x-apisports-key': API_KEY}, timeout=10).json()
            
            for j in resp.get('response', []):
                # Monitora todas as ligas
                msg = await analisar_confronto(j['fixture']['id'], j['teams']['home']['name'], j['teams']['away']['name'])
                if msg: 
                    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='Markdown')
            
            await asyncio.sleep(600) 
        except Exception as e:
            await asyncio.sleep(60)

if __name__ == '__main__':
    asyncio.run(main())
