import os

ROOT_DIR = os.path.dirname(__file__)

DB_HOST = "localhost"
DB_NAME = "cccagg"
DB_USER = "root"
DB_PASS = "root"

CACHE_ROOT = os.path.join(ROOT_DIR, 'cache')

DOWNLOADER_SETTINGS = {
    'backend': 'CCCAGG'
}


def ensure_dir_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)