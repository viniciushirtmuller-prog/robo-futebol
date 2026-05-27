import requests
import os
import sys
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
from groq import Groq

# CONFIGURAÇÕES
API_KEY_FUTEBOL = "359e1e0ab654e3eb56c7cec930de5d3e"
TOKEN_TELEGRAM = "8856369868:AAGjBMrFLZRTMGA_XZpPxB3bGGRX48ErXFc"

# Carrega a chave de forma segura
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

if not GROQ_API_KEY:
    print("ERRO CRÍTICO: GROQ_API_KEY não configurada na Railway!")
    sys.exit(1) # Para o bot se não tiver chave

client = Groq(api_key=GROQ_API_KEY)

async def analisar_com_ia(dados):
    prompt = f"""
    Analise estes dados de um jogo de futebol: {dados}.
    Dê uma recomendação de aposta (Gols, Cantos ou Cartões) curta, direta e profissional. 
    Justifique com base nos números. Se os números forem baixos, informe que não há valor.
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[{"role": "user", "content": prompt}],
            model="llama3-8b-8192",
        )
        return chat_completion.choices[0].message.content
    except Exception as e:
        return f"Erro ao processar IA: {str(e)}"

async def comando_analisar(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Digite: /analisar [nome do time]")
        return
        
    time_busca = " ".join(context.args).lower()
    await update.message.reply_text(f"🤖 Analisando {time_busca}...")
    
    hoje = "2026-05-26"
    url = f"https://v3.football.api-sports.io/fixtures?date={hoje}"
    
    try:
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
            await update.message.reply_text("Jogo não encontrado hoje.")
    except Exception as e:
        await update.message.reply_text("Erro ao buscar dados. Tente novamente.")

if __name__ == '__main__':
    app = ApplicationBuilder().token(TOKEN_TELEGRAM).build()
    app.add_handler(CommandHandler("analisar", comando_analisar))
    app.add_handler(CommandHandler("jogos", comando_analisar))
    app.add_handler(CommandHandler("bingos", comando_analisar))
    app.run_polling()
