from datetime import datetime
from json import JSONEncoder

class Damage:
    def __init__(self):
        self.id:int | None = None
        self.legacy_id:int | None = None
        self.text:str = "Unknown"
        self.last_modified:datetime = datetime.now()
        self.who_modified:str = "Excel Importer"

class DamageSerializer(JSONEncoder):
    def default(self, o):
        if isinstance(o, Damage):
            return {
                "id": o.id,
                "legacy_id": o.legacy_id,
                "text": o.text,
                "last_modified": o.last_modified,
                "who_modified": o.who_modified,
            }
        return super(DamageSerializer, self).default(o)
