DEBUG = 1
INFO = 2
NONE = 3

LEVEL = DEBUG # SET THIS

def SetLevel(level):
    global LEVEL
    LEVEL = level
    _reset()

deb = print
info = print

def _reset():
    global deb, info
    deb = print if LEVEL <= DEBUG else lambda *a, **k: None
    info = print if LEVEL <= INFO else lambda *a, **k: None

_reset()
