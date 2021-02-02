from abc import ABC, abstractmethod


class PersistanceInterface(ABC):
    @abstractmethod
    def write(self, data):
        pass

    @abstractmethod
    def read(self, param):
        pass

    @abstractmethod
    def find(self, query):
        pass