from __future__ import annotations

from app.db.session import SessionLocal
from app.fixtures.development import seed_development_content


def main() -> None:
    with SessionLocal.begin() as session:
        created = seed_development_content(session)
    print("development fixtures created" if created else "development fixtures already exist")


if __name__ == "__main__":
    main()
