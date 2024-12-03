from abc import ABC, abstractmethod
import pandas as pd

class Client(ABC):
    def __init__(self, creds):
        self.creds = creds

    @abstractmethod
    def get_price_history(self, product_id: str, bars: int, granularity: str, end_date=None) -> pd.DataFrame:
        raise NotImplementedError
    
    
