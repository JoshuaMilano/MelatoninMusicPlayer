import sqlite3
from pathlib import Path

class Database():
    def __init__(self, datafolder_location: str):
        # Create the database variable
        self.db = None

        # Create the database file
        self.database_location = Path(datafolder_location) / 'library.db'
        self.database_location.parent.mkdir(parents=True, exist_ok=True)
        self.database_location.touch(exist_ok=True)

        self.build()

    def build(self):
        """Rebuild (or build) the database"""
        # Get database
        database = sqlite3.connect(str(self.database_location))

        # Turn on foreign key constraints (to be safe)
        database.execute('PRAGMA foreign_keys = ON')

        # Return all data as dictionaries
        database.row_factory = sqlite3.Row

        # Set db to the database
        self.db = database


