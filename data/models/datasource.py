from datetime import datetime
from json import JSONEncoder

class DataSource:
    """Represents a data source, which is derived from the Source field in the PalmObservation and CycadObservation tables."""
    def __init__(self):
        self.source = None
        self.count = 0
        self.type = None
    
class DataSourceSerializer(JSONEncoder):
    def default(self, o):
        if isinstance(o, DataSource):
            serialized = {
                "source": o.source,
                "count": o.count,
                "type": o.type,
            }
            return serialized
        return super(DataSourceSerializer, self).default(o)