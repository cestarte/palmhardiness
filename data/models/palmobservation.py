from datetime import datetime, timezone
from json import JSONEncoder

class PalmObservation:
    def __init__(self):
        self.id:int | None = None
        self.legacy_id:int
        self.palm_id:int
        self.palm_legacy_id:int
        self.who_reported:str
        self.city:str | None = None
        self.state:str | None = None
        self.country:str
        self.damage_id:int
        self.damage_legacy_id:int
        self.event_legacy_id:int
        self.event_id:int
        self.description:str
        self.source:str
        self.low_temp:float
        self.last_modified:datetime = datetime.now(timezone.utc)
        self.who_modified:str = "Excel Importer"
        self.location_id:int | None = None

        # These fields are not in the database
        self.event_name:str | None = None
        self.event_description:str | None = None
        self.event_who_reported:str | None = None
        self.damage_text:str | None = None
        self.location:str | None = None

    
class PalmObservationSerializer(JSONEncoder):
    def default(self, o):
        if isinstance(o, PalmObservation):

            o.location = None
            if o.city is not None:
                o.location = o.city
            if o.location is not None and o.state is not None:
                o.location += f", {o.state}"
            elif o.state is not None:
                o.location = o.state
            if o.location is not None and o.country is not None:
                o.location += f", {o.country}"
            elif o.country is not None:
                o.location = o.country

            return {
                "id": o.id,
                "legacy_id": o.legacy_id,
                "palm_id": o.palm_id,
                "palm_legacy_id": o.palm_legacy_id,
                "who_reported": o.who_reported,
                "city": o.city,
                "state": o.state,
                "country": o.country,
                "damage_id": o.damage_id,
                "damage_legacy_id": o.damage_legacy_id,
                "event_legacy_id": o.event_legacy_id,
                "event_id": o.event_id,
                "description": o.description,
                "source": o.source,
                "low_temp": o.low_temp,
                "last_modified": o.last_modified,
                "who_modified": o.who_modified,
                "location_id": o.location_id,

                # These fields are not in the database
                "event_name": o.event_name,
                "event_description": o.event_description,
                "event_who_reported": o.event_who_reported,
                "damage_text": o.damage_text,

                # calculated
                "location": o.location
            }
        return super(PalmObservationSerializer, self).default(o)
