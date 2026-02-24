from sqlalchemy import inspect, text
from app.db.session import engine


def add_subject_approval_columns() -> None:
    inspector = inspect(engine)
    columns = {col["name"] for col in inspector.get_columns("subjects")}

    with engine.begin() as conn:
        if "approval_status" not in columns:
            conn.execute(
                text(
                    "ALTER TABLE subjects "
                    "ADD COLUMN approval_status TEXT"
                )
            )

        conn.execute(
            text(
                "UPDATE subjects "
                "SET approval_status = 'approved' "
                "WHERE approval_status IS NULL"
            )
        )

        conn.execute(
            text(
                "ALTER TABLE subjects "
                "ALTER COLUMN approval_status SET DEFAULT 'pending'"
            )
        )

        conn.execute(
            text(
                "ALTER TABLE subjects "
                "ALTER COLUMN approval_status SET NOT NULL"
            )
        )

        if "approved_by" not in columns:
            conn.execute(
                text(
                    "ALTER TABLE subjects "
                    "ADD COLUMN approved_by VARCHAR"
                )
            )

        if "approved_at" not in columns:
            conn.execute(
                text(
                    "ALTER TABLE subjects "
                    "ADD COLUMN approved_at TIMESTAMP"
                )
            )

        if "rejection_reason" not in columns:
            conn.execute(
                text(
                    "ALTER TABLE subjects "
                    "ADD COLUMN rejection_reason TEXT"
                )
            )

        constraints = {
            c["name"] for c in inspector.get_check_constraints("subjects") if c.get("name")
        }
        if "subjects_approval_status_check" not in constraints:
            conn.execute(
                text(
                    "ALTER TABLE subjects "
                    "ADD CONSTRAINT subjects_approval_status_check "
                    "CHECK (approval_status IN ('pending', 'approved', 'rejected'))"
                )
            )


if __name__ == "__main__":
    add_subject_approval_columns()
    print("subjects approval columns migration applied (if needed).")
