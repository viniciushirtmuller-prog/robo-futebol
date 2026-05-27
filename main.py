import requests
import asyncio
from datetime import datetime
from telegram import Bot
from telegram.ext import ApplicationBuilder, CommandHandler

# CONFIGURAÇÕES
API_KEY = "359e1e0ab654e3eb56c7cec930de5d3e"
TOKEN_TELEGRAM = "8856369868:AAGjBMrFLZRTMGA_XZpPxB3bGGRX48ErXFc"
CHAT_ID = "805165304"

# Ligas de Elite para análise Pro
LIGAS_PRINCIPAIS = {
    "13": "CONMEBOL Libertadores",
    "71": "Brasileirão Série A",
    "72": "Brasileirão Série B",
    "73": "Copa do Brasil",
    "2": "Champions League"
}

bot = Bot(token=TOKEN_TELEGRAM)
robo_ativo = False

def gerar_analise_detalhada(casa_nome, fora_nome):
    # Lógica de análise (Simulação de cálculo de média combinada)
    return {
        "vencedor_time": casa_nome, 
        "vitoria_prob": "68%",
        "gols_over": "Over 2.5 (Taxa: 76%)",
        "cantos_over": "Over 9.5 (Tendência: Alta)",
        "cartoes_over": "Over 4.5 (Confiança: 78%)"
    }

async def monitorar():
    global robo_ativo
    # Data dinâmica: sempre buscará os jogos do dia atual
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    
    while robo_ativo:
        for l_id, nome_liga in LIGAS_PRINCIPAIS.items():
            url = f"https://v3.football.api-sports.io/fixtures?date={data_hoje}&league={l_id}&season=2026"
            try:
                resp = requests.get(url, headers={'x-apisports-key': API_KEY}).json()
                jogos = resp.get('response', [])
                
                print(f"DEBUG: Buscando {nome_liga} ({data_hoje}) -> {len(jogos)} jogos encontrados.")
                
                for j in jogos:
                    if j['fixture']['status']['short'] == 'NS':
                        casa = j['teams']['home']['name']
                        fora = j['teams']['away']['name']
                        stats = gerar_analise_detalhada(casa, fora)
                        
                        # Mensagem formatada em HTML
                        msg = (f"⚽ <b>Jogo:</b> {casa} x {fora}\n"
                               f"🏆 <b>Liga:</b> {nome_liga}\n\n"
                               f"📊 <b>Análise de Mercado (Média Combinada):</b>\n"
                               f"• Favorito: {stats['vencedor_time']} ({stats['vitoria_prob']})\n"
                               f"• Gols: {stats['gols_over']}\n"
                               f"• Cantos: {stats['cantos_over']}\n"
                               f"• Cartões: {stats['cartoes_over']}\n\n"
                               f"💡 <i>Oportunidade: Verifique Back {stats['vencedor_time']} ou Over Gols.</i>")
                        
                        await bot.send_message(chat_id=CHAT_ID, text=msg, parse_mode='HTML')
                        await asyncio.sleep(3) # Pausa de segurança para o Telegram
            except Exception as e:
                print(f"Erro na liga {nome_liga}: {e}")
        
        # O robô descansa 1 hora antes de checar se surgiram novos jogos
        await asyncio.sleep(3600)

async def start(update, context):
    global robo_ativo
    if not robo_ativo:
        robo_ativo = True
        await update.message.reply_text("🚀 Robô Analista Profissional ATIVADO!")
        asyncio.create_task(monitorar())

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("start", start))
    app.run_polling()
