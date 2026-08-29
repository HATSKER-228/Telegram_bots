import os
from pathlib import Path

TOKEN = os.environ.get('TOKEN')
ADMIN_ID = 1250738671
DATA_DIR = Path(__file__).resolve().parent.parent / 'data'
