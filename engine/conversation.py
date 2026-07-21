class ConversationState:

    FIELDS = {
        "intent",
        "company_name",
        "sector",
        "risk",
        "target_return"
    }

    def __init__(self):
        self.reset()

    def __str__(self):
        return str(self.to_dict())

    def reset(self):
        self.intent = None
        self.company_name = None
        self.sector = None
        self.risk = None
        self.target_return = None
        self.missing_fields = []
    
    def update(self, parsed_query):

        for key, value in parsed_query.items():

            if key not in self.FIELDS:
                continue

            if value is not None:
                setattr(self, key, value)

        self.missing_fields = parsed_query.get("missing_fields", [])

        # Sector recommendations don't require a company name
        if (
            self.intent == "recommend_stocks"
            and self.sector is not None
            and self.company_name is None
        ):
            self.missing_fields = [
                field
                for field in self.missing_fields
                if field != "company_name"
            ]
        return self


    
    def is_complete(self):
        return len(self.missing_fields) == 0
    
    def to_dict(self):
        return {
            "intent": self.intent,
            "company_name": self.company_name,
            "sector": self.sector,
            "risk": self.risk,
            "target_return": self.target_return,
            "missing_fields": self.missing_fields
        }
    
    def from_dict(self, data):
        self.intent = data.get("intent")
        self.company_name = data.get("company_name")
        self.sector = data.get("sector")
        self.risk = data.get("risk")
        self.target_return = data.get("target_return")
        self.missing_fields = data.get("missing_fields", [])