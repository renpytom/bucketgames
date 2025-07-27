from typing import Any

import dataclasses
import datetime
import dateutil.parser
import packaging.version
import pathlib
import re
import shutil
import tomllib

from jinja2 import Environment, select_autoescape, FileSystemLoader, ChoiceLoader, PackageLoader

# Globals.
bucket_path: pathlib.Path


class Proxy():
    """
    Proxies attributes through to the underlying object or its toml attribute.
    """

    def __init__(self, target: Any):
        self.target = target

    def __getattr__(self, field: str):
        """
        Returns the value of the field from the underlying object or its toml attribute.
        """

        if hasattr(self.target, field):
            return getattr(self.target, field)

        if hasattr(self.target, "toml") and field in self.target.toml:
            return self.target.toml[field]

        raise AttributeError(field, self)

@dataclasses.dataclass
class File:
    """
    Represents a file inside a release.
    """

    directory: str
    "The path to the file, relative to the bucket root, using forward slashes."

    size: int
    "The size of the file in bytes."

    date: datetime.datetime
    "The date of the file, typically the last modified date."



@dataclasses.dataclass
class Release:
    """
    Represents a release.
    """

    path: pathlib.Path
    "The path to the release directory."

    directory: str
    "The path to the release directory, relative to the bucket root, using forward slashes."

    version: packaging.version.Version
    "The version of the release."

    date: datetime.datetime
    "The date of the release."

    files: list[File]
    "The files in the release."

    toml: dict[str, Any]
    "The contents of the release's `release.toml` file, if it exists."

    def proxy(self) -> Proxy:
        """
        Returns a Proxy object for this release, allowing access to its attributes and toml keys.
        """
        return Proxy(self)

linked: set[pathlib.Path]
"""A set of paths that have already been linked using Game.link(), and so don't need to be copied again."""

@dataclasses.dataclass
class Game:
    """
    Represents a game.
    """

    path: pathlib.Path
    "The path to the game directory."

    website_path: pathlib.Path
    "The path to the website directory for this game."

    date: datetime.datetime
    "The date of the game. Typically the date of the latest release, unless overridden."

    releases: list[Release]
    "The releases of the game."

    toml: dict[str, Any]
    "The contents of the game's `game.toml` file, if it exists."

    def proxy(self) -> Proxy:
        """
        Returns a Proxy object for this game, allowing access to its attributes and toml keys.
        """
        rv = Proxy(self)
        rv.releases = [r.proxy() for r in self.releases]
        return rv

    def link(self, filename: str) -> str | None:
        """
        Looks for a file with the given filename in the game's directory. If it exists, returns
        the path (relative to the game) to the file with the extension. Otherwise, returns None.

        As a side effect, it will also copy the file to the website directory if it exists.
        """

        file_path = self.path / filename

        if file_path.is_file():
            destination = self.website_path / filename

            if not destination in linked:
                shutil.copy(file_path, destination)
                linked.add(destination)

            return filename

        return None

    def image_link(self, base: str) -> str | None:
        """
        Looks for an image file with the given base name in the game's directory.
        If it exists, returns the path (relative to the game) to the image file with the extension.
        Otherwise, returns None.

        As a side effect, it will also copy the image file to the website directory if it exists.
        """

        image_extensions = self.toml["image_extensions"]

        for ext in image_extensions:
            image_link = self.link(base + ext)
            if image_link:
                return image_link

        return None


def apply_template(destination: pathlib.Path, template: str, game_path: pathlib.Path|None=None, **kwargs: Any):
    """
    Locates a Jinja2 template file, renders it with the given keyword arguments, and writes the result to a file.

    `destination`
        The path to the file where the rendered template will be written.

    `template`
        The name of the template file to render. This should be a Jinja2 template. This is also the output
        filename in the `destination` directory.

    `game_path`
        The path to the game directory. If provided, this will be used to load templates from the game directory.
        If not provided, only the bucket directory and package templates will be used.

    Keyword arguments are passed to the Jinja2 template for rendering.
    """

    loaders = [ ]
    if game_path:
        loaders.append(FileSystemLoader(str(game_path)))
    loaders.append(FileSystemLoader(str(bucket_path)))
    loaders.append(PackageLoader("bucketgames", "templates"))

    env = Environment(
        loader=ChoiceLoader(loaders),
        autoescape=select_autoescape(['html', 'xml'])
    )

    t = env.get_template(template)

    rendered = t.render(**kwargs)

    destination.write_text(rendered, encoding="utf-8")

def scan_release(game_path: pathlib.Path, release_path: pathlib.Path) -> Release:
    """
    Scans a release directory and returns a Release object.
    """

    release_toml_path = release_path / "release.toml"
    if release_toml_path.is_file():
        try:
            with open(release_toml_path, "rb") as f:
                toml = tomllib.load(f)
        except tomllib.TOMLDecodeError as e:
            raise SystemExit(f"Error decoding release.toml: {e}")

    else:
        toml = {}

    # The extensions for the files in the release.
    extensions = toml.get("suffixes", [ ".gz", "bz2", ".xz", ".zip", ".apk", ".ipak", ".pdf", ".txt" ])

    max_date = datetime.datetime.fromtimestamp(0)
    files: list[File] = []

    for file_path in release_path.iterdir():
        if not file_path.suffix in extensions:
            continue

        if not file_path.is_file():
            continue

        file_stat = file_path.stat()
        file_date = datetime.datetime.fromtimestamp(file_stat.st_mtime)

        files.append(File(
            directory=str(file_path.relative_to(game_path)).replace('\\', '/'),
            size=file_stat.st_size,
            date=file_date
        ))

    if not files:
        raise SystemExit(f"No downloadable files found in release directory: {release_path}")

    # Determine the version.
    if "version" in toml:
        try:
            version = packaging.version.parse(toml["version"])
        except packaging.version.InvalidVersion as e:
            raise SystemExit(f"Invalid version format in release.toml: {e}")

    elif m := re.search(r"-(.*?)-dists$", release_path.name):
        try:
            version = packaging.version.parse(m.group(1))
        except packaging.version.InvalidVersion as e:
            raise SystemExit(f"Invalid version format in directory name '{release_path.name}'.")

    else:
        try:
            version = packaging.version.parse(release_path.name)
        except packaging.version.InvalidVersion as e:
            raise SystemExit(f"Invalid version format in directory name '{release_path.name}'.")

    # Determine the release date.
    if "date" in toml:
        try:
            release_date = dateutil.parser.parse(toml["date"])
        except ValueError as e:
            raise SystemExit(f"Invalid date key format in {release_toml_path}: {e}")
    else:
        if not files:
            raise SystemExit(f"No files found in release directory: {release_path}")

        release_date = max(f.date for f in files)

    return Release(
        path=release_path,
        directory=str(release_path.relative_to(game_path)).replace('\\', '/'),
        version=version,
        date=release_date,
        files=files,
        toml=toml
    )

def generate_game(game_path: pathlib.Path, website_path: pathlib.Path) -> Game:
    """
    Generates the website files for a specific game.
    """

    game_toml_path = game_path / "game.toml"
    try:
        with open(game_toml_path, "rb") as f:
            game_toml = tomllib.load(f)
    except tomllib.TOMLDecodeError as e:
        raise SystemExit(f"Error decoding {game_toml_path}: {e}")

    game_toml.setdefault("image_extensions", [".png", ".jpg", ".jpeg", ".gif", ".webp"])

    if website_path.is_dir():
        shutil.rmtree(website_path)

    website_path.mkdir()

    # Copy subdirectories over to the website, and scan for releases.

    releases: list[Release] = []

    for d in game_path.iterdir():

        if not d.is_dir() or d.name.startswith(("_", ".")):
            continue

        if re.match(r'\d', d.name) or re.search(r'-dists$', d.name) or (d / "release.toml").is_file():
            release = scan_release(game_path, d)
            releases.append(release)

        shutil.copytree(d, website_path / d.name)

    releases.sort(key=lambda r: r.date, reverse=True)

    # Title.

    if "title" not in game_toml:
        raise SystemExit(f"Missing 'title' key in {game_toml_path}.")

    # Date.

    if "date" in game_toml:
        try:
            date = dateutil.parser.parse(game_toml["date"])
        except ValueError as e:
            raise SystemExit(f"Invalid date key format in {game_toml_path}: {e}")

    else:
        if not releases:
            raise SystemExit(f"No date and no releases for: {game_path}")

        date = max(r.date for r in releases)

    # Create the game object.

    game = Game(
        path=game_path,
        website_path=website_path,
        date=date,
        releases=releases,
        toml=game_toml
    )

    proxy = game.proxy()

    apply_template(
        destination=website_path / "index.html",
        template="game.html",
        game_path=game_path,
        game=proxy,
    )

    apply_template(
        destination=website_path / "style.css",
        template="style.css",
        game_path=game_path,
        game=proxy,
    )

    return game

def generate(bucket: str) -> None:
    """
    Generates the website files for the specified bucket.
    """

    global bucket_path

    bucket_path = pathlib.Path(bucket)
    website = bucket_path / "_website"

    website.mkdir(exist_ok=True)

    for i in bucket_path.iterdir():

        if (i / "game.toml").is_file():
            generate_game(i, website / i.name)

    print("Website files generated successfully.")
