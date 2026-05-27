import requests
import asyncio
import os
from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from groq import Groq

# CONFIGURAÇÕES
API_KEY_FUTEBOL = "359e1e0ab654e3eb56c7cec930de5d3e"
TOKEN_TELEGRAM = "8856369868:AAGjBMrFLZRTMGA_XZpPxB3bGGRX48ErXFc"
CHAT_ID = "805165304"
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# Variável de controle
robo_ativo = False
LIGAS_PERMITIDAS = ["brasileirao", "libertadores", "copa do brasil", "serie a", "premier league"]

client = Groq(api_key=GROQ_API_KEY)

async def analisar_ia(dados):
    prompt = f"Analise este jogo: {dados}. Forneça APENAS: 1. Mercado ideal (ex: Vitoria Casa, Over 2.5), 2. Probabilidade (%), 3. Motivo da entrada. Seja técnico e profissional."
    completion = client.chat.completions.create(messages=[{"role": "user", "content": prompt}], model="llama3-8b-8192")
    return completion.choices[0].message.content

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global robo_ativo
    robo_ativo = True
    await update.message.reply_text("✅ Robô LIGADO! Monitorando jogos de hoje...")
    asyncio.create_task(monitorar_jogos(context.application.bot))

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global robo_ativo
    robo_ativo = False
    await update.message.reply_text("⛔ Robô DESLIGADO! Parando análises.")

async def monitorar_jogos(bot):
    global robo_ativo
    while robo_ativo:
        try:
            tz = pytz.timezone('America/Sao_Paulo')
            hoje = datetime.now(tz).strftime('%Y-%m-%d')
            url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"
            resp = requests.get(url, headers={'x-apisports-key': API_KEY_FUTEBOL}).json()
            
            for j in resp.get('response', []):
                # Apenas jogos que NÃO começaram (NS)
                if any(fav in j['league']['name'].lower() for fav in LIGAS_PERMITIDAS) and j['fixture']['status']['short'] == 'NS':
                    info = f"{j['teams']['home']['name']} vs {j['teams']['away']['name']} (Liga: {j['league']['name']})"
                    analise = await analisar_ia(info)
                    await bot.send_message(chat_id=CHAT_ID, text=f"🎯 *SINAL DE ENTRADA*\n\n{analise}", parse_mode='Markdown')
                    await asyncio.sleep(60) # Pausa curta
            
            await asyncio.sleep(1800) # Checa a cada 30 min
        except Exception as e:
            print(f"Erro no loop: {e}")
            await asyncio.sleep(60)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.run_polling()
