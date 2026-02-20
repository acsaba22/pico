DEBUG = True
deb = print if DEBUG else lambda *a, **k: None

INFO = True
deb = print if INFO else lambda *a, **k: None