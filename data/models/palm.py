from datetime import datetime, timezone

class Palm:
    def __init__(self):
        self.id = None
        self.legacy_id = None
        self.genus = None
        self.species = None
        self.variety = None
        self.common_name = None
        self.last_modified = datetime.now(timezone.utc)
        self.who_modified = "Excel Importer"
