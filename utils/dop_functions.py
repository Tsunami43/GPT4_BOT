import re

from loader import encoder


def clear_text(text:str):
    l = re.findall("(?is).+?[.!?]", text)
    return ''.join(l)

def num_tokens_from_text(text: str) -> int:
    return len(encoder.encode(text)) + 2

def split_text_every_n_symbols(text : str, n : int = 4000):
    return [text[i:i + n] for i in range(0, len(text), n)]