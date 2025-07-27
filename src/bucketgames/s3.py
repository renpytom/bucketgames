"""
S3-Compatible Storage Synchronization Functions

Supports AWS S3, Cloudflare R2, Backblaze B2, MinIO, and other S3-compatible services.

USAGE EXAMPLES:

1. AWS S3 (using environment variables for credentials):
    from bucketgames.s3 import sync_directory_to_s3

    results = sync_directory_to_s3(
        local_directory="/path/to/local/folder",
        bucket_name="my-aws-bucket",
        s3_directory="backup/data",
        region_name="us-west-2",
        dry_run=True  # Preview changes first
    )

2. Cloudflare R2:
    from bucketgames.s3 import sync_directory_to_s3

    results = sync_directory_to_s3(
        local_directory="/path/to/local/folder",
        bucket_name="my-r2-bucket",
        s3_directory="backup",
        aws_access_key_id="your_r2_access_key",
        aws_secret_access_key="your_r2_secret_key",
        endpoint_url="https://your-account-id.r2.cloudflarestorage.com",
        region_name="auto",
        dry_run=True
    )

3. Backblaze B2:
    from bucketgames.s3 import sync_directory_to_s3

    results = sync_directory_to_s3(
        local_directory="/path/to/local/folder",
        bucket_name="my-b2-bucket",
        s3_directory="backup",
        aws_access_key_id="your_key_id",
        aws_secret_access_key="your_application_key",
        endpoint_url="https://s3.us-west-002.backblazeb2.com",
        region_name="us-west-002",
        dry_run=True
    )
"""

import os
import hashlib
from pathlib import Path
from typing import Optional, Dict, Any
import boto3
from botocore.exceptions import ClientError, NoCredentialsError
from botocore.config import Config


