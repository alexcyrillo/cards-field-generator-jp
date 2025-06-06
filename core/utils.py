import csv

def processar_palavras(texto):
    return [p.strip() for p in texto.strip().split(",") if p.strip()]

def exportar_cards_csv(cards, file_path):
    if not cards:
        return
    campos = list(cards[0].keys())
    with open(file_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=campos)
        writer.writeheader()
        for card in cards:
            writer.writerow(card)
