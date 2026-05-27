import requests
import asyncio
import os
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler

# CONFIGURAÇÕES
API_KEY = "359e1e0ab654e3eb56c7cec930de5d3e"
TOKEN_TELEGRAM = "8856369868:AAGjBMrFLZRTMGA_XZpPxB3bGGRX48ErXFc"
CHAT_ID = "805165304"
LIBERTADORES_ID = "13"

bot = Bot(token=TOKEN_TELEGRAM)
robo_ativo = False

def limpar_texto(texto):
    """Limpa caracteres que quebram o HTML do Telegram."""
    return str(texto).replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")

async def monitorar_libertadores():
    global robo_ativo
    while robo_ativo:
        try:
            # Busca jogos de hoje para o ID da Libertadores (13)
            url = f"https://v3.football.api-sports.io/fixtures?date=2026-05-26&league={LIBERTADORES_ID}&season=2026"
            headers = {'x-apisports-key': API_KEY}
            resp = requests.get(url, headers=headers).json()
            
            jogos = resp.get('response', [])
            if not jogos:
                await bot.send_message(chat_id=CHAT_ID, text="Nenhum jogo da Libertadores hoje.")
            
            for j in jogos:
                if j['fixture']['status']['short'] == 'NS':
                    casa = limpar_texto(j['teams']['home']['name'])
                    fora = limpar_texto(j['teams']['away']['name'])
                    
                    texto = f"<b>⚽ Jogo:</b> {casa} x {fora}\n<i>Status: Aguardando início.</i>"
                    await bot.send_message(chat_id=CHAT_ID, text=texto, parse_mode='HTML')
                    await asyncio.sleep(5)
            
            await asyncio.sleep(3600) # Espera 1 hora
        except Exception as e:
            print(f"Erro no loop: {e}")
            await asyncio.sleep(60)

async def start(update, context):
    global robo_ativo
    if not robo_ativo:
        robo_ativo = True
        await update.message.reply_text("✅ Robô Libertadores ATIVO!")
        asyncio.create_task(monitorar_libertadores())

async def stop(update, context):
    global robo_ativo
    robo_ativo = False
    await update.message.reply_text("⛔ Robô PARADO.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.run_polling()
