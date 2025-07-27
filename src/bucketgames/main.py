import argparse
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


def upload(bucket: str) -> None:
    """
    Uploads a local directory to the specified S3-compatible bucket.
    """

    credentials = Credentials(bucket)

    from bucketgames.s3 import sync_directory_to_s3

    website = pathlib.Path(bucket) / "_website"
    if not website.is_dir():
        raise SystemExit(f"Website directory not found: {website}\nPlease run `bucketgames build <bucket>` first.")

    results = sync_directory_to_s3(
        local_directory=str(website),
        bucket_name=bucket,
        s3_directory="",
        aws_access_key_id=credentials.key_id,
        aws_secret_access_key=credentials.secret_key,
        endpoint_url=credentials.endpoint_url,
        region_name=credentials.region,
        dry_run=False
    )

    print("Upload Results:")

    if results["uploaded"]:
        for i in results["uploaded"]:
            print(f"  - {i}")

    if results["deleted"]:
        print("Deleted files:")
        for i in results["deleted"]:
            print(f"  - {i}")

    if results["errors"]:
        print("Errors:")
        for i in results["errors"]:
            print(f"  - {i}")


def main():

    ap = argparse.ArgumentParser(description="Bucket Games - Self-Host Games on S3-Compatible Storage")
    sps = ap.add_subparsers(dest="command", required=True)

    sp = sps.add_parser("upload", help="Sync local directory to S3-compatible storage")
    sp.add_argument("bucket", help="The name of the bucket to sync up.")

    args = ap.parse_args()

    match args.command:
        case "upload":
            upload(args.bucket)
        case _:
            ap.error("Unknown command.")

    pass
