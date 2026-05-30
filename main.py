import os
import requests
import asyncio
from datetime import datetime
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler
from groq import Groq

# CONFIGURAÇÕES FIXAS
API_KEY = ""
TOKEN_TELEGRAM = ":AAGjBMrFLZRTMGA_XZpPxB3bGGRX48ErXFc"
CHAT_ID = ""
GROQ_API = "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"

LIGAS = {
    "13": "Libertadores", "11": "Copa Sul-Americana", "71": "Brasileirão A",
    "72": "Brasileirão B", "73": "Copa do Brasil", "2": "Champions League",
    "3": "Europa League", "39": "Premier League", "140": "La Liga",
    "135": "Serie A", "78": "Bundesliga", "61": "Ligue 1"
}

bot = Bot(token=TOKEN_TELEGRAM)
groq_client = Groq(api_key=GROQ_API)

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

def gerar_analise_ia(stats, casa, fora, liga):
    prompt = f"Analise o jogo {casa} x {fora} da liga {liga}. Dados: Média de Gols {stats['gols']}, Cantos {stats['cantos']}, Cartões {stats['cartoes']}. Escreva uma análise técnica e curta para apostas."
    try:
        chat = groq_client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )
        return chat.choices[0].message.content
    except:
        return "Análise em processamento."

async def monitorar():
    while True:
        data_hoje = datetime.now().strftime("%Y-%m-%d")
        for l_id, nome_liga in LIGAS.items():
            url = f"https://v3.football.api-sports.io/fixtures?date={data_hoje}&league={l_id}&season=2026"
            try:
                resp = requests.get(url, headers={'x-apisports-key': API_KEY}).json()
                for j in resp.get('response', []):
                    status = j['fixture']['status']['short']
                    
                    # FILTRO: Só processa se estiver AO VIVO (1H, 2H) ou para começar (NS)
                    if status in ['1H', '2H', 'NS']:
                        stats = obter_estatisticas(j['fixture']['id'])
                        analise = gerar_analise_ia(stats, j['teams']['home']['name'], j['teams']['away']['name'], nome_liga)
                        
                        msg = (f"⚽ <b>{j['teams']['home']['name']} x {j['teams']['away']['name']}</b>\n"
                               f"🏆 {nome_liga} | Status: {status}\n\n"
                               f"🤖 <b>Análise da IA:</b>\n{analise}\n\n"
                               f"📊 <i>Dados: Gols {stats['gols']} | Cantos {stats['cantos']}</i>")
                        
                        await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='HTML')
                        await asyncio.sleep(8) # Tempo para não ser bloqueado pela API
            except: continue
        await asyncio.sleep(1800) # Espera 30 min antes de checar todas as ligas novamente

async def start(u, c):
    await u.message.reply_text("🚀 Robô Inteligente ATIVADO. Monitorando apenas jogos ativos.")
    asyncio.create_task(monitorar())

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
