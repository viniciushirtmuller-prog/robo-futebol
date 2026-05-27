import requests
import asyncio
import os
import sys
from datetime import datetime
import pytz
from telegram import Bot
from groq import Groq

# CONFIGURAÇÕES
API_KEY_FUTEBOL = "359e1e0ab654e3eb56c7cec930de5d3e"
TOKEN_TELEGRAM = "8856369868:AAGjBMrFLZRTMGA_XZpPxB3bGGRX48ErXFc"
CHAT_ID = "805165304"

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
if not GROQ_API_KEY:
    sys.exit(1)

LIGAS_PERMITIDAS = ["brasileirao", "libertadores", "copa do brasil", "serie a", "premier league"]

bot = Bot(token=TOKEN_TELEGRAM)
client = Groq(api_key=GROQ_API_KEY)

async def analisar_automatica(dados):
    prompt = f"Analise estes dados de times que VÃO se enfrentar: {dados}. Dê um prognóstico de aposta (Mercado + Probabilidade) baseado no histórico. Seja direto."
    try:
        completion = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192")
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erro na IA: {e}"

async def monitorar_jogos():
    while True:
        try:
            tz = pytz.timezone('America/Sao_Paulo')
            hoje = datetime.now(tz).strftime('%Y-%m-%d')
            url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"
            
            resp = requests.get(url, headers={'x-apisports-key': API_KEY_FUTEBOL}).json()
            
            for j in resp.get('response', []):
                liga = j['league']['name'].lower()
                status = j['fixture']['status']['short']
                
                # BUSCA APENAS JOGOS QUE NÃO COMEÇARAM (NS)
                if any(fav in liga for fav in LIGAS_PERMITIDAS) and status == 'NS':
                    id_jogo = j['fixture']['id']
                    
                    # Para jogos pré-jogo, usamos o endpoint de 'headtohead' ou apenas info básica
                    # Aqui passamos a info do time para a IA decidir
                    info_times = f"Time Casa: {j['teams']['home']['name']}, Time Fora: {j['teams']['away']['name']}, Liga: {j['league']['name']}"
                    
                    analise = await analisar_automatica(info_times)
                    await bot.send_message(chat_id=CHAT_ID, text=f"📋 *PRÉ-JOGO (Análise)*\n{j['teams']['home']['name']} x {j['teams']['away']['name']}\n\n{analise}", parse_mode='Markdown')
                    await asyncio.sleep(5)
            
        except Exception as e:
            print(f"Erro: {e}")
            
        await asyncio.sleep(3600) # Busca a cada 1 hora

if __name__ == '__main__':
    asyncio.run(monitorar_jogos())
