import pathlib
import tomllib

class Credentials:

    key_id: str
    "The key id to use for S3-compatible storage."

    secret_key: str
    "The secret key to use for S3-compatible storage."

    endpoint_url: str
    "The endpoint URL for S3-compatible storage."

    region: str
    "The region for S3-compatible storage, if applicable."

    def __init__(self, bucket: str) -> None:
        """
        Reads credentials from the file 'credentials.toml' in the bucket directorty.

        Args:
            bucket (str): The name of the bucket to read credentials for.
        """

        credentials_file = pathlib.Path(bucket) / "credentials.toml"

        def get(k: str) -> str:
            """
            Returns the value of the key `k` from the credentials file, reporting an error if it is not found.
            """
            if k not in data:
                raise ValueError(f"Missing required key in credentials file: {k}")

            if not isinstance(data[k], str):
                raise ValueError(f"Key '{k}' in credentials file must be a string, got {type(data[k])}")

            return data[k]

        try:
            with open(credentials_file, "rb") as f:
                data = tomllib.load(f)

            self.key_id = get("key_id")
            self.secret_key = get("secret_key")
            self.endpoint_url = get("endpoint_url")
            self.region = get("region") if "region" in data else "auto"

        except FileNotFoundError:
            raise SystemExit(f"Credentials file not found: {credentials_file}")
        except tomllib.TOMLDecodeError as e:
            raise SystemExit(f"Error decoding credentials file: {e}")

def upload_callback(event_type: str, key: str | None = None, error_info: str | None = None) -> None:
    """
    Callback function to handle upload events.

    Args:
        event_type (str): The type of event ("upload", "skip", "delete", "error").
        key (str or None): The relative file path or S3 key involved, or None for general errors.
        error_info (str or None): Error message if event_type is "error", otherwise None.

    Returns:
        None
    """

    if event_type == "uploaded":
        print(f"Uploaded: {key}")
    elif event_type == "deleted":
        print(f"Deleted: {key}")
    elif event_type == "error":
        print(f"Error with {key}: {error_info}")
    elif event_type == "dryrun_upload":
        print(f"Dry run upload: {key}")
    elif event_type == "dryrun_delete":
        print(f"Dry run delete: {key}")

def upload(bucket: str) -> None:
    """
    Uploads a local directory to the specified S3-compatible bucket.
    """

    credentials = Credentials(bucket)

    from bucketgames.s3 import sync_directory_to_s3

    website = pathlib.Path(bucket) / "_website"
    if not website.is_dir():
        raise SystemExit(f"Website directory not found: {website}\nPlease run `bucketgames build <bucket>` first.")

    sync_directory_to_s3(
        local_directory=str(website),
        bucket_name=bucket,
        s3_directory="",
        aws_access_key_id=credentials.key_id,
        aws_secret_access_key=credentials.secret_key,
        endpoint_url=credentials.endpoint_url,
        region_name=credentials.region,
        dry_run=False,
        callback=upload_callback
    )
