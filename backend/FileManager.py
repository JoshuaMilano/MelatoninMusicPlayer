import shutil, mutagen
from pathlib import Path

from backend.SongHelpers import SongMetadata, get_song_metadata
from backend.BackendHelpers import move_album_img, move_artist_img, remove_empty_folders

class FileManager():
    """Runs operations on files and retrieves file data"""
    def __init__(self):
        self.supported_music_extensions = {'.flac', '.mp3', '.wav'}
        self.supported_image_extensions = {'.jpg', '.jpeg', '.png'}

    def sort_music_folder(self, music_folder: Path):
        # Rename music folder to unsorted_music_folder
        unsorted_music_folder = music_folder.parent / f'{music_folder.name}_UNSORTED'

        if unsorted_music_folder.exists():
            # TODO: Handle multiple unsorted folders, enumerate
            return

        # Rename the old music folder, create a new one
        music_folder.rename(unsorted_music_folder)
        music_folder.mkdir(parents=True, exist_ok=True)

        audio_files = [f for f in unsorted_music_folder.rglob('*') if f.suffix.lower() in self.supported_music_extensions]

        processed_albums = set()
        processed_artists = set()

        for file_path in audio_files:
            try:
                metadata = get_song_metadata(file_path, sanitise=True)

                if metadata is None:
                    continue

                # Indented to stay inside the try block:
                artist_folder = music_folder / metadata.album_artist
                
                album_folder = artist_folder / metadata.album
                album_folder.mkdir(parents=True, exist_ok=True)

                new_file_path = album_folder / f'{metadata.title}{file_path.suffix.lower()}'

                if album_folder not in processed_albums:
                    move_album_img(old_album_folder=file_path.parent, new_album_folder=album_folder, allowed_extensions=self.supported_image_extensions)
                    processed_albums.add(album_folder)

                if artist_folder not in processed_artists:
                    move_artist_img(old_album_folder=file_path.parent, artist_folder=artist_folder, allowed_extensions=self.supported_image_extensions)
                    processed_artists.add(artist_folder)

                # TODO: Add support for .lrc files

                if not new_file_path.exists():
                    shutil.move(file_path, new_file_path)
                else:
                    # File Exists, do nothing, leave it to the user to sort.
                    continue

            except Exception as e:
                print(e)

        remove_empty_folders(unsorted_music_folder)
        print('Done Sorting')