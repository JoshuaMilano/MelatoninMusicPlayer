import sqlite3, shutil
from pathlib import Path
from backend.FileManager import FileManager

class Database():
    def __init__(self, datafolder_location: str):

        # Create the database variable
        self.db = None

        # Create the file manager
        self.file_manager = FileManager()

        # Create the database file
        self.database_location = Path(datafolder_location) / 'library.db'
        self.database_location.parent.mkdir(parents=True, exist_ok=True)
        self.database_location.touch(exist_ok=True)

        self.create_db()
        # self.build_db()

    def create_db(self):
        """Rebuild (or build) the database"""
        # Get database
        database = sqlite3.connect(str(self.database_location))

        # Turn on foreign key constraints (to be safe)
        database.execute('PRAGMA foreign_keys = ON')

        # Return all data as dictionaries
        database.row_factory = sqlite3.Row

        # Set db to the database
        self.db = database

    def build_db(self, music_folder: Path):
        self.file_manager.sort_music_folder(music_folder)
        pass
            

