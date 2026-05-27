import requests
import asyncio
import os
from datetime import datetime
import pytz
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# CONFIGURAÇÕES
API_KEY_FUTEBOL = "359e1e0ab654e3eb56c7cec930de5d3e"
TOKEN_TELEGRAM = "8856369868:AAGjBMrFLZRTMGA_XZpPxB3bGGRX48ErXFc"
CHAT_ID = "805165304"

robo_ativo = False
LIGAS_PERMITIDAS = ["brasileirao", "libertadores", "copa do brasil", "serie a", "premier league"]

async def calcular_probabilidades(home_id, away_id):
    """Calcula chances baseadas nos últimos 5 jogos de cada time."""
    url = f"https://v3.football.api-sports.io/fixtures/headtohead?h2h={home_id}-{away_id}&last=5"
    headers = {'x-apisports-key': API_KEY_FUTEBOL}
    try:
        data = requests.get(url, headers=headers).json()
        h2h = data.get('response', [])
        
        # Lógica simples de cálculo: % de vitórias no histórico
        vitorias_home = sum(1 for j in h2h if j['teams']['home']['id'] == home_id and j['goals']['home'] > j['goals']['away'])
        total = len(h2h) if len(h2h) > 0 else 1
        
        prob_home = (vitorias_home / total) * 100
        return f"📊 <b>Estatísticas (H2H):</b>\n- Vitória Casa: {prob_home:.1f}%\n- Chance de Empate/Fora: {100-prob_home:.1f}%\n- <b>Sugestão de Mercado:</b> Ambas Marcam ou Over 1.5 Gols."
    except:
        return "Estatísticas insuficientes para este confronto."

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global robo_ativo
    robo_ativo = True
    await update.message.reply_text("✅ <b>Robô de Probabilidades ATIVO!</b> Monitorando jogos...")
    asyncio.create_task(monitorar_probabilidades(context.application.bot))

async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global robo_ativo
    robo_ativo = False
    await update.message.reply_text("⛔ <b>Robô PARADO.</b>")

async def monitorar_probabilidades(bot):
    global robo_ativo
    while robo_ativo:
        try:
            tz = pytz.timezone('America/Sao_Paulo')
            hoje = datetime.now(tz).strftime('%Y-%m-%d')
            url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"
            resp = requests.get(url, headers={'x-apisports-key': API_KEY_FUTEBOL}).json()
            
            for j in resp.get('response', []):
                if any(fav in j['league']['name'].lower() for fav in LIGAS_PERMITIDAS) and j['fixture']['status']['short'] == 'NS':
                    home_id = j['teams']['home']['id']
                    away_id = j['teams']['away']['id']
                    
                    prob = await calcular_probabilidades(home_id, away_id)
                    texto = f"⚽ <b>{j['teams']['home']['name']} x {j['teams']['away']['name']}</b>\nLiga: {j['league']['name']}\n\n{prob}"
                    
                    await bot.send_message(chat_id=CHAT_ID, text=texto, parse_mode='HTML')
                    await asyncio.sleep(10)
            await asyncio.sleep(3600)
        except Exception as e:
            print(f"Erro: {e}")
            await asyncio.sleep(60)

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("stop", stop))
    app.run_polling()
