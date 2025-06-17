import jaconv
from integrations.openai_client import is_japanese

def romaji_to_japanese(word):
    if is_japanese(word):
        return word
    return jaconv.alphabet2kana(word)
