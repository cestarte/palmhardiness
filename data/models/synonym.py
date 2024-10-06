from datetime import datetime, timezone
from json import JSONEncoder

class Synonym:
    def __init__(self):
        self.id:int | None = None
        self.palm_legacy_id:int | None = None
        self.genus:str = "Unknown"
        self.species:str = "Unknown"
        self.variety:str = "Unknown"
        self.last_modified:datetime = datetime.now(timezone.utc)
        self.who_modified:str = "Excel Importer"


class SynonymSerializer(JSONEncoder):
    def default(self, o):
        if isinstance(o, Synonym):
            return {
                "id": o.id,
                "palm_legacy_id": o.palm_legacy_id,
                "genus": o.genus,
                "species": o.species,
                "variety": o.variety,
                "last_modified": o.last_modified,
                "who_modified": o.who_modified
            }
        return super(SynonymSerializer, self).default(o)
