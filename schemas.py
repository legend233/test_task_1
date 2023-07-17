from typing import List, Dict
from pydantic import BaseModel
class Rate_valid(BaseModel):
    cargo_type: str
    rate: float

class Prices_load(BaseModel):
    __root__: Dict[str, List[Rate_valid]]

class Status(BaseModel):
    message: str