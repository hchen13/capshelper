import os

ROOT_DIR = os.path.dirname(__file__)

DB_HOST = "localhost"
DB_NAME = "caps"
DB_USER = "root"
DB_PASS = "root"

CACHE_ROOT = os.path.join(ROOT_DIR, 'cache')


def ensure_dir_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)