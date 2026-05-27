import requests
from datetime import datetime, timezone
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

API_KEY = "359e1e0ab654e3eb56c7cec930de5d3e"
TOKEN = "8856369868:AAGjBMrFLZRTMGA_XZpPxB3bGGRX48ErXFc"

def gerar_analise(s, c, ca):
    # Logica de recomendação
    recom = "Aguardando mais dados"
    if s > 20: recom = "Gols: Over 2.5"
    elif c > 8: recom = "Cantos: Mais de 9.5"
    elif ca > 3: recom = "Cartões: Mais de 3.5"
    
    return (f"📊 Taxa de Confiança: {(s+c+ca)/2}% \n"
            f"✅ Entrada Sugerida: *{recom}*\n"
            f"🎯 Total Chutes/Cantos/Cartões: {s}/{c}/{ca}")

async def get_jogos_filtrados(query=None):
    hoje = datetime.now().strftime('%Y-%m-%d')
    url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"
    resp = requests.get(url, headers={'x-apisports-key': API_KEY}).json()
    
    lista = []
    agora = datetime.now(timezone.utc)
    
    for j in resp.get('response', []):
        data_jogo = datetime.strptime(j['fixture']['date'], '%Y-%m-%dT%H:%M:%S+00:00').replace(tzinfo=timezone.utc)
        
        # Filtra apenas jogos que ainda vão começar
        if data_jogo > agora:
            if query and query.lower() not in j['teams']['home']['name'].lower() and query.lower() not in j['teams']['away']['name'].lower():
                continue
            
            # Pega estatísticas
            id_jogo = j['fixture']['id']
            stat_url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={id_jogo}"
            stats = requests.get(stat_url, headers={'x-apisports-key': API_KEY}).json().get('response', [])
            
            s, c, ca = 0, 0, 0
            if len(stats) >= 2:
                casa = {st['type']: st['value'] for st in stats[0]['statistics']}
                fora = {st['type']: st['value'] for st in stats[1]['statistics']}
                s = int(casa.get('Total Shots', 0) or 0) + int(fora.get('Total Shots', 0) or 0)
                c = int(casa.get('Corner Kicks', 0) or 0) + int(fora.get('Corner Kicks', 0) or 0)
                ca = int(casa.get('Yellow Cards', 0) or 0) + int(fora.get('Yellow Cards', 0) or 0)
            
            lista.append(f"⚽ {j['teams']['home']['name']} x {j['teams']['away']['name']}\n{gerar_analise(s, c, ca)}")
    return lista

async def cmd_analisar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = " ".join(context.args)
    resultados = await get_jogos_filtrados(query)
    if not resultados: await update.message.reply_text("Nenhum jogo futuro encontrado.")
    else: await update.message.reply_text("\n\n".join(resultados), parse_mode='Markdown')

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("jogos", cmd_analisar)) # /jogos
    app.add_handler(CommandHandler("bingos", cmd_analisar)) # /bingos
    app.add_handler(CommandHandler("analisar", cmd_analisar)) # /analisar time
    print("Robô corrigido e pronto.")
    app.run_polling()
