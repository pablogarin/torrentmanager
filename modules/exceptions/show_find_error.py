class ShowFindException(Exception):
    _seriesid = None

    def __init__(self, message: str, seriesid: any):
        super.__init__(message)
        self._seriesid = seriesid
