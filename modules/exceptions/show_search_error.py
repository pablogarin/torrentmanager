class ShowSearchException(Exception):
    __query = None

    def __init__(self, message, query: str):
        super.__init__(message)
        self.__query = query
