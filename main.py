# Adicione este comando para debugar
async def debug_api(update: Update, context: ContextTypes.DEFAULT_TYPE):
    hoje = datetime.now(pytz.timezone('America/Sao_Paulo')).strftime('%Y-%m-%d')
    url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"
    resp = requests.get(url, headers={'x-apisports-key': API_KEY_FUTEBOL}).json()
    
    # Mostra os 2 primeiros jogos encontrados no dia
    jogos = str(resp.get('response', [])[:2])
    await update.message.reply_text(f"Resposta da API: {jogos[:1000]}") # Limita o texto

# No seu app, adicione:
app.add_handler(CommandHandler("debug", debug_api))
