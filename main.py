import requests
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from groq import Groq

# CONFIGURAÇÕES
API_KEY_FUTEBOL = "359e1e0ab654e3eb56c7cec930de5d3e"
TOKEN_TELEGRAM = "8856369868:AAGjBMrFLZRTMGA_XZpPxB3bGGRX48ErXFc"

# A chave será lida da Railway (Variáveis de Ambiente)
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = Groq(api_key=GROQ_API_KEY)

async def analisar_com_ia(dados):
    prompt = f"""
    Analise estes dados de um jogo de futebol: {dados}.
    Dê uma recomendação de aposta curta e direta (Gols, Cantos ou Cartões) 
    com uma justificativa baseada nos números fornecidos. 
    Se os números forem muito baixos, diga que não há valor.
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Erro ao consultar IA: {str(e)}"

async def comando_analisar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Digite o nome do time. Ex: /analisar flamengo")
        return
        
    time_busca = " ".join(context.args).lower()
    await update.message.reply_text(f"🤖 Analisando {time_busca}...")
    
    hoje = "2026-05-26"
    url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"
    
    resp = requests.get(url, headers={'x-apisports-key': API_KEY_FUTEBOL}).json()
    
    encontrou = False
    for j in resp.get('response', []):
        home = j['teams']['home']['name'].lower()
        away = j['teams']['away']['name'].lower()
        
        if time_busca in home or time_busca in away:
            id_jogo = j['fixture']['id']
            stat_url = f"https://v3.football.api-sports.io/fixtures/statistics?fixture={id_jogo}"
            stats = requests.get(stat_url, headers={'x-apisports-key': API_KEY_FUTEBOL}).json()
            
            dados = f"{home.upper()} vs {away.upper()}. Estatísticas: {stats.get('response')}"
            
            analise = await analisar_com_ia(dados)
            await update.message.reply_text(f"⚽ *{home.upper()} x {away.upper()}*\n\n{analise}", parse_mode='Markdown')
            encontrou = True
            break
            
    if not encontrou:
        await update.message.reply_text("Jogo não encontrado ou sem estatísticas hoje.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("analisar", comando_analisar))
    app.add_handler(CommandHandler("jogos", comando_analisar))
    app.add_handler(CommandHandler("bingos", comando_analisar))
    print("Robô operacional com IA!")
    app.run_polling()
