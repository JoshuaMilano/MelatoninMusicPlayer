from dataclasses import dataclass
from pathlib import Path
import mutagen

from backend.BackendHelpers import get_primary_artist

@dataclass
class SongMetadata:
    """Dataclass to store music metadata"""
    title: str
    artist: str
    album: str
    album_artist: str
    duration_ms: int


def get_song_metadata(file_path_str):
    file_path = Path(file_path_str)
    try:
        audio = mutagen.File(file_path, easy=True)
    except TypeError:
        audio = mutagen.File(file_path)

    if audio is None:
        return None

    raw_title = audio.get('title', [file_path.stem])[0]
    raw_artist = get_primary_artist(audio.get('artist', ['Unknown Artist'])[0])
    raw_album = audio.get('album', ['Unknown Album'])[0]
    raw_album_artist = get_primary_artist((audio.get('albumartist') or audio.get('artist', ['Unknown Artist']))[0])
    raw_duration = int(audio.info.length)
    
    return SongMetadata(
        title = raw_title,
        artist = raw_artist,
        album = raw_album,
        album_artist = raw_album_artist,
        duration_ms = raw_duration * 1000
    )