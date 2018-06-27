import settings
from downloader.cccagg import CCCAGG

DEFAULTS = {
    'backend': 'CCCAGG'
}

configs = getattr(settings, 'DOWNLOADER_SETTINGS', None) or DEFAULTS

if configs['backend'] == 'CCCAGG':
    Downloader = CCCAGG
# TODO: additional backends registered here if implemented
else:
    print("Unknown backend: {}, fall back to default backend.".format(configs['backend']))
    Downloader = CCCAGG