import logging
import os
import secrets

from dotenv import load_dotenv
from fastapi import BackgroundTasks, FastAPI, Header, HTTPException
from pydantic import BaseModel, EmailStr

load_dotenv()

# imported after load_dotenv so env vars are set
from enrich import FREE_DOMAINS, domain_of, enrich
from notify import notify_hot, notify_review
from scoring import score_lead
from store import init, save

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("lead-agent")

app = FastAPI(title="Lead scoring agent")
init()


class Lead(BaseModel):
    name: str
    email: EmailStr
    company: str = ""
    job_title: str = ""
    website: str = ""
    message: str = ""
    source: str = "unknown"


def process_lead(lead: Lead):
    data = lead.model_dump()
    data["email"] = data["email"].lower().strip()
    domain = domain_of(data["email"])

    if domain in FREE_DOMAINS:
        result = {"score": 0, "tier": "cold", "reasoning": "Personal email address.",
                  "next_step": "No action."}
    else:
        try:
            result = score_lead(data, enrich(domain))
        except Exception as exc:  # a failed score must never lose a lead
            log.exception("Scoring failed for %s", data["email"])
            notify_review(data, str(exc))
            result = {"score": 0, "tier": "review", "reasoning": f"Scoring failed: {exc}",
                      "next_step": "Review this lead manually."}

    save(data, result)
    log.info("lead %s scored %s (%s)", data["email"], result["score"], result["tier"])
    if result["tier"] == "hot":
        notify_hot(data, result)


@app.post("/leads", status_code=202)
def new_lead(lead: Lead, background: BackgroundTasks, x_api_key: str = Header(default="")):
    expected = os.getenv("LEAD_API_KEY", "")
    if not expected or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(status_code=401, detail="Invalid API key")
    background.add_task(process_lead, lead)
    return {"status": "accepted"}
