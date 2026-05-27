import requests
import os
from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

API_KEY_FUTEBOL = "359e1e0ab654e3eb56c7cec930de5d3e"

async def debug_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Fuso horário de Brasília
    tz = pytz.timezone('America/Sao_Paulo')
    hoje = datetime.now(tz).strftime('%Y-%m-%d')
    url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"
    
    # Faz a requisição
    headers = {'x-apisports-key': API_KEY_FUTEBOL}
    resposta = requests.get(url, headers=headers).json()
    
    # Pega apenas os nomes dos times para não poluir o chat
    jogos = []
    for j in resposta.get('response', []):
        nome = f"{j['teams']['home']['name']} vs {j['teams']['away']['name']}"
        jogos.append(nome)
    
    # Envia o resultado
    if not jogos:
        await update.message.reply_text("A API retornou VAZIA para hoje. Verifique se seu plano está ativo ou se a data está correta.")
    else:
        await update.message.reply_text(f"Jogos encontrados na API hoje:\n" + "\n".join(jogos))

if __name__ == '__main__':
    # (Mantenha o resto da inicialização do seu bot aqui)
    app = ApplicationBuilder().token("8856369868:AAGjBMrFLZRTMGA_XZpPxB3bGGRX48ErXFc").build()
    app.add_handler(CommandHandler("debug", debug_api))
    app.run_polling()
