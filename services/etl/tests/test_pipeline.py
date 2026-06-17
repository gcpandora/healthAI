import os


def test_data_dir_has_default():
    """DATA_DIR doit avoir une valeur par défaut (indépendant de pandas)."""
    val = os.getenv("DATA_DIR", "/app/data/raw")
    assert val and len(val) > 0


def test_rapport_dir_has_default():
    """RAPPORT_DIR doit avoir une valeur par défaut."""
    val = os.getenv("RAPPORT_DIR", "/app/rapport")
    assert val and len(val) > 0


def test_database_url_format():
    """DATABASE_URL, si définie, doit commencer par postgresql://."""
    url = os.getenv("DATABASE_URL")
    if url:
        assert url.startswith("postgresql://"), f"Format inattendu : {url}"
