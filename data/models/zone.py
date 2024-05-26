from datetime import datetime
from json import JSONEncoder

class Zone:
    def __init__(self):
        self.id:int | None = None
        self.name:str = "Unknown"
        self.min:float = -1.0
        self.max:float = 1.0
        self.last_modified:datetime = datetime.now()
        self.who_modified:str = "Excel Importer"

class ZoneSerializer(JSONEncoder):
    def default(self, o):
        if isinstance(o, Zone):
            return {
                "id": o.id,
                "name": o.name,
                "min": o.min,
                "max": o.max,
                "last_modified": o.last_modified,
                "who_modified": o.who_modified
            }
        return super(ZoneSerializer, self).default(o)


