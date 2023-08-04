from warnings import filterwarnings

filterwarnings(action="ignore", module=".*vlc.*", category=DeprecationWarning)
