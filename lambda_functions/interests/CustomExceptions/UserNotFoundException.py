class UserNotFoundException(Exception):
    def __init__(self,message=None):
        super().__init__(message)

    def message(self):
        return self.message()