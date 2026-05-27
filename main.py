import requests
import asyncio
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler

API_KEY = "359e1e0ab654e3eb56c7cec930de5d3e"
TOKEN_TELEGRAM = "8856369868:AAGjBMrFLZRTMGA_XZpPxB3bGGRX48ErXFc"
CHAT_ID = "805165304"

# IDs das Ligas Principais (Brasileirão, Libertadores, Champions, etc)
LIGAS_PRINCIPAIS = {"71": "Brasileirão", "13": "Libertadores", "2": "Champions League"}

bot = Bot(token=TOKEN_TELEGRAM)
robo_ativo = False

async def calcular_analise(fixture_id, liga_id):
    headers = {'x-apisports-key': API_KEY}
    # Busca estatísticas do jogo
    stats_url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
    data = requests.get(stats_url, headers=headers).json()
    
    # Simulação de análise baseada em dados Pro
    return "📈 <b>Probabilidade de Vitoria:</b> 65%\n🎯 <b>Tendência:</b> Over 2.5 gols\n⚠️ <b>Confiança:</b> Alta"

async def monitorar():
    global robo_ativo
    while robo_ativo:
        for l_id in LIGAS_PRINCIPAIS:
            url = f"https://v3.football.api-sports.io/fixtures?date=2026-05-26&league={l_id}&season=2026"
            resp = requests.get(url, headers={'x-apisports-key': API_KEY}).json()
            
            for j in resp.get('response', []):
                if j['fixture']['status']['short'] == 'NS':
                    analise = await calcular_analise(j['fixture']['id'], l_id)
                    texto = (f"⚽ <b>{j['teams']['home']['name']} x {j['teams']['away']['name']}</b>\n"
                             f"🏆 {LIGAS_PRINCIPAIS[l_id]}\n\n"
                             f"{analise}")
                    await bot.send_message(chat_id=CHAT_ID, text=texto, parse_mode='HTML')
                    await asyncio.sleep(5)
        await asyncio.sleep(3600)

async def start(update, context):
    global robo_ativo
    robo_ativo = True
    asyncio.create_task(monitorar())
    await update.message.reply_text("✅ Robô Analista Pro ATIVO!")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
