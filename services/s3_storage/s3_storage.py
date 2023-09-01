from __future__ import annotations

from abc import abstractmethod
from typing import (
    Any,
    AsyncGenerator,
    Protocol,
)


class S3Storage(Protocol):
    """Storage interface"""

    @abstractmethod
    async def is_file_exists(self, filename: str) -> bool:
        """
        Check file exists in storage
        Args
            filename: the name of the file with which it is saved

        Returns:
            bool: True on file exists
        """

    @abstractmethod
    async def put_data(self, filename: str, data: bytes) -> None:
        """
        Put bytes to file in storage

        Args
            filename: the name of the file it will be saved with
            data: file content
        """

    @abstractmethod
    async def put_local_file(self, filename: str, src_path: str) -> None:
        """
        Load file by local path and put it to storage

        Args
            filename: the name of the file it will be saved with
            src_path: local path and filename
        """

    @abstractmethod
    async def get_file(self, filename: str) -> bytes:
        """
        Download the entire file from the storage

        Args:
            filename: the name of the file it was saved with

        Return:
            bytes: file content
        """

    @abstractmethod
    async def get_file_stream(self, filename: str, chunk_size: int) -> AsyncGenerator[Any, bytes]:
        """
        Getting a file from storage in chunks. Generator.

        Args:
            filename: the name of the file it was saved with
            chunk_size: file fragment size

        Return:
            bytes: file chunk content
        """
        yield b""

    @abstractmethod
    async def delete_file(self, filename: str) -> None:
        """
        Deleting a saved file from storage.

        Args:
            filename: the name of the file it was saved with
        """

    @abstractmethod
    async def create_bucket(self, bucket_name: str) -> None:
        """
        Creating a bucket in storage

        Args:
            bucket_name: the name of the bucket to be created
        """

    @abstractmethod
    async def delete_bucket(self, bucket_name: str) -> None:
        """
        Deleting a bucket in storage

        Args:
            bucket_name: the name of the bucket to be deleted
        """

    @abstractmethod
    async def is_bucket_exists(self, bucket_name: str) -> bool:
        """
        Checking if a bucket exists in storage

        Args:
            bucket_name: the name of the desired bucket
        """
