from __future__ import annotations

from app.core.config import get_settings
from app.db.session import SessionLocal
from app.services.admin_auth import (
    InitialAdministratorConfigurationError,
    provision_initial_administrator,
)


def main() -> None:
    with SessionLocal.begin() as session:
        try:
            administrator = provision_initial_administrator(session, get_settings())
        except InitialAdministratorConfigurationError as error:
            raise SystemExit(str(error)) from error
    print(f"initial administrator ensured for {administrator.email}")


if __name__ == "__main__":
    main()
