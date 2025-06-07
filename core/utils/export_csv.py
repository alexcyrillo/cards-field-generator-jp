import csv


def export_cards_csv(cards, file_path):
    if not cards:
        return
    fields = list(cards[0].keys())
    with open(file_path, "w", newline='', encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fields)
        writer.writeheader()
        for card in cards:
            writer.writerow(card)