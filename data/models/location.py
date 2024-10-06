from datetime import datetime, timezone
from json import JSONEncoder
from typing import Optional

class Location:
    def __init__(self):
        self.id:Optional[int] = None
        self.last_modified:datetime = datetime.now(timezone.utc)
        self.who_modified:str = 'Unknown'
        self.latitude:Optional[str] = None
        self.longitude:Optional[str] = None
        self.city:Optional[str] = None
        self.state:Optional[str] = None
        self.country:Optional[str] = None
        self.geo:Optional[str] = None
        self.when_attempted_geocode:Optional[datetime] = None

        # Fields not stored to DB
        self.palm_observations:Optional[int] = 0
        self.events:Optional[int] = 0
        self.cycad_observations:Optional[int] = 0
        # Used during import to track the ids of associated items
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
                "country": o.country,
                "geo": o.geo,
                "when_attempted_geocode": o.when_attempted_geocode,
                "palm_observations": o.palm_observations,
                "cycad_observations": o.cycad_observations,
                "events": o.events,
            }
        return super(LocationSerializer, self).default(o)


