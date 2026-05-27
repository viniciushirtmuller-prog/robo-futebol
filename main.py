import requests
import asyncio
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler

# CONFIGURAÇÕES
API_KEY = "359e1e0ab654e3eb56c7cec930de5d3e"
TOKEN_TELEGRAM = "8856369868:AAGjBMrFLZRTMGA_XZpPxB3bGGRX48ErXFc"
CHAT_ID = "805165304"

# Ligas Selecionadas (IDs mapeados nos logs)
LIGAS_PRINCIPAIS = {
    "13": "CONMEBOL Libertadores",
    "71": "Brasileirão Série A",
    "72": "Brasileirão Série B",
    "73": "Copa do Brasil",
    "2": "Champions League"
}

bot = Bot(token=TOKEN_TELEGRAM)
robo_ativo = False

def formatar_analise(casa, fora, stats):
    # Lógica de análise combinada (média dos dois times)
    # Exemplo simplificado de cálculo:
    gols_total = (stats['home_avg_goals'] + stats['away_avg_goals'])
    cantos_total = (stats['home_avg_corners'] + stats['away_avg_corners'])
    cards_total = (stats['home_avg_cards'] + stats['away_avg_cards'])

    msg = (f"⚽ <b>{casa} x {fora}</b>\n"
           f"📊 <b>Análise de Mercado (Média Combinada):</b>\n"
           f"• Gols: {'Over 2.5' if gols_total > 2.8 else 'Under 2.5'} (Média: {gols_total:.1f})\n"
           f"• Cantos: {'Over 9.5' if cantos_total > 9.5 else 'Under 9.5'} (Média: {cantos_total:.1f})\n"
           f"• Cartões: {'Over 4.5' if cards_total > 4.0 else 'Under 4.5'} (Média: {cards_total:.1f})\n\n"
           f"💡 <i>Sugestão: Focar em mercados com probabilidade > 70%.</i>")
    return msg

async def buscar_estatisticas(fixture_id):
    # Simulando dados da API Pro para exemplo (substituir por chamada real a v3.football.api-sports.io/fixtures/statistics)
    return {
        'home_avg_goals': 1.6, 'away_avg_goals': 1.5,
        'home_avg_corners': 5.2, 'away_avg_corners': 5.5,
        'home_avg_cards': 2.1, 'away_avg_cards': 2.3
    }

async def monitorar():
    global robo_ativo
    while robo_ativo:
        for l_id, nome_liga in LIGAS_PRINCIPAIS.items():
            url = f"https://v3.football.api-sports.io/fixtures?date=2026-05-26&league={l_id}&season=2026"
            try:
                resp = requests.get(url, headers={'x-apisports-key': API_KEY}).json()
                for j in resp.get('response', []):
                    if j['fixture']['status']['short'] == 'NS':
                        stats = await buscar_estatisticas(j['fixture']['id'])
                        texto = formatar_analise(j['teams']['home']['name'], j['teams']['away']['name'], stats)
                        await bot.send_message(chat_id=CHAT_ID, text=texto, parse_mode='HTML')
                        await asyncio.sleep(3)
            except Exception as e:
                print(f"Erro na liga {nome_liga}: {e}")
        await asyncio.sleep(3600) # Pausa de 1 hora entre varreduras

async def start(update, context):
    global robo_ativo
    if not robo_ativo:
        robo_ativo = True
        await update.message.reply_text("🚀 Robô Profissional ATIVADO!")
        asyncio.create_task(monitorar())

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
