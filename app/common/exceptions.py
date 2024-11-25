class DuplicateError(Exception):
    """데이터 중복 시 발생하는 예외"""

    def __init__(self, message: str):
        self.message = message
        self.status_code = 409


class NotFoundError(Exception):
    """데이터 존재하지 않을 때 발생하는 예외"""

    def __init__(self, message: str):
        self.message = message
        self.status_code = 404
