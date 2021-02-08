from abc import ABC, abstractmethod


class PersistanceInterface(ABC):
    @abstractmethod
    def write(self, data: any) -> None:
        pass

    @abstractmethod
    def read(self, param: any) -> any:
        pass

    @abstractmethod
    def find(self, query: str) -> list:
        pass
