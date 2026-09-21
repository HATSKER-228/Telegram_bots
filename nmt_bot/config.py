import os

BOT_TOKEN = os.environ.get('TOKEN')
WORDS_PER_TEST = int(os.getenv("WORDS_PER_TEST", "36"))
