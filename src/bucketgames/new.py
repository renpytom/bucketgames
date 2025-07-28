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

import importlib.resources
import pathlib


def copy(resource: str, destination: pathlib.Path):
    """
    Copy a resource file from the package to the specified destination.
    """

    resource_path = importlib.resources.files("bucketgames") / "resources" / resource
    resource_text = resource_path.read_text()
    destination.write_text(resource_text)


def init_bucket(bucket: str):
    """
    Initialize a new bucket directory structure.
    """

    bucket_path = pathlib.Path(bucket)

    if bucket_path.exists():
        raise FileExistsError(f"Bucket directory '{bucket}' already exists, cannot initialize.")

    # Create the bucket directory
    bucket_path.mkdir(parents=True, exist_ok=True)

    # Copy default contents.
    copy("credentials.toml", bucket_path / "credentials.toml")
    copy("bucket.toml", bucket_path / "bucket.toml")
    copy("gitignore", bucket_path / ".gitignore")


def add_game(bucket: str, game_name: str):
    """
    Add a new game to the bucket.
    """

    bucket_path = pathlib.Path(bucket)

    if not bucket_path.exists():
        raise FileNotFoundError(f"Bucket directory '{bucket}' does not exist.")

    game_path = bucket_path / game_name

    if game_path.exists():
        raise FileExistsError(f"Game '{game_name}' already exists in bucket '{bucket}'.")

    # Create the game directory
    game_path.mkdir(parents=True, exist_ok=True)

    # Copy default game files
    copy("game.toml", game_path / "game.toml")
