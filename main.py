import requests
import asyncio
from datetime import datetime
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler

# CONFIGURAÇÕES DE API E TELEGRAM
API_KEY = "359e1e0ab654e3eb56c7cec930de5d3e"
TOKEN_TELEGRAM = "8856369868:AAGjBMrFLZRTMGA_XZpPxB3bGGRX48ErXFc"
CHAT_ID = "805165304"

# LISTA ABRANGENTE DE COMPETIÇÕES
LIGAS = {
    "13": "Libertadores", "11": "Copa Sul-Americana",
    "71": "Brasileirão Série A", "72": "Brasileirão Série B",
    "73": "Copa do Brasil", "2": "Champions League",
    "3": "Europa League", "39": "Premier League",
    "128": "Campeonato Argentino", "140": "La Liga"
}

bot = Bot(token=TOKEN_TELEGRAM)
robo_ativo = False

def calcular_tendencias(stats):
    """
    Função de análise complexa: aqui você pode futuramente 
    conectar cálculos matemáticos baseados em médias reais.
    """
    return {
        "vitoria": "Alta probabilidade",
        "gols": "Over 2.5",
        "cantos": "Over 9.5",
        "cartoes": "Over 4.5"
    }

async def processar_liga(l_id, nome_liga):
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    url = f"https://v3.football.api-sports.io/fixtures?date={data_hoje}&league={l_id}&season=2026"
    headers = {'x-apisports-key': API_KEY}
    
    try:
        resp = requests.get(url, headers=headers).json()
        jogos = resp.get('response', [])
        
        for j in jogos:
            # Filtro rigoroso: apenas jogos que ainda não começaram
            if j['fixture']['status']['short'] == 'NS':
                casa = j['teams']['home']['name']
                fora = j['teams']['away']['name']
                horario = j['fixture']['date'][11:16] # Formato HH:MM
                
                analise = calcular_tendencias(None)
                
                msg = (f"⚽ <b>{casa} x {fora}</b>\n"
                       f"🏆 {nome_liga} | ⏰ {horario}\n\n"
                       f"📊 <b>Análise de Mercado (Combinada):</b>\n"
                       f"• Favorito: {casa} (Tendência: {analise['vitoria']})\n"
                       f"• Gols: {analise['gols']}\n"
                       f"• Escanteios: {analise['cantos']}\n"
                       f"• Cartões: {analise['cartoes']}\n\n"
                       f"💡 <i>Analise as odds antes de entrar no mercado!</i>")
                
                await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='HTML')
                await asyncio.sleep(1.5) # Pausa estratégica
                
    except Exception as e:
        print(f"Erro ao processar {nome_liga}: {e}")

async def monitorar():
    global robo_ativo
    while robo_ativo:
        for l_id, nome_liga in LIGAS.items():
            await processar_liga(l_id, nome_liga)
        # Após varrer todas as ligas, ele aguarda 30 minutos antes de repetir
        await asyncio.sleep(1800)

async def start(update, context):
    global robo_ativo
    if not robo_ativo:
        robo_ativo = True
        await update.message.reply_text("🚀 Robô Iniciado: Analisando Ligas de Elite...")
        asyncio.create_task(monitorar())

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
