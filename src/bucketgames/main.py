import argparse

from . import generate
from . import webserver
from . import upload

def main():

    ap = argparse.ArgumentParser(description="Bucket Games - Self-Host Games on S3-Compatible Storage")
    sps = ap.add_subparsers(dest="command", required=True)

    sp = sps.add_parser("upload", help="Sync local directory to S3-compatible storage")
    sp.add_argument("bucket", help="The name of the bucket to sync up.")

    sp = sps.add_parser("generate", help="Generate website files for a bucket")
    sp.add_argument("bucket", help="The name of the bucket to generate website files for.")
    sp.add_argument("--serve", action="store_true", help="Serve the generated website files immediately after generation.")

    sp = sps.add_parser("serve", help="Run the web server to serve the website files")
    sp.add_argument("bucket", help="The name of the bucket to server.")

    args = ap.parse_args()

    match args.command:
        case "upload":
            upload.upload(args.bucket)
        case "generate":
            generate.generate(args.bucket)
            if args.serve:
                webserver.start(args.bucket)
        case "serve":
            webserver.start(args.bucket)
        case _:
            ap.error("Unknown command.")

    pass
