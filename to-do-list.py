import psycopg2

from prompt_toolkit import prompt
from prompt_toolkit.completion import WordCompleter

choices = WordCompleter(['start', 'exit', 'help'])

while True:
    answer = prompt('Выбери: ', completer=choices)
    print("Ты выбрал:", answer)