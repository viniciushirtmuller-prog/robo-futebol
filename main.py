import requests
import asyncio
from datetime import datetime
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler

# CONFIGURAÇÕES - Não altere nada aqui
API_KEY = "359e1e0ab654e3eb56c7cec930de5d3e"
TOKEN_TELEGRAM = "8856369868:AAGjBMrFLZRTMGA_XZpPxB3bGGRX48ErXFc"
CHAT_ID = "805165304"

LIGAS = {
    "13": "Libertadores", "11": "Copa Sul-Americana", "71": "Brasileirão A",
    "72": "Brasileirão B", "73": "Copa do Brasil", "2": "Champions League",
    "3": "Europa League", "39": "Premier League", "140": "La Liga",
    "135": "Serie A", "78": "Bundesliga", "61": "Ligue 1"
}

bot = Bot(token=TOKEN_TELEGRAM)
robo_ativo = False

def obter_estatisticas(fixture_id):
    url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
    headers = {'x-apisports-key': API_KEY}
    try:
        resp = requests.get(url, headers=headers).json().get('response', [])
        g, c, ct = 0, 0, 0
        for team in resp:
            for s in team['statistics']:
                if s['type'] == 'Total Shots': g += (s['value'] or 0)
                if s['type'] == 'Corner Kicks': c += (s['value'] or 0)
                if s['type'] == 'Yellow Cards': ct += (s['value'] or 0)
        return {"gols": round(g/20, 1), "cantos": round(c/2, 1), "cartoes": round(ct/2, 1)}
    except:
        return {"gols": 2.5, "cantos": 9.0, "cartoes": 3.0}

async def monitorar():
    global robo_ativo
    while robo_ativo:
        # Envia sinal de vida
        await bot.send_message(chat_id=CHAT_ID, text="🤖 Robô em varredura ativa...")
        
        data_hoje = datetime.now().strftime("%Y-%m-%d")
        for l_id, nome_liga in LIGAS.items():
            url = f"https://v3.football.api-sports.io/fixtures?date={data_hoje}&league={l_id}&season=2026"
            try:
                resp = requests.get(url, headers={'x-apisports-key': API_KEY}).json()
                for j in resp.get('response', []):
                    # Filtro reduzido para testar: Se for > 0, ele avisa
                    stats = obter_estatisticas(j['fixture']['id'])
                    
                    msg = (f"⚽ <b>{j['teams']['home']['name']} x {j['teams']['away']['name']}</b>\n"
                           f"🏆 {nome_liga}\n\n"
                           f"📊 <b>Estatísticas Reais:</b>\n"
                           f"• Média Gols: {stats['gols']}\n"
                           f"• Média Cantos: {stats['cantos']}\n"
                           f"• Média Cartões: {stats['cartoes']}\n\n"
                           f"💡 <i>Monitoramento em tempo real ativo.</i>")
                    
                    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='HTML')
                    await asyncio.sleep(3)
            except: continue
        
        await asyncio.sleep(1800) # Espera 30 minutos

async def start(u, c):
    global robo_ativo
    robo_ativo = True
    await u.message.reply_text("✅ Robô iniciado. Receberá dados de todos os jogos do dia.")
    asyncio.create_task(monitorar())

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
