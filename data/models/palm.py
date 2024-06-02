from datetime import datetime
from json import JSONEncoder

class Palm:
    def __init__(self):
        self.id = None
        self.legacy_id = None
        self.genus = None
        self.species = None
        self.variety = None
        self.common_name = None
        self.zone_id = 0
        self.last_modified = datetime.now()
        self.who_modified = "Excel Importer"

        # fields not in the database but commonly included
        self.zone_name = None
        self.observation_count = None
    
class PalmSerializer(JSONEncoder):
    def default(self, o):
        if isinstance(o, Palm):
            serialized = {
                "id": o.id,
                "legacy_id": o.legacy_id,
                "genus": o.genus,
                "zone_id": o.zone_id,
                "last_modified": o.last_modified,
                "who_modified": o.who_modified,
                "species": o.species,
                "variety": o.variety,
                "common_name": o.common_name,
                "zone_name": o.zone_name,
                "observation_count": o.observation_count,
            }



            return serialized
        return super(PalmSerializer, self).default(o)