"""Unit tests verifying Alembic migration configuration and revision chain."""

import importlib
from unittest.mock import patch

from alembic.config import Config
from alembic.script import ScriptDirectory

from migrations.env import get_migration_url


def test_alembic_config_and_revisions() -> None:
    alembic_cfg = Config("alembic.ini")
    script = ScriptDirectory.from_config(alembic_cfg)

    # Verify head revision is 0006
    heads = script.get_heads()
    assert heads == ["0006"]

    rev_0006 = script.get_revision("0006")
    assert rev_0006 is not None
    assert rev_0006.down_revision == "0005"
    assert rev_0006.doc is not None
    assert "datasets" in rev_0006.doc.lower()

    # Verify revision 0005 metadata
    rev_0005 = script.get_revision("0005")
    assert rev_0005 is not None
    assert rev_0005.down_revision == "0004"
    assert rev_0005.doc is not None
    assert "game system tables" in rev_0005.doc.lower()

    # Verify revision 0004 metadata
    rev_0004 = script.get_revision("0004")
    assert rev_0004 is not None
    assert rev_0004.down_revision == "0003"
    assert rev_0004.doc is not None
    assert "district crop stats" in rev_0004.doc.lower()

    # Verify revision 0003 metadata
    rev_0003 = script.get_revision("0003")
    assert rev_0003 is not None
    assert rev_0003.down_revision == "0002"
    assert rev_0003.doc is not None
    assert "regions" in rev_0003.doc.lower()

    # Verify revision 0002 metadata
    rev_0002 = script.get_revision("0002")
    assert rev_0002 is not None
    assert rev_0002.down_revision == "0001"
    assert rev_0002.doc is not None
    assert "users" in rev_0002.doc.lower()

    # Verify revision 0001 metadata
    rev_0001 = script.get_revision("0001")
    assert rev_0001 is not None
    assert rev_0001.down_revision is None
    assert rev_0001.doc is not None
    assert "postgis" in rev_0001.doc.lower()


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
