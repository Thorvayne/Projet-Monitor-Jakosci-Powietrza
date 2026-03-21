from pydantic import BaseModel, ConfigDict
from typing import Optional, List

class City(BaseModel):
    id: int
    name: str

class Station(BaseModel):
    id: int
    stationName: str
    gegrLat: str
    gegrLon: str
    city: Optional[City] = None

class IndexLevel(BaseModel):
    id: int
    indexLevelName: str

class AirQualityIndex(BaseModel):
    id: int
    stCalcDate: Optional[str] = None
    stIndexLevel: Optional[IndexLevel] = None
    
    
    model_config = ConfigDict(extra='ignore')