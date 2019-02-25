from pathlib import Path

# Everything in "fixures" gets loaded as a plugin
pytest_plugins = [
	f"fixtures.{path.stem}" for path in Path(__file__).parent.glob("fixtures/*.py")
	if path.stem != "__init__"
]
