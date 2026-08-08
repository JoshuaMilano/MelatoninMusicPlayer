import re

def sanitise_data(name):
    """Removes illegal characters that Windows forbids in folder and file names."""
    sanitised = re.sub(r'[<>:"/\\|?*]', '', str(name))
    return sanitised.strip(' .')

def get_primary_artist(artist_string):
    """Splits concatenated artist strings and returns on the primary artist."""
    artist_string = str(artist_string)
    parts = re.split(r'(?i)\s*(?:;|\bfeat\.?\b|\bft\.?\b)', str(artist_string))

    return parts[0].strip()