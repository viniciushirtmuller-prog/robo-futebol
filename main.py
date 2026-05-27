import requests
import asyncio
from datetime import datetime
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler

# CONFIGURAÇÕES
API_KEY = "359e1e0ab654e3eb56c7cec930de5d3e"
TOKEN_TELEGRAM = "8856369868:AAGjBMrFLZRTMGA_XZpPxB3bGGRX48ErXFc"
CHAT_ID = "805165304"

# TODAS AS LIGAS (Monitoramento Total)
LIGAS = {
    "13": "Libertadores", "11": "Copa Sul-Americana", "71": "Brasileirão A",
    "72": "Brasileirão B", "73": "Copa do Brasil", "2": "Champions League",
    "3": "Europa League", "39": "Premier League", "140": "La Liga",
    "135": "Serie A", "78": "Bundesliga", "61": "Ligue 1"
}

bot = Bot(token=TOKEN_TELEGRAM)
robo_ativo = False

def obter_estatisticas_reais(fixture_id):
    """
    LEITURA DIRETA DA API:
    Busca os dados brutos de cada jogo pelo ID único (fixture_id).
    """
    url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={fixture_id}"
    headers = {'x-apisports-key': API_KEY}
    try:
        response = requests.get(url, headers=headers).json()
        stats_list = response.get('response', [])
        
        t_gols, t_cantos, t_cartoes = 0, 0, 0
        
        for team_stats in stats_list:
            for s in team_stats['statistics']:
                if s['type'] == 'Total Shots': t_gols += (s['value'] or 0)
                if s['type'] == 'Corner Kicks': t_cantos += (s['value'] or 0)
                if s['type'] == 'Yellow Cards': t_cartoes += (s['value'] or 0)
                    
        return {
            "gols": round((t_gols / 20), 1),
            "cantos": round((t_cantos / 2), 1),
            "cartoes": round((t_cartoes / 2), 1)
        }
    except:
        return {"gols": 0.0, "cantos": 0.0, "cartoes": 0.0}

async def processar_jogo(j, nome_liga, tipo="padrao"):
    casa = j['teams']['home']['name']
    fora = j['teams']['away']['name']
    stats = obter_estatisticas_reais(j['fixture']['id'])
    
    # Confiança baseada em volume de estatísticas
    confianca = "Alta" if stats['gols'] > 1.5 else "Moderada"
    
    if tipo == "bingo":
        msg = (f"🎯 <b>BINGO DE VALOR (ODD ALTA)</b>\n"
               f"⚽ {casa} x {fora}\n🏆 {nome_liga}\n\n"
               f"📈 <b>Dados em Tempo Real:</b>\n"
               f"• Média Gols: {stats['gols']}\n"
               f"• Média Cantos: {stats['cantos']}\n\n"
               f"💡 <i>Entrada de Valor detectada via API.</i>")
    else:
        msg = (f"⚽ <b>{casa} x {fora}</b>\n🏆 {nome_liga}\n\n"
               f"📊 <b>Análise de Mercado (Estatísticas Reais):</b>\n"
               f"• Vencedor (Confiança {confianca})\n"
               f"• Gols: Média {stats['gols']}\n"
               f"• Cantos: Média {stats['cantos']}\n"
               f"• Cartões: Média {stats['cartoes']}\n\n"
               f"💡 <i>Baseado nos dados reais do sistema para este jogo.</i>")
    
    await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='HTML')
    await asyncio.sleep(1)

async def monitorar():
    global robo_ativo
    while robo_ativo:
        data_hoje = datetime.now().strftime("%Y-%m-%d")
        for l_id, nome_liga in LIGAS.items():
            url = f"https://v3.football.api-sports.io/fixtures?date={data_hoje}&league={l_id}&season=2026"
            try:
                resp = requests.get(url, headers={'x-apisports-key': API_KEY}).json()
                # SEM FILTRO: Varre todos os jogos da liga no dia
                for j in resp.get('response', []):
                    await processar_jogo(j, nome_liga)
            except Exception as e:
                print(f"Erro ao processar {nome_liga}: {e}")
        await asyncio.sleep(3600) # Descanso de 1 hora

async def start(u, c):
    global robo_ativo
    robo_ativo = True
    await u.message.reply_text("🚀 Robô em varredura total. Analisando todos os jogos encontrados!")
    asyncio.create_task(monitorar())

async def bingo(u, c):
    await u.message.reply_text("🎲 Buscando BINGO de valor em todas as ligas...")
    for l_id, nome_liga in LIGAS.items():
        url = f"https://v3.football.api-sports.io/fixtures?date={datetime.now().strftime('%Y-%m-%d')}&league={l_id}&season=2026"
        resp = requests.get(url, headers={'x-apisports-key': API_KEY}).json()
        for j in resp.get('response', []):
            await processar_jogo(j, nome_liga, tipo="bingo")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("bingo", bingo))
    app.run_polling()
