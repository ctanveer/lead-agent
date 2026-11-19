import os

import httpx

FREE_DOMAINS = {"gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com"}

UNKNOWN = {
    "industry": "unknown",
    "employee_count": "unknown",
    "country": "unknown",
    "short_description": "unknown",
}


def domain_of(email: str) -> str:
    return email.split("@")[1].lower().strip()


def enrich(domain: str) -> dict:
    """Return company facts for a domain. Never raises: failures give "unknown"."""
    key = os.getenv("ENRICH_API_KEY")
    if not key:
        return dict(UNKNOWN)
    try:
        r = httpx.get(
            "https://api.your-provider.com/v1/company",  # placeholder: replace with your provider
            params={"domain": domain},
            headers={"Authorization": f"Bearer {key}"},
            timeout=10,
        )
        r.raise_for_status()
        data = r.json()
        return {k: data.get(k) or "unknown" for k in UNKNOWN}
    except (httpx.HTTPError, ValueError):
        return dict(UNKNOWN)
