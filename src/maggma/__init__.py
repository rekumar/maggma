""" Primary Maggma module """
from importlib.metadata import version, PackageNotFoundError

try:
    __version__ = version('maggma')
except PackageNotFoundError:  # pragma: no cover
    # package is not installed
    pass
