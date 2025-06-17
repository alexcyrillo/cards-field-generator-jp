import time
from core.utils.romaji_conversor import romaji_to_japanese
from integrations.openai_client import consultar_ia, is_japanese
from configs.prompts import PROMPTS
from concurrent.futures import ThreadPoolExecutor, as_completed
import json


def gerar_campos_para_palavra(word, log_func=None):
    word_jap = romaji_to_japanese(word)
    campos = {}
    # Paraleliza as requisições para cada campo
    def gerar_campo(campo, prompt_template):
        prompt_str = prompt_template.replace('{word}', word_jap)
        if log_func:
            log_func(f"{campo}: gerando para {word_jap}")
        resposta = consultar_ia(prompt_str)
        return campo, resposta.strip()
    with ThreadPoolExecutor(max_workers=len(PROMPTS)) as executor:
        futures = [executor.submit(gerar_campo, campo, prompt) for campo, prompt in PROMPTS.items()]
        for future in as_completed(futures):
            campo, resposta = future.result()
            campos[campo] = resposta
    return campos


def gerar_cards(palavras, log_func=None, num_threads=5):
    todos = []
    def gerar_para_palavra(palavra):
        palavra_jap = romaji_to_japanese(palavra)
        if log_func:
            log_func(f"Gerando registro para: {palavra_jap}")
        return gerar_campos_para_palavra(palavra_jap, log_func=log_func)

    with ThreadPoolExecutor(max_workers=min(num_threads, len(palavras))) as executor:
        futures = [executor.submit(gerar_para_palavra, palavra) for palavra in palavras]
        for future in as_completed(futures):
            todos.append(future.result())
    return todos
