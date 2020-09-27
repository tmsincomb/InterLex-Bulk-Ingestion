from pathlib import Path
from typing import Union, Dict, List, Tuple


def pathing(path: Union[str, Path], new: bool = False) -> Path:
    """ Guarantees correct expansion rules for pathing.
    :param Union[str, Path] path: path of folder or file you wish to expand.
    :param bool new: will check if distination exists if new
        (will check parent path regardless).
    :return: A pathlib.Path object.
    :example:
    >>> pathing('~/Desktop/folderofgoodstuffs/')
    /home/user/Desktop/folderofgoodstuffs
    """
    path = Path(path)
    # Expand tilda shortened path or local path.
    if str(path)[0] == '~':
        path = path.expanduser()
    else:
        path = path.absolute() #
    # Make sure new paths don't existing & existing paths actually exist.
    if new:
        if not path.parent.exists():
            raise ValueError(f'ERROR ::: Parent directory of {path} does not exist.')
        if path.exists():
            raise ValueError(f'ERROR ::: {path} already exists!')
    else:
        if not path.exists():
            raise ValueError(f'ERROR ::: Path {path} does not exist.')
    return path