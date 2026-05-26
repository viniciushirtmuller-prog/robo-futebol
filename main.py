import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

API_KEY = "359e1e0ab654e3eb56c7cec930de5d3e"
TOKEN = "8856369868:AAGjBMrFLZRTMGA_XZpPxB3bGGRX48ErXFc"

def calcular_analise(shots, corners, cards):
    # Taxas baseadas em volume total
    gols_taxa = min(99, (shots / 20) * 100)
    canto_taxa = min(99, (corners / 10) * 100)
    cartao_taxa = min(99, (cards / 4) * 100)
    
    return (f"🎯 Gols: {gols_taxa:.0f}%\n"
            f"🚩 Cantos: {canto_taxa:.0f}%\n"
            f"🟨 Cartões: {cartao_taxa:.0f}%")

async def get_stats(id_jogo):
    url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={id_jogo}"
    try:
        resp = requests.get(url, headers={'x-apisports-key': API_KEY}, timeout=5).json()
        if not resp.get('response') or len(resp['response']) < 2: return 0, 0, 0
        
        casa = {s['type']: s['value'] for s in resp['response'][0]['statistics']}
        fora = {s['type']: s['value'] for s in resp['response'][1]['statistics']}
        
        s = int(casa.get('Total Shots', 0) or 0) + int(fora.get('Total Shots', 0) or 0)
        c = int(casa.get('Corner Kicks', 0) or 0) + int(fora.get('Corner Kicks', 0) or 0)
        ca = int(casa.get('Yellow Cards', 0) or 0) + int(fora.get('Yellow Cards', 0) or 0)
        return s, c, ca
    except:
        return 0, 0, 0

async def listar_jogos(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("📥 Carregando todos os jogos do dia... aguarde.")
    hoje = "2026-05-26"
    resp = requests.get(f"https://v3.football.api-sports.io/fixtures?date={hoje}", headers={'x-apisports-key': API_KEY}).json()
    
    jogos = resp.get('response', [])
    if not jogos:
        await update.message.reply_text("Nenhum jogo encontrado para hoje.")
        return

    bloco_mensagem = ""
    contador = 0
    total_jogos = len(jogos)

    for j in jogos:
        stats = await get_stats(j['fixture']['id'])
        resumo = calcular_analise(*stats)
        
        bloco_mensagem += f"⚽ *{j['teams']['home']['name']} x {j['teams']['away']['name']}*\n{resumo}\n\n"
        contador += 1
        
        # Envia bloco a cada 5 jogos ou se for o último jogo da lista
        if contador % 5 == 0 or contador == total_jogos:
            await update.message.reply_text(bloco_mensagem, parse_mode='Markdown')
            bloco_mensagem = ""

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("jogos", listar_jogos))
    app.add_handler(CommandHandler("analisar", listar_jogos))
    print("Robô em modo 'Tudo ou Nada' - Processando 100% dos jogos.")
    app.run_polling()
