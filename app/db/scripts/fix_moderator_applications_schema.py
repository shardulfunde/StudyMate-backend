from sqlalchemy import inspect, text

from app.db.session import engine


def fix_moderator_applications_schema() -> None:
    inspector = inspect(engine)
    columns = {col["name"]: col for col in inspector.get_columns("moderator_applications")}

    with engine.begin() as conn:
        if "requested_scope_type" not in columns:
            conn.execute(
                text(
                    "ALTER TABLE moderator_applications "
                    "ADD COLUMN requested_scope_type TEXT"
                )
            )

        if "requested_scope_id" not in columns:
            conn.execute(
                text(
                    "ALTER TABLE moderator_applications "
                    "ADD COLUMN requested_scope_id UUID"
                )
            )

        full_name_col = columns.get("full_name")
        if full_name_col and not full_name_col.get("nullable", True):
            conn.execute(
                text(
                    "ALTER TABLE moderator_applications "
                    "ALTER COLUMN full_name DROP NOT NULL"
                )
            )


if __name__ == "__main__":
    fix_moderator_applications_schema()
    print("moderator_applications schema migration applied (if needed).")
