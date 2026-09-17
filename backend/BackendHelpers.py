import re, shutil
from pathlib import Path

def sanitise_data(name):
    """Removes illegal characters that Windows forbids in folder and file names."""
    sanitised = re.sub(r'[<>:"/\\|?*]', '', str(name))
    return sanitised.strip(' .')

def get_primary_artist(artist_string):
    """Splits concatenated artist strings and returns on the primary artist."""
    artist_string = str(artist_string)
    parts = re.split(r'(?i)\s*(?:;|\bfeat\.?\b|\bft\.?\b)', str(artist_string))

    return parts[0].strip()

def move_album_img(*, old_album_folder: Path, new_album_folder: Path, allowed_extensions: set):
    """Copies album art from the original location to the new location if that album art image extension is allowed"""

    images_in_folder = [img for img in old_album_folder.iterdir() if img.suffix.lower() in allowed_extensions]
    
    if images_in_folder:
        cover_source = images_in_folder[0]
        cover_target = new_album_folder / f'cover{cover_source.suffix.lower()}'

        if not cover_target.exists():
            shutil.move(cover_source, cover_target)

    
def move_artist_img(*, old_album_folder: Path, artist_folder: Path, allowed_extensions: set):
    """Copies artist art from the original location to the new location if that artist art image extension is allowed"""
    artist_art_path = None
    for ext in allowed_extensions:
        if (old_album_folder.parent / f'artist{ext}').exists():
            artist_art_path = old_album_folder.parent / f'artist{ext}'
            break
        elif (old_album_folder / f'artist{ext}').exists():
            artist_art_path = old_album_folder / f'artist{ext}'
            break

    if artist_art_path:
        artist_art_target = artist_folder / f'artist{artist_art_path.suffix.lower()}'
        if not artist_art_target.exists():
            shutil.move(artist_art_path, artist_art_target)

def remove_empty_folders(directory: Path):
    for folder in sorted(directory.rglob('*'), key=lambda p: len(p.parts), reverse=True):
        if folder.is_dir() and not any(folder.iterdir()):
            folder.rmdir()