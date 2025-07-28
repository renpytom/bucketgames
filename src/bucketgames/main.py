# Copyright 2025 Tom Rothamel
#
# Permission is hereby granted, free of charge, to any person
# obtaining a copy of this software and associated documentation files
# (the "Software"), to deal in the Software without restriction,
# including without limitation the rights to use, copy, modify, merge,
# publish, distribute, sublicense, and/or sell copies of the Software,
# and to permit persons to whom the Software is furnished to do so,
# subject to the following conditions:
#
# The above copyright notice and this permission notice shall be
# included in all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
# NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
# LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
# OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
# WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.


import argparse

from . import generate
from . import webserver
from . import upload

def main():

    ap = argparse.ArgumentParser(description="Bucket Games - Self-Host Games on S3-Compatible Storage")
    ap.add_argument("bucket", help="The path to the bucket to initialize or use.")

    sps = ap.add_subparsers(dest="command", required=True)

    sp = sps.add_parser("upload", help="Sync local directory to S3-compatible storage")

    sp = sps.add_parser("generate", help="Generate website files for a bucket")
    sp.add_argument("--serve", action="store_true", help="Serve the generated website files immediately after generation.")

    sp = sps.add_parser("serve", help="Run the web server to serve the website files")

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
