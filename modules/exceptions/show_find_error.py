class ShowFindException(Exception):
    __seriesid = None

    def __init__(self, message: str, seriesid: any):
        super.__init__(message)
        self.__seriesid = seriesid
