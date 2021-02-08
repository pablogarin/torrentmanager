class ShowSearchError(Exception):
    _query = None

    def __init__(self, message, query: str):
        super.__init__(message)
        self._query = query
