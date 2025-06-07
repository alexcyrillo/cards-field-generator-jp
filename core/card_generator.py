import time
from core.utils.romaji import romaji_to_japanese
from integrations.openai_client import consultar_ia, is_japanese
from configs.prompts import PROMPTS
from concurrent.futures import ThreadPoolExecutor, as_completed
import json


def gerar_campos_para_palavra(word, log_func=None):
    word_jap = romaji_to_japanese(word)
    prompt = PROMPTS
    if log_func:
        log_func(f"Gerando {word_jap}")
    # Monta prompt único para todos os campos, usando as chaves corretas do PROMPTS
    prompt_str = (
        f"Responda SOMENTE em JSON, sem explicações, para a palavra japonesa '{word_jap}', com as chaves: 'Kanji', 'Conjugação', 'Tradução', 'Definição', 'Exemplos de uso', 'Formalidade'.\n"
        "Exemplo de resposta:\n"
        '{"Kanji": "...", "Conjugação": "...", "Tradução": "...", "Definição": "...", "Exemplos de uso": "...", "Formalidade": "..."}'
        '\nSiga as seguintes regras:'
        f" Para o campo Kanji: {prompt['Kanji']}"
        f" Para o campo Conjugação: {prompt['Conjugação']}"
        f" Para o campo Tradução: {prompt['Tradução']}"
        f" Para o campo Definição: {prompt['Definição']}"
        f" Para o campo Exemplos de uso: {prompt['Exemplos de uso']}"
        f" Para o campo Formalidade: {prompt['Formalidade']}"
    )
    resposta = consultar_ia(prompt_str)
    try:
        campos = json.loads(resposta)
    except Exception:
        # fallback: tenta encontrar o JSON na resposta
        try:
            json_start = resposta.find('{')
            json_end = resposta.rfind('}') + 1
            campos = json.loads(resposta[json_start:json_end])
        except Exception:
            # fallback: retorna tudo em um campo só
            campos = {k: resposta for k in PROMPTS.keys()}
    return campos


def gerar_cards(palavras, log_func=None):
    todos = []
    def gerar_para_palavra(palavra):
        palavra_jap = romaji_to_japanese(palavra)
        if log_func:
            log_func(f"Gerando registro para: {palavra_jap}")
        return gerar_campos_para_palavra(palavra_jap, log_func=log_func)

    with ThreadPoolExecutor(max_workers=min(5, len(palavras))) as executor:
        futures = [executor.submit(gerar_para_palavra, palavra) for palavra in palavras]
        for future in as_completed(futures):
            todos.append(future.result())
    return todos
