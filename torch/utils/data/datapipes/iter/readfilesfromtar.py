from torch.utils.data import IterDataPipe
from torch.utils.data.datapipes.utils.common import validate_pathname_binary_tuple
from typing import Iterable, Iterator, Tuple, Optional, IO, cast
from io import BufferedIOBase

import os
import tarfile
import warnings

class ReadFilesFromTarIterDataPipe(IterDataPipe[Tuple[str, BufferedIOBase]]):
    r""":class:`ReadFilesFromTarIterDataPipe`.

    Iterable datapipe to extract tar binary streams from input iterable which contains tuples of
    pathname and tar binary stream, yields pathname and extracted binary stream in a tuple.
    args:
        datapipe: Iterable datapipe that provides pathname and tar binary stream in tuples
        mode: File mode used by `tarfile.open` to read file object. Mode has to be a string of the form 'filemode[:compression]'
        length: a nominal length of the datapipe

    Note:
        The opened file handles will be closed automatically if the default DecoderDataPipe
        is attached. Otherwise, user should be responsible to close file handles explicitly
        or let Python's GC close them periodly.
    """
    def __init__(
        self,
        datapipe : Iterable[Tuple[str, BufferedIOBase]],
        mode: str = "r:*",
        length : int = -1
    ):
        super().__init__()
        self.datapipe: Iterable[Tuple[str, BufferedIOBase]] = datapipe
        self.mode = mode
        self.length: int = length

    def __iter__(self) -> Iterator[Tuple[str, BufferedIOBase]]:
        if not isinstance(self.datapipe, Iterable):
            raise TypeError("datapipe must be Iterable type but got {}".format(type(self.datapipe)))
        for data in self.datapipe:
            validate_pathname_binary_tuple(data)
            pathname, data_stream = data
            try:
                # typing.cast is used here to silence mypy's type checker
                tar = tarfile.open(fileobj=cast(Optional[IO[bytes]], data_stream), mode=self.mode)
                for tarinfo in tar:
                    if not tarinfo.isfile():
                        continue
                    extracted_fobj = tar.extractfile(tarinfo)
                    if extracted_fobj is None:
                        warnings.warn("failed to extract file {} from source tarfile {}".format(tarinfo.name, pathname))
                        raise tarfile.ExtractError
                    inner_pathname = os.path.normpath(os.path.join(pathname, tarinfo.name))
                    # Add a reference of the source tarfile into extracted_fobj, so the source
                    # tarfile handle won't be released until all the extracted file objs are destroyed.
                    extracted_fobj.source_ref = tar  # type: ignore[attr-defined]
                    # typing.cast is used here to silence mypy's type checker
                    yield (inner_pathname, cast(BufferedIOBase, extracted_fobj))
            except Exception as e:
                warnings.warn(
                    "Unable to extract files from corrupted tarfile stream {} due to: {}, abort!".format(pathname, e))
                raise e

    def __len__(self):
        if self.length == -1:
            raise TypeError("{} instance doesn't have valid length".format(type(self).__name__))
        return self.length
