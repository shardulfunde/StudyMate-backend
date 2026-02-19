from sqlalchemy import inspect, text
from app.db.session import engine


def add_embedding_status_column() -> None:
    inspector = inspect(engine)
    columns = {col["name"] for col in inspector.get_columns("resources")}

    with engine.begin() as conn:
        if "embedding_status" not in columns:
            conn.execute(
                text(
                    "ALTER TABLE resources "
                    "ADD COLUMN embedding_status TEXT NOT NULL DEFAULT 'pending'"
                )
            )

        constraints = {
            c["name"] for c in inspector.get_check_constraints("resources") if c.get("name")
        }
        if "resources_embedding_status_check" not in constraints:
            conn.execute(
                text(
                    "ALTER TABLE resources "
                    "ADD CONSTRAINT resources_embedding_status_check "
                    "CHECK (embedding_status IN ('pending', 'processing', 'completed', 'failed'))"
                )
            )


if __name__ == "__main__":
    add_embedding_status_column()
    print("resources.embedding_status migration applied (if needed).")
