from datetime import datetime, timezone
from json import JSONEncoder

class Event:
    def __init__(self):
        self.id:int | None = None
        self.legacy_id:int | None = None
        self.who_reported:str = "Unknown"
        self.city:str = "Unknown"
        self.state:str = "Unknown"
        self.country:str = "Unknown"
        self.name:str = "Unknown"
        self.description:str = "Unknown"
        self.last_modified:datetime = datetime.now(timezone.utc)
        self.who_modified:str = "Excel Importer"
        self.location_id:int | None = None

        # Joined fields
        self.latitude:float | None = None
        self.longitude:float | None = None
        self.geo:str | None = None

class EventSerializer(JSONEncoder):
    def default(self, o):
        if isinstance(o, Event):
            return {
                "id": o.id,
                "legacy_id": o.legacy_id,
                "who_reported": o.who_reported,
                "city": o.city,
                "state": o.state,
                "country": o.country,
                "name": o.name,
                "description": o.description,
                "last_modified": o.last_modified,
                "who_modified": o.who_modified,
                "location_id": o.location_id,

                # Joined fields
                "latitude": o.latitude,
                "longitude": o.longitude,
                "geo": o.geo,
            }
        return super(EventSerializer, self).default(o)

