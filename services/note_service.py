import time

class NoteDto:
    def __init__(self, user_id, title, content, created_at=None, updated_at=None, note_id=None):
        self.note_id = note_id
        self.user_id = user_id
        self.title = title
        self.content = content
        if created_at == None:
            created_at = round(time.time())
        self.created_at = created_at
        self.updated_at = updated_at




