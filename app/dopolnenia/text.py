import os
FILES_PATH = r'__pycache__'
def read_file(file_path):
    with open(file_path, encoding='utf-8') as file:
        return [line.strip() for line in file]

ACCENTS_WORD = read_file(os.path.join(FILES_PATH, 'accents.txt'))
ACCENTS_WORD_WRONG = read_file(os.path.join(FILES_PATH, 'accents_wrong.txt'))
DICTIONARY_WORD = read_file(os.path.join(FILES_PATH, 'dictionary.txt'))
DICTIONARY_WORD_WRONG = read_file(os.path.join(FILES_PATH, 'dictionary_wrong.txt'))

words = {
    'accents': (ACCENTS_WORD, ACCENTS_WORD_WRONG),
    'dictionary': (DICTIONARY_WORD, DICTIONARY_WORD_WRONG)}

options_main = {
    'accents': ('📢 Ударения\n 4 задание ЕГЭ'),
    'dictionary': ('✏️ Словарные слова\n 9 задание ЕГЭ'),
    'GoMain_menu': ('✍️ <b>Егэ русский язык</b>')
}


