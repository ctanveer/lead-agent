import os
import sqlite3

DB = os.getenv("LEADS_DB", "leads.db")


def init():
    with sqlite3.connect(DB) as db:
        db.execute("""CREATE TABLE IF NOT EXISTS leads (
            email TEXT PRIMARY KEY, name TEXT, company TEXT, job_title TEXT,
            source TEXT, message TEXT, score INTEGER, tier TEXT,
            reasoning TEXT, next_step TEXT, human_tier TEXT,
            status TEXT DEFAULT 'new',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP)""")


def save(lead: dict, result: dict):
    with sqlite3.connect(DB) as db:
        db.execute("""INSERT INTO leads
            (email, name, company, job_title, source, message, score, tier, reasoning, next_step)
            VALUES (:email, :name, :company, :job_title, :source, :message,
                    :score, :tier, :reasoning, :next_step)
            ON CONFLICT(email) DO UPDATE SET name=excluded.name, company=excluded.company,
                job_title=excluded.job_title, source=excluded.source, message=excluded.message,
                score=excluded.score, tier=excluded.tier,
                reasoning=excluded.reasoning, next_step=excluded.next_step""",
            {**lead, **result})
