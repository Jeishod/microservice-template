from contextlib import asynccontextmanager
from typing import (
    Any,
    AsyncGenerator,
)

import aioboto3
from botocore.client import ClientError

from services.s3_storage.s3_storage import S3Storage


FILE_NOT_FOUND = "404"
UNSPECIFIED_BUCKET = "unspecified"


class S3Boto3(S3Storage):
    """Implementation of access to c3 repositories using boto3"""

    _session: aioboto3.Session
    # Connection params
    _endpoint: str
    _secure: bool
    _default_bucket: str | None

    def __init__(  # pylint: disable=too-many-arguments
        self,
        endpoint: str,
        access_key: str,
        secret_key: str,
        default_bucket: str | None = None,
        secure: bool = False,
    ) -> None:
        self._endpoint = endpoint
        self._session = aioboto3.Session(
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key,
            region_name="",
        )
        self._secure = secure
        self._default_bucket = default_bucket

    @asynccontextmanager
    async def _resource(self):
        """Global resource manager"""
        async with self._session.resource(
            service_name="s3",
            endpoint_url=self._endpoint,
        ) as resource:
            yield resource

    @asynccontextmanager
    async def _bucket(self, name: str | None = None):
        """
        Connection to the default bucket or passed in arguments

        Args:
            name: target bucket name (if no bucket is specified, the default specified is used)
        """
        bucket_name: str = name or self._default_bucket or UNSPECIFIED_BUCKET
        async with self._resource() as resource:
            bucket = await resource.Bucket(bucket_name)
            yield bucket

    async def is_file_exists(self, filename: str, bucket_name: str | None = None) -> bool:
        """
        Check file exists in storage
        Args
            filename: the name of the file with which it is saved

        Returns:
            bool: True on file exists
        """
        try:
            _bucket_name: str = bucket_name or self._default_bucket or UNSPECIFIED_BUCKET
            async with self._resource() as resource:
                target_object = await resource.Object(_bucket_name, filename)
                await target_object.load()
            return True
        except ClientError as client_error:
            if client_error.response["Error"]["Code"] == "404":
                return False
            raise client_error

    async def put_data(self, filename: str, data: bytes) -> None:
        """
        Put bytes to file in storage. If the file already exists it will be overwritten

        Args
            filename: the name of the file it will be saved with
            data: file content
        """
        async with self._bucket() as bucket:
            target_file = await bucket.Object(filename)
            await target_file.put(Body=data)

    async def put_local_file(self, filename: str, src_path: str) -> None:
        """
        Load file by local path and put it to storage

        Args
            filename: the name of the file it will be saved with
            src_path: local path and filename
        """
        async with self._bucket() as bucket:
            await bucket.upload_file(Key=filename, Filename=src_path)

    async def get_file(self, filename: str) -> bytes:
        """
        Download the entire file from the storage

        Args:
            filename: the name of the file it was saved with

        Return:
            bytes: file content
        """
        async with self._bucket() as bucket:
            target_object = await bucket.Object(filename)
            target_file = await target_object.get()
            file_stream = await target_file["Body"].read()
            return file_stream

    async def get_file_stream(self, filename: str, chunk_size: int) -> AsyncGenerator[Any, bytes]:
        """
        Getting a file from storage in chunks. Generator.

        Args:
            filename: the name of the file it was saved with
            chunk_size: file fragment size

        Return:
            bytes: file chunk content
        """
        async with self._bucket() as bucket:
            target_object = await bucket.Object(filename)
            target_file = await target_object.get()
            while file_chunk := await target_file["Body"].read(chunk_size):
                yield file_chunk

    async def delete_file(self, filename: str) -> None:
        """
        Deleting a saved file from storage. If the file doesn't exist, nothing will happen

        Args:
            filename: the name of the file it was saved with
        """
        async with self._bucket() as bucket:
            target_object = await bucket.Object(filename)
            await target_object.delete()

    async def create_bucket(self, bucket_name: str) -> None:
        """
        Creating a bucket in storage. If the bucket is already created, nothing will happen

        Args:
            bucket_name: the name of the bucket to be created
        """
        async with self._resource() as resource:
            await resource.create_bucket(Bucket=bucket_name)

    async def delete_bucket(self, bucket_name: str) -> None:
        """
        Deleting a bucket in storage. If the bucket doesn't exist, nothing will happen

        Args:
            bucket_name: the name of the bucket to be deleted
        """
        async with self._resource() as resource:
            bucket = await resource.Bucket(bucket_name)
            await bucket.delete()

    async def is_bucket_exists(self, bucket_name: str) -> bool:
        """
        Checking if a bucket exists in storage

        Args:
            bucket_name: the name of the desired bucket
        """
        async with self._resource() as resource:
            try:
                await resource.meta.client.head_bucket(Bucket=bucket_name)
            except ClientError as client_error:
                if client_error.response["Error"]["Code"] == FILE_NOT_FOUND:
                    return False
                raise client_error
        return True
