import os

ROOT_DIR = os.path.dirname(__file__)

CACHE_ROOT = os.path.join(ROOT_DIR, 'cache')

DOWNLOADER_SETTINGS = {
    'backend': 'CCCAGG'
}


def ensure_dir_exists(path):
    if not os.path.exists(path):
        os.makedirs(path)