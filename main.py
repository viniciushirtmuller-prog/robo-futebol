import requests
import asyncio
import os
import sys
from datetime import datetime
import pytz
from telegram import Update, Bot
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from groq import Groq

# CONFIGURAÇÕES
API_KEY_FUTEBOL = "359e1e0ab654e3eb56c7cec930de5d3e"
TOKEN_TELEGRAM = "8856369868:AAGjBMrFLZRTMGA_XZpPxB3bGGRX48ErXFc"
CHAT_ID = "805165304"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    sys.exit(1)

robo_ativo = False
LIGAS_PERMITIDAS = ["brasileirao", "libertadores", "copa do brasil", "serie a", "premier league"]
client = Groq(api_key=GROQ_API_KEY)

async def analisar_ia(dados):
    prompt = f"Analise este jogo: {dados}. Forneça APENAS: 1. Mercado ideal, 2. Probabilidade (%), 3. Motivo. Seja técnico."
    try:
        completion = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192")
        return completion.choices[0].message.content
    except Exception:
        return "Erro ao gerar análise."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global robo_ativo
    robo_ativo = True
    await update.message.reply_text("✅ Robô LIGADO!")
    # Inicia o monitoramento se já não estiver rodando
    asyncio.create_task(monitorar_jogos(context.application.bot))

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global robo_ativo
    robo_ativo = False
    await update.message.reply_text("⛔ Robô DESLIGADO!")

async def monitorar_jogos(bot):
    global robo_ativo
    while robo_ativo:
        try:
            tz = pytz.timezone('America/Sao_Paulo')
            hoje = datetime.now(tz).strftime('%Y-%m-%d')
            url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"
            resp = requests.get(url, headers={'x-apisports-key': API_KEY_FUTEBOL}).json()
            
            for j in resp.get('response', []):
                if any(fav in j['league']['name'].lower() for fav in LIGAS_PERMITIDAS) and j['fixture']['status']['short'] == 'NS':
                    info = f"{j['teams']['home']['name']} vs {j['teams']['away']['name']} (Liga: {j['league']['name']})"
                    analise = await analisar_ia(info)
                    # USANDO PARSE_MODE HTML PARA EVITAR ERROS DE CARACTERES
                    texto = f"<b>🎯 SINAL DE ENTRADA</b>\n\n{analise}"
                    await bot.send_message(chat_id=CHAT_ID, text=texto, parse_mode='HTML')
                    await asyncio.sleep(10)
            await asyncio.sleep(1800)
        except Exception as e:
            print(f"Erro no loop: {e}")
            await asyncio.sleep(60)

if __name__ == '__main__':
    # Usando o novo método de builder sem get_event_loop
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.run_polling()
