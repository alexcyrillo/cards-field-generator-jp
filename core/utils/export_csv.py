import csv
import json

EXPECTED_FIELDS = [
    "Kanji",
    "Conjugação",
    "Tradução",
    "Definição",
    "Exemplos de uso",
    "Formalidade"
]


def flatten_card(card):
    # Se o card inteiro for uma string JSON, desserialize
    if isinstance(card, str):
        try:
            card = json.loads(card)
        except Exception:
            return card
    # Se algum campo for string JSON com todas as chaves esperadas, use esse dicionário como card e pare
    for v in card.values():
        if isinstance(v, str):
            try:
                v_json = json.loads(v)
                if isinstance(v_json, dict) and all(k in v_json for k in EXPECTED_FIELDS):
                    return v_json  # Pare aqui, não continue flatten
            except Exception:
                pass
    # Caso contrário, faz flatten normal
    new_card = {}
    for k, v in card.items():
        if isinstance(v, str):
            try:
                v_json = json.loads(v)
                if isinstance(v_json, dict):
                    new_card.update(v_json)
                    continue
            except Exception:
                pass
        new_card[k] = v
    return new_card


def export_cards_csv(cards, file_path):
    if not cards:
        return
    # Achata todos os cards e garante campos consistentes
    flat_cards = [flatten_card(card) for card in cards]
    # Remove duplicatas exatas
    seen = set()
    unique_cards = []
    for card in flat_cards:
        card_tuple = tuple((k, card.get(k, "")) for k in EXPECTED_FIELDS)
        if card_tuple not in seen:
            seen.add(card_tuple)
            unique_cards.append(card)
    # Garante que todos os campos estejam presentes
    all_fields = set(EXPECTED_FIELDS)
    for card in unique_cards:
        all_fields.update(card.keys())
    fields = [f for f in EXPECTED_FIELDS if f in all_fields] + [f for f in all_fields if f not in EXPECTED_FIELDS]
    with open(file_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for card in unique_cards:
            writer.writerow({k: card.get(k, "") for k in fields})