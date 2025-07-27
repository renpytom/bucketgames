import pathlib
import shutil

def generate_game(game: pathlib.Path, website: pathlib.Path) -> None:
    """
    Generates the website files for a specific game.
    """

    if not game.is_dir():
        raise SystemExit(f"Game directory not found: {game}")

    if website.is_dir():
        shutil.rmtree(website)

    website.mkdir()

    downloads = game / "downloads"

    if downloads.is_dir():
        shutil.copytree(downloads, website / "downloads")

    print(f"Game files for {game.name} generated successfully.")

def generate(bucket: str) -> None:
    """
    Generates the website files for the specified bucket.
    """

    path = pathlib.Path(bucket)
    website = path / "_website"

    website.mkdir(exist_ok=True)

    for i in path.iterdir():

        if i.is_dir() and not i.name[0] in ("_", "."):
            generate_game(i, website / i.name)

    print("Website files generated successfully.")
