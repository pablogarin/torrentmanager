from abc import ABC, abstractmethod

class ClientInterface(ABC):
    @abstractmethod
    def search(self, query: str) -> list:
        pass

    @abstractmethod
    def find(self, id: any) -> any:
        pass
