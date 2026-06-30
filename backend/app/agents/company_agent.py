class CompanyAgent:
    """
    Purpose:
        Provide structured company intelligence placeholders for the future
        multi-agent research layer.

    Responsibilities:
        - Represent company profile, business, sector, headquarters, and peer
          context in a consistent JSON shape.
        - Keep company enrichment separate from stock price and news retrieval.
        - Document future API and RAG integration points.

    Expected inputs:
        - A ticker or company name string.

    Expected outputs:
        - Dictionaries containing normalized company fields and metadata about
          placeholder status.

    Future expansion notes:
        - Integrate company fundamentals APIs for profile, sector, industry,
          and headquarters fields.
        - Use RAG over filings, annual reports, earnings transcripts, and
          curated company notes for business descriptions and competitor maps.
        - Add source attribution once external data providers are connected.
    """

    PLACEHOLDER_SOURCE = "phase_2_placeholder"

    def get_company_profile(self, company: str):
        return {
            "company": company,
            "profile": {
                "name": company,
                "description": None,
                "website": None,
                "exchange": None,
            },
            "source": self.PLACEHOLDER_SOURCE,
            "notes": "Future API/RAG integration will populate company profile details.",
        }

    def get_company_business(self, company: str):
        return {
            "company": company,
            "business": {
                "summary": None,
                "segments": [],
                "revenue_drivers": [],
            },
            "source": self.PLACEHOLDER_SOURCE,
            "notes": "Future RAG integration can summarize filings and annual reports.",
        }

    def get_company_sector(self, company: str):
        return {
            "company": company,
            "sector": None,
            "industry": None,
            "source": self.PLACEHOLDER_SOURCE,
            "notes": "Future fundamentals APIs can populate sector and industry fields.",
        }

    def get_company_headquarters(self, company: str):
        return {
            "company": company,
            "headquarters": {
                "city": None,
                "state": None,
                "country": None,
            },
            "source": self.PLACEHOLDER_SOURCE,
            "notes": "Future company profile APIs can populate headquarters metadata.",
        }

    def get_company_competitors(self, company: str):
        return {
            "company": company,
            "competitors": [],
            "source": self.PLACEHOLDER_SOURCE,
            "notes": "Future API/RAG integration can build peer groups by sector, industry, and business model.",
        }
