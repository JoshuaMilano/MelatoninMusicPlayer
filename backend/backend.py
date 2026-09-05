from pathlib import Path
from platformdirs import user_data_path

from database.Database import Database

class DataFolder():
    def __init__(self):
        # Create variable to store Database Class
        self.database = None

        # Default Path
        # WINDOWS:  // <Username>\AppData\Local\MelatoninMusicPlayer
        # Linux:    // .local/share/MelatoninMusicPlayer
        default_path = user_data_path(appname='MelatoninMusicPlayer', appauthor=False)

        # check for an existing datafolder
        if default_path.exists() and default_path.is_dir():
            # Set Default path
            self.datafolder_location = default_path    
            # Instance the database class
            self.database = Database(self.datafolder_location)
        else:
            # Set Datafolder location to None
            self.datafolder_location = None

    def setup_folder(self, setup_location):
        if setup_location:
            self.datafolder_location = Path(setup_location) / 'MelatoninMusicPlayer'     
        else:
            self.datafolder_location = user_data_path(appname='MelatoninMusicPlayer', appauthor=False)

        # Create the 'MelatoninMusicPLayer folder'
        self.datafolder_location.mkdir(parents=True, exist_ok=True)
        # Instance the database class
        self.database = Database(self.datafolder_location)
