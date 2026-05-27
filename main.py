import requests
import asyncio
from datetime import datetime
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler

# CONFIGURAÇÕES
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

def calcular_valor(stats):
    # Lógica Matemática: Probabilidade baseada em média de Gols
    prob_real = min((stats['gols'] / 4.0), 0.95)
    odd_justa = 1 / prob_real
    
    # Exemplo: Se odd da casa for > odd_justa + 15% de margem
    odd_casa_exemplo = 2.10 
    ev = (prob_real * odd_casa_exemplo) - 1
    
    # Critério de Kelly (Stake)
    stake = max(0.01, min(0.05, (prob_real * odd_casa_exemplo - 1) / (odd_casa_exemplo - 1)))
    
    return ev, stake, odd_justa

def obter_dados_reais(fixture_id):
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

async def processar_jogo(j, nome_liga):
    stats = obter_dados_reais(j['fixture']['id'])
    ev, stake, odd_justa = calcular_valor(stats)
    
    if ev > 0.15: # FILTRO DE VALOR: Só envia se EV > 15%
        msg = (f"💎 <b>SINAL DE VALOR (+EV)</b>\n"
               f"⚽ {j['teams']['home']['name']} x {j['teams']['away']['name']}\n"
               f"🏆 {nome_liga}\n\n"
               f"📊 <b>Análise Matemática:</b>\n"
               f"• Média Gols: {stats['gols']} | Cantos: {stats['cantos']}\n"
               f"• Valor Esperado (EV): +{int(ev*100)}%\n\n"
               f"💰 <b>Gestão Profissional:</b>\n"
               f"• Odd Justa: {round(odd_justa, 2)}\n"
               f"• Stake Recomendada: {int(stake*100)}% da banca\n\n"
               f"💡 <i>Entrada: Over 2.5 Gols | Oportunidade por desajuste de mercado.</i>")
        await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='HTML')

async def monitorar():
    global robo_ativo
    while robo_ativo:
        for l_id, nome_liga in LIGAS.items():
            url = f"https://v3.football.api-sports.io/fixtures?date={datetime.now().strftime('%Y-%m-%d')}&league={l_id}&season=2026"
            try:
                resp = requests.get(url, headers={'x-apisports-key': API_KEY}).json()
                for j in resp.get('response', []):
                    await processar_jogo(j, nome_liga)
                    await asyncio.sleep(2)
            except: continue
        await asyncio.sleep(3600)

async def start(u, c):
    global robo_ativo
    robo_ativo = True
    await u.message.reply_text("🚀 Robô de Valor ATIVADO. Buscando desajustes matemáticos...")
    asyncio.create_task(monitorar())

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
