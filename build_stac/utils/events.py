from datetime import datetime
from typing import Dict, List, Literal, Optional, Union
from pathlib import Path
import re

from .provider import Provider
from pydantic import BaseModel, Field
import pystac


INTERVAL = Literal["month", "year"]


class BaseEvent(BaseModel, frozen=True):
    collection: str
    s3_filename: str

    id_regex: Optional[str] = None
    asset_name: Optional[str] = None
    asset_roles: Optional[List[str]] = None
    asset_media_type: Optional[Union[str, pystac.MediaType]] = None

    providers: List[Provider] = []

    def item_id(self: "BaseEvent") -> str:
        if self.id_regex:
            id_components = re.findall(self.id_regex, self.s3_filename)
            assert len(id_components) == 1
            id = "-".join(id_components[0])
        else:
            id = Path(self.s3_filename).stem
        return id


class CmrEvent(BaseEvent):
    granule_id: str


class RegexEvent(BaseEvent):
    filename_regex: Optional[str]

    start_datetime: Optional[datetime] = None
    end_datetime: Optional[datetime] = None
    single_datetime: Optional[datetime] = None

    properties: Optional[Dict] = Field(default_factory=dict)
    datetime_range: Optional[INTERVAL] = None

    providers: List[Provider] = []


SupportedEvent = Union[RegexEvent, CmrEvent]
