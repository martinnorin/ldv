
""" Module for data class for digest. """

from typing import Any, Dict
from dataclasses import dataclass, asdict
from datetime import datetime


@dataclass
class DigestDto:
    """ Data class for versioning values stored in .digest file. """

    timestamp: str
    hexdigest: str
    size: int
    filepath: str
    remote_filepath: str

    def __init__(
        self,
        timestamp: datetime,
        hexdigest: str,
        size: int,
        filepath: str,
        remote_filepath: str
    ) -> None:
        """ Initialize.

        Args:
            timestamp: date and time when version tracking file
            hexdigest: version of file
            size: size of file in bytes
            filepath: relative filepath from path specified in .ldv/config
            remote_filepath: full remote filepath that can be used for
                             locating and downloading the file manually
        """

        self.timestamp = timestamp.isoformat()
        self.hexdigest = hexdigest
        self.size = size
        self.filepath = filepath
        self.remote_filepath = remote_filepath

    def to_dict(self) -> Dict[str, Any]:
        """ Serialize object to dict. """

        return asdict(self)
