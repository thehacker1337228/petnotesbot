import time

class UserDto:
    def __init__(self, tg_id,username,state="start",json_data=None, created_at = None, user_id = None):
        self.tg_id = tg_id
        self.username = username
        if created_at == None:
            created_at = round(time.time())
        self.created_at = created_at
        self.state = state
        self.json_data = json_data
        self.user_id = user_id

