import os
from dotenv import load_dotenv
from core.card_generator import gerar_cards

# Carrega variáveis de ambiente do arquivo .env
load_dotenv()

# CONFIG
MODEL = "gpt-4"  # Ou gpt-3.5-turbo

# Função principal
if __name__ == "__main__":
    entrada = input("Digite as palavras separadas por vírgula: ")
    palavras = [p.strip() for p in entrada.split(",")]

    cards = gerar_cards(palavras)

    # Exibe resultados (ou salva como TSV/CSV para importar depois)
    for card in cards:
        print("\n" + "="*40)
        for campo, conteudo in card.items():
            print(f"{campo}: {conteudo}")
