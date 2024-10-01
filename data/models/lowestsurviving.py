from datetime import datetime
from json import JSONEncoder

### POCO representing a query result, not a database table
class LowestSurviving:
    def __init__(self):
        self.id = None
        self.genus = None
        self.species = None
        self.variety = None
        self.common_name = None
        self.min = 0
        self.max = 0
        self.average = 0
        self.records = None
        self.name = None
    
class LowestSurvivingSerializer(JSONEncoder):
    def default(self, o):
        if isinstance(o, LowestSurviving):

            if o.species == '' or o.species == '<Genus>':
                o.species = None

            name = o.genus
            if o.species is not None and o.species != "<Genus>":
                name += f" {o.species}"
            if o.variety is not None:
                name += f" {o.variety}"

            serialized = {
                "id": o.id,
                "genus": o.genus,
                "species": o.species,
                "variety": o.variety,
                "common_name": o.common_name,
                "min": o.min,
                "max": o.max,
                "average": o.average,
                "records": o.records,
                "name": name,
            }

            return serialized
        return super(LowestSurvivingSerializer, self).default(o)