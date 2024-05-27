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
        self.zone_name = None
        self.last_modified = datetime.now()
        self.who_modified = "Excel Importer"
    
class PalmSerializer(JSONEncoder):
    def default(self, o):
        if isinstance(o, Palm):
            return {
                "id": o.id,
                "legacy_id": o.legacy_id,
                "genus": o.genus,
                "species": o.species,
                "variety": o.variety,
                "common_name": o.common_name,
                "zone_id": o.zone_id,
                "zone_name": o.zone_name,
                "last_modified": o.last_modified,
                "who_modified": o.who_modified,
            }
        return super(PalmSerializer, self).default(o)