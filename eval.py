import csv
import sys

from dotenv import load_dotenv

load_dotenv()

from enrich import FREE_DOMAINS, domain_of, enrich
from scoring import score_lead

path = sys.argv[1] if len(sys.argv) > 1 else "labeled_leads.csv"
with open(path, newline="") as f:
    rows = list(csv.DictReader(f))

hits = 0
for r in rows:
    domain = domain_of(r["email"])
    if domain in FREE_DOMAINS:  # same shortcut as the live pipeline
        res = {"score": 0, "tier": "cold"}
    else:
        res = score_lead(r, enrich(domain))
    ok = res["tier"] == r["expected_tier"]
    hits += ok
    print("OK  " if ok else "MISS", r["email"], res["score"], res["tier"], "expected", r["expected_tier"])
print(f"agreement: {hits}/{len(rows)} ({hits / max(len(rows), 1):.0%})")
