from enum import Enum
from datetime import datetime
from typing import List

from pydantic import BaseModel, AnyUrl


class ProviderRole(str, Enum):
    host = "host"
    licensor = "licensor"
    processor = "processor"
    producer = "producer"
    publisher = "publisher"
    rights_holder = "rights_holder"
    source = "source"

    class Config:
        use_enum_values = True


class Provider(BaseModel):
    name: str
    url: AnyUrl
    roles: List[ProviderRole]
