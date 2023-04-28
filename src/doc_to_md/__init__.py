from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version("doc_to_readme")
except PackageNotFoundError:
    pass
