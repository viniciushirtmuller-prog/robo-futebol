import requests
import asyncio
import os
from datetime import datetime
import pytz
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler

# CONFIGURAÇÕES
API_KEY_FUTEBOL = "359e1e0ab654e3eb56c7cec930de5d3e"
TOKEN_TELEGRAM = "8856369868:AAGjBMrFLZRTMGA_XZpPxB3bGGRX48ErXFc"
CHAT_ID = "805165304"
LIBERTADORES_ID = "13" # ID confirmado por você

robo_ativo = False
bot = Bot(token=TOKEN_TELEGRAM)

def proteger_texto(texto):
    return str(texto).replace("<", "&lt;").replace(">", "&gt;").replace("&", "&amp;")

async def monitorar_libertadores():
    global robo_ativo
    while robo_ativo:
        try:
            tz = pytz.timezone('America/Sao_Paulo')
            hoje = datetime.now(tz).strftime('%Y-%m-%d')
            # Busca jogos de HOJE da Libertadores
            url = f"https://v3.football.api-sports.io/fixtures?date={hoje}&league={LIBERTADORES_ID}&season=2026"
            headers = {'x-apisports-key': API_KEY_FUTEBOL}
            
            resp = requests.get(url, headers=headers).json()
            
            # Verifica se existem jogos
            if 'response' in resp and len(resp['response']) > 0:
                for j in resp['response']:
                    if j['fixture']['status']['short'] == 'NS':
                        casa = proteger_texto(j['teams']['home']['name'])
                        fora = proteger_texto(j['teams']['away']['name'])
                        
                        texto = (f"⚽ <b>LIBERTADORES HOJE</b>\n\n"
                                 f"<b>{casa} x {fora}</b>\n"
                                 f"<i>Status: Aguardando início.</i>")
                        
                        await bot.send_message(chat_id=CHAT_ID, text=texto, parse_mode='HTML')
                        await asyncio.sleep(5)
            
            # Aguarda 1 hora antes da próxima verificação
            await asyncio.sleep(3600)
        except Exception as e:
            print(f"Erro no monitoramento: {e}")
            await asyncio.sleep(60)

async def start(update, context):
    global robo_ativo
    robo_ativo = True
    await update.message.reply_text("✅ <b>Robô Libertadores Ativo!</b> Monitorando os jogos de hoje.")
    asyncio.create_task(monitorar_libertadores())

async def stop(update, context):
    global robo_ativo
    robo_ativo = False
    await update.message.reply_text("⛔ <b>Robô Desativado.</b>")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.run_polling()
