from datetime import datetime
from json import JSONEncoder
from typing import Optional

class Location:
    def __init__(self):
        self.id:Optional[int] = None
        self.last_modified:datetime = datetime.now()
        self.who_modified:str = 'Unknown'
        self.latitude:Optional[str] = None
        self.longitude:Optional[str] = None
        self.city:Optional[str] = None
        self.state:Optional[str] = None
        self.country:Optional[str] = None

        # Fields not stored to DB
        # Used during import to track the ids of associated items
        # self.palm_observations:list[int] = []
        # self.event_observations:list[int] = []
        # self.cycad_observations:list[int] = []
        self.source:Optional[str] = None
        self.source_id:Optional[int] = None

    def __eq__(self, other):
        return self.city == other.city and self.state == other.state and self.country == other.country
    
    def __ne__(self, other):
        return self.city != other.city or self.state != other.state or self.country != other.country

    def __str__(self):
        self_str = ''
        for key, value in self.__dict__.items():
            self_str += f'{key}: {value}, '
        return self_str

class LocationSerializer(JSONEncoder):
    def default(self, o):
        if isinstance(o, Location):
            return {
                "id": o.id,
                "last_modified": o.last_modified,
                "who_modified": o.who_modified,
                "latitude": o.latitude,
                "longitude": o.longitude,
                "city": o.city,
                "state": o.state,
                "country": o.country
            }
        return super(LocationSerializer, self).default(o)


