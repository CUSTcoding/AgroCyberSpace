"""Unit tests verifying Alembic migration configuration and revision chain."""

import importlib
from unittest.mock import patch

from alembic.config import Config
from alembic.script import ScriptDirectory

from migrations.env import get_migration_url


def test_alembic_config_and_revisions() -> None:
    alembic_cfg = Config("alembic.ini")
    script = ScriptDirectory.from_config(alembic_cfg)

    # Verify head revision is 0001
    heads = script.get_heads()
    assert heads == ["0001"]

    # Verify revision 0001 metadata
    rev = script.get_revision("0001")
    assert rev is not None
    assert rev.down_revision is None
    assert rev.doc is not None
    assert "postgis" in rev.doc.lower()


def test_migration_0001_has_upgrade_and_downgrade() -> None:
    migration_0001 = importlib.import_module("migrations.versions.0001_enable_postgis")
    assert hasattr(migration_0001, "upgrade")
    assert hasattr(migration_0001, "downgrade")
    assert callable(migration_0001.upgrade)
    assert callable(migration_0001.downgrade)


def test_get_migration_url_selection() -> None:
    # 1. When DIRECT is set, it takes precedence
    with patch("migrations.env.settings.DATABASE_URL_DIRECT", "postgresql://direct-host/db"):
        with patch("migrations.env.settings.DATABASE_URL", "postgresql://pooler-host/db"):
            url = get_migration_url()
            assert url == "postgresql+psycopg://direct-host/db"

    # 2. When DIRECT is not set, DATABASE_URL is used
    with patch("migrations.env.settings.DATABASE_URL_DIRECT", None):
        with patch("migrations.env.settings.DATABASE_URL", "postgresql://pooler-host/db"):
            url = get_migration_url()
            assert url == "postgresql+psycopg://pooler-host/db"
