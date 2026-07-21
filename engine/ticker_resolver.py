import json


class TickerResolver:

    def __init__(self, knowledge_file="knowledge/knowledge_base.json"):
        with open(knowledge_file, "r") as f:
            self.knowledge = json.load(f)

        self.aliases = {
            "hdfc": "HDFCBANK",
            "icici": "ICICIBANK",
            "sbi": "SBIN",
            "tcs": "TCS",
            "lt": "LT",
            "l&t": "LT",
            "reliance": "RELIANCE",
            "infosys": "INFY",
            "airtel": "BHARTIARTL",
            "itc": "ITC",
            "sun pharma": "SUNPHARMA",
            "sunpharma": "SUNPHARMA"
        }

    def _build_response(self, ticker):

        data = self.knowledge[ticker]

        return {
            "ticker": data["yahoo_ticker"],
            "company_name": data["company_name"]
        }

    def resolve(self, company_name):

        query = company_name.lower().strip()

        # -----------------------------
        # Alias match
        # -----------------------------
        if query in self.aliases:
            return self._build_response(self.aliases[query])

        # -----------------------------
        # Exact company name
        # -----------------------------
        for ticker, data in self.knowledge.items():

            if data["company_name"].lower() == query:
                return self._build_response(ticker)

        # -----------------------------
        # Exact internal ticker
        # -----------------------------
        for ticker in self.knowledge:

            if ticker.lower() == query:
                return self._build_response(ticker)

        # -----------------------------
        # Partial company name
        # -----------------------------
        for ticker, data in self.knowledge.items():

            if query in data["company_name"].lower():
                return self._build_response(ticker)

        return None

    def get_supported_companies(self):

        return sorted(
            data["company_name"]
            for data in self.knowledge.values()
        )