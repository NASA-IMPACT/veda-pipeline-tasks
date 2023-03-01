from datetime import datetime
from enum import Enum
from typing import List

from pydantic import AnyUrl, BaseModel


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
