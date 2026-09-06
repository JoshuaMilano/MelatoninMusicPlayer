from backend.dataStructures.LinkedList import LinkedList

class Queue:
    """Creates an empty music queue"""
    def __init__(self):
        self.song_list = LinkedList()
        self.current_song = self.song_list.head

    def append(self, data):
        self.song_list.append(data)
        if not self.current_song:
            self.current_song = self.song_list.head
        