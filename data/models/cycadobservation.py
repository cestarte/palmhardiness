from datetime import datetime, timezone

class CycadObservation:
    def __init__(self):
        self.id:int | None = None
        self.cycad_id:int
        self.cycad_legacy_id:int
        self.who_reported:str
        self.city:str | None = None
        self.state:str | None = None
        self.country:str
        self.damage_id:int
        self.event_legacy_id:int
        self.event_id:int
        self.description:str
        self.source:str
        self.low_temp:float
        self.last_modified:datetime = datetime.now(timezone.utc)
        self.who_modified:str = "Excel Importer"

        # These fields are not in the database
        self.damage_text:str | None = None
        self.genus:str | None = None
        self.species:str | None = None
        self.variety:str | None = None