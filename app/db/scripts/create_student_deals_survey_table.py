import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.pool import NullPool


def create_student_deals_survey_table() -> None:
    load_dotenv()
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        raise RuntimeError("DATABASE_URL is not set.")

    engine = create_engine(
        database_url,
        poolclass=NullPool,
        pool_pre_ping=True,
    )

    inspector = inspect(engine)

    with engine.begin() as conn:
        if not inspector.has_table("student_deals_survey_responses"):
            conn.execute(
                text(
                    """
                    CREATE TABLE student_deals_survey_responses (
                        id UUID PRIMARY KEY,
                        responder_email TEXT NOT NULL,
                        interest VARCHAR(20) NOT NULL,
                        spending VARCHAR(20) NOT NULL,
                        frequency VARCHAR(30) NOT NULL,
                        category_preference TEXT[] NOT NULL,
                        decision_driver VARCHAR(40) NOT NULL,
                        offer_preference VARCHAR(40) NOT NULL,
                        ordering_preference VARCHAR(20) NOT NULL,
                        delivery_flexibility VARCHAR(10) NOT NULL,
                        usage_intent VARCHAR(30) NOT NULL,
                        open_feedback TEXT,
                        created_at TIMESTAMPTZ NOT NULL DEFAULT now()
                    )
                    """
                )
            )
        else:
            columns = {
                column["name"]
                for column in inspector.get_columns("student_deals_survey_responses")
            }
            if "responder_email" not in columns:
                conn.execute(
                    text(
                        "ALTER TABLE student_deals_survey_responses "
                        "ADD COLUMN responder_email TEXT"
                    )
                )
                columns.add("responder_email")

            if "responder_email" in columns:
                conn.execute(
                    text(
                        """
                        CREATE UNIQUE INDEX IF NOT EXISTS
                        ux_student_deals_survey_responses_responder_email
                        ON student_deals_survey_responses (lower(responder_email))
                        """
                    )
                )


if __name__ == "__main__":
    create_student_deals_survey_table()
    print("student_deals_survey_responses table is ready.")
