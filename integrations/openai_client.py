import openai
import os
import re
from dotenv import load_dotenv

load_dotenv()
openai.api_key = os.getenv("OPENAI_API_KEY", "SUA_CHAVE_API")
MODEL = os.getenv("MODEL", "gpt-4.1-nano")  # Lê do .env

def is_japanese(text):
    """Retorna True se o texto contém kana ou kanji."""
    return re.search(r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff]', text) is not None

def consultar_ia(prompt):
    try:
        resposta = openai.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Você é um assistente especialista em japonês, que responde de forma clara e didática para brasileiros."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=500
        )
        return resposta.choices[0].message.content
    except Exception as e:
        return f"Erro: {e}"
