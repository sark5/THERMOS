from abc import ABC,abstractmethod
class SatelliteProvider(ABC):
    @abstractmethod
    def search(
        self,
        latitude:float,
        longitude:float,
        start_date:str,
        end_date:str
    ):
        pass
    @abstractmethod
    def download(self,scene):
        pass
    