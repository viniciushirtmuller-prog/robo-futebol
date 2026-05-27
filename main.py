import requests
import asyncio
import os
import sys
from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes, Application
from groq import Groq
from telegram import Bot

# CONFIGURAÇÕES
API_KEY_FUTEBOL = "359e1e0ab654e3eb56c7cec930de5d3e"
TOKEN_TELEGRAM = "8856369868:AAGjBMrFLZRTMGA_XZpPxB3bGGRX48ErXFc"
CHAT_ID = "805165304"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    sys.exit(1)

LIGAS_PERMITIDAS = ["brasileirao", "libertadores", "copa do brasil", "serie a", "premier league"]
client = Groq(api_key=GROQ_API_KEY)

async def analisar_ia(dados):
    prompt = f"Analise estes dados de times que VÃO se enfrentar: {dados}. Dê um prognóstico de aposta (Mercado + Probabilidade) baseado no histórico. Seja profissional e direto."
    try:
        completion = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192")
        return completion.choices[0].message.content
    except Exception as e:
        return f"Erro na IA: {e}"

# --- COMANDOS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("🤖 Robô Analista Online! Estou monitorando as ligas e te enviarei análises pré-jogo.")

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ O robô está ativo e monitorando a API.")

# --- MONITORAMENTO AUTOMÁTICO ---
async def monitorar_jogos(bot: Bot):
    while True:
        try:
            tz = pytz.timezone('America/Sao_Paulo')
            hoje = datetime.now(tz).strftime('%Y-%m-%d')
            url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"
            resp = requests.get(url, headers={'x-apisports-key': API_KEY_FUTEBOL}).json()
            
            for j in resp.get('response', []):
                if any(fav in j['league']['name'].lower() for fav in LIGAS_PERMITIDAS) and j['fixture']['status']['short'] == 'NS':
                    info = f"{j['teams']['home']['name']} x {j['teams']['away']['name']}, Liga: {j['league']['name']}"
                    analise = await analisar_ia(info)
                    await bot.send_message(chat_id=CHAT_ID, text=f"📋 *PRÉ-JOGO*\n{analise}", parse_mode='Markdown')
                    await asyncio.sleep(10)
        except Exception as e:
            print(f"Erro no loop: {e}")
        await asyncio.sleep(3600) # Checagem a cada 1 hora

if __name__ == '__main__':
    # Configuração do App com comandos
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status))
    
    # Inicia o monitoramento em background
    loop = asyncio.get_event_loop()
    loop.create_task(monitorar_jogos(app.bot))
    
    app.run_polling()
