import sqlite3
from pathlib import Path

class Database():
    def __init__(self, database_location: str = ''):
        # Grab location of the MelatoninMusicPLayer folder
        self.file_directory = database_location

        # Create the database variable
        self.db = None

    def set_new_location(self, new_folder: str):
        """Sets a new database location, and rebuilds the database"""
        # Grab the new folder
        self.file_directory = new_folder

        # Create the full path
        self.db_path = Path(new_folder) / 'MelatoninMusicPlayer' / 'library.db'

        # Make sure the path and file exists exists
        self.db_path.parent.mkdir(parents=True, exist_ok=True)

        self.rebuild()

    def rebuild(self):
        """Rebuild (or build) the database"""
        # Get database
        database = sqlite3.connect(str(self.db_path))

        # Turn on foreign key constraints (to be safe)
        database.execute('PRAGMA foreign_keys = ON')

        # Return all data as dictionaries
        database.row_factory = sqlite3.Row

        # Set db to the database
        self.db = database


