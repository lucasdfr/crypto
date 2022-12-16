from config import Config
from models import BaseModel


class W3(BaseModel):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.w3 = Config.get_web3()
