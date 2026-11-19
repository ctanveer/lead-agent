import logging
import os

import httpx

log = logging.getLogger("lead-agent")


def _post(text: str):
    url = os.getenv("SLACK_WEBHOOK_URL")
    if not url:
        log.info("Slack not configured, would have posted:\n%s", text)
        return
    try:
        httpx.post(url, json={"text": text}, timeout=10).raise_for_status()
    except httpx.HTTPError:
        log.exception("Slack post failed")


def notify_hot(lead: dict, r: dict):
    _post(
        f":fire: Hot lead ({r['score']}/100)\n"
        f"*{lead['name']}*, {lead['job_title']} at {lead['company']}\n"
        f"Email: {lead['email']}\n"
        f"Why: {r['reasoning']}\n"
        f"Next step: {r['next_step']}"
    )


def notify_review(lead: dict, error: str):
    _post(f":warning: Needs manual review: {lead['email']} ({error})")