def sync_directory_to_s3(
    local_directory: str,
    bucket_name: str,
    s3_directory: str = "",
    aws_access_key_id: Optional[str] = None,
    aws_secret_access_key: Optional[str] = None,
    aws_session_token: Optional[str] = None,
    region_name: str = "us-east-1",
    endpoint_url: Optional[str] = None,
    delete_missing: bool = False,
    dry_run: bool = False,
    callback=None
) -> None:
    """
    Synchronize a local directory with an S3-compatible bucket directory.

    Supports AWS S3, Cloudflare R2, Backblaze B2, and other S3-compatible services.

    Args:
        local_directory: Path to the local directory to sync
        bucket_name: Name of the S3 bucket
        s3_directory: Directory path within the S3 bucket (optional, defaults to root)
        aws_access_key_id: Access key ID (optional, can use environment variables)
        aws_secret_access_key: Secret access key (optional, can use environment variables)
        aws_session_token: Session token (optional, for temporary credentials)
        region_name: Region name (default: us-east-1)
        endpoint_url: Custom endpoint URL for S3-compatible services
                     Examples:
                     - Cloudflare R2: "https://<account-id>.r2.cloudflarestorage.com"
                     - Backblaze B2: "https://s3.<region>.backblazeb2.com"
                     - MinIO: "http://localhost:9000"
        delete_missing: Whether to delete files in S3 that don't exist locally
        dry_run: If True, only show what would be done without making changes
        callback: Function to call after each operation. Signature:

            callback(event_type, key, error_info)

            Where:
                event_type (str): One of:
                    "uploaded"       - File was uploaded to S3
                    "skipped"        - File was already up to date, skipped
                    "deleted"        - File was deleted from S3
                    "dryrun_upload"  - File would be uploaded (dry run)
                    "dryrun_delete"  - File would be deleted (dry run)
                    "error"          - An error occurred
                key (str or None): The relative file path or S3 key involved, or None for general errors
                error_info (str or None): Error message if event_type is "error", otherwise None

    Returns:
        None
    """
    # No results dict; use callback for reporting

    # Validate local directory
    local_path = Path(local_directory)
    if not local_path.exists():
        raise FileNotFoundError(f"Local directory does not exist: {local_directory}")
    if not local_path.is_dir():
        raise NotADirectoryError(f"Path is not a directory: {local_directory}")

    # Initialize S3 client
    try:
        session_kwargs = {}
        if aws_access_key_id and aws_secret_access_key:
            session_kwargs.update({
                'aws_access_key_id': aws_access_key_id,
                'aws_secret_access_key': aws_secret_access_key
            })
            if aws_session_token:
                session_kwargs['aws_session_token'] = aws_session_token

        # Create S3 client with optional custom endpoint
        client_kwargs = {
            'service_name': 's3',
            'region_name': region_name,
            **session_kwargs
        }
        if endpoint_url:
            client_kwargs['endpoint_url'] = endpoint_url
            # For non-AWS services, we might need to disable SSL verification
            # and use path-style addressing
            client_kwargs['config'] = Config(
                s3={'addressing_style': 'path'}
            )

        s3_client = boto3.client(**client_kwargs)

        # Test connection
        s3_client.head_bucket(Bucket=bucket_name)

    except NoCredentialsError:
        raise NoCredentialsError()
    except ClientError as e:
        if e.response['Error']['Code'] == '404':
            raise ValueError(f"Bucket '{bucket_name}' does not exist or is not accessible")
        else:
            raise e

    # Normalize S3 directory path
    s3_prefix = s3_directory.strip('/') + '/' if s3_directory else ''

    # Get existing S3 objects
    s3_objects = {}
    try:
        paginator = s3_client.get_paginator('list_objects_v2')
        for page in paginator.paginate(Bucket=bucket_name, Prefix=s3_prefix):
            for obj in page.get('Contents', []):
                # Remove the prefix to get relative path
                relative_key = obj['Key'][len(s3_prefix):] if s3_prefix else obj['Key']
                if relative_key:  # Skip empty keys (directory markers)
                    s3_objects[relative_key] = {
                        'etag': obj['ETag'].strip('"'),
                        'size': obj['Size'],
                        'last_modified': obj['LastModified']
                    }
    except ClientError as e:
        if callback:
            callback("error", None, f"Error listing S3 objects: {e}")
        return

    # Track which S3 objects we've seen during sync
    synced_s3_objects = set()

    # Walk through local directory
    for root, dirs, files in os.walk(local_directory):
        for file in files:
            local_file_path = Path(root) / file
            relative_path = local_file_path.relative_to(local_path)
            s3_key = s3_prefix + str(relative_path).replace('\\', '/')
            relative_key = str(relative_path).replace('\\', '/')

            synced_s3_objects.add(relative_key)

            try:
                # Calculate local file MD5
                local_md5 = _calculate_md5(local_file_path)
                local_size = local_file_path.stat().st_size

                # Check if file needs to be uploaded
                needs_upload = True
                if relative_key in s3_objects:
                    s3_etag = s3_objects[relative_key]['etag']
                    s3_size = s3_objects[relative_key]['size']

                    # Compare MD5 and size
                    if local_md5 == s3_etag and local_size == s3_size:
                        needs_upload = False
                        if callback:
                            callback("skipped", relative_key, None)

                if needs_upload:
                    if dry_run:
                        if callback:
                            callback("dryrun_upload", relative_key, None)
                    else:
                        try:
                            s3_client.upload_file(
                                str(local_file_path),
                                bucket_name,
                                s3_key
                            )
                            if callback:
                                callback("uploaded", relative_key, None)
                        except Exception as e:
                            if callback:
                                callback("error", relative_key, f"Upload failed: {e}")

            except Exception as e:
                if callback:
                    callback("error", relative_key, f"Error processing {relative_key}: {e}")

    # Handle deletion of files that exist in S3 but not locally
    if delete_missing:
        for s3_relative_key in s3_objects:
            if s3_relative_key not in synced_s3_objects:
                s3_key = s3_prefix + s3_relative_key
                if dry_run:
                    if callback:
                        callback("dryrun_delete", s3_relative_key, None)
                else:
                    try:
                        s3_client.delete_object(Bucket=bucket_name, Key=s3_key)
                        if callback:
                            callback("deleted", s3_relative_key, None)
                    except ClientError as e:
                        if callback:
                            callback("error", s3_relative_key, f"Error deleting {s3_relative_key}: {e}")

    # No return value


def _calculate_md5(file_path: Path) -> str:
    """Calculate MD5 hash of a file."""
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()
