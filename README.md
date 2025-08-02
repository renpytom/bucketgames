# Bucket Games
Host games on S3-compatible buckets. 

## Installation

### Prequisites

- Python, version 3.13 recommended (https://www.python.org/downloads/)
- uv (https://docs.astral.sh/uv/getting-started/installation/)
- git (optional)
- R2 OR S3-compatible storage OR storage capable of hosting all site files.

### Download or Clone the files

#### Option 1: Git Clone

-  Clone the repository `git clone https://github.com/renpytom/bucketgames.git` 
    - Developers: please use ssh to allow pushing
- Switch to the folder in the terminal with `cd bucketgames`

#### Option 2: Download ZIP 

- Click the green "Code" button at the top of the GitHub page, and find the "Download ZIP" option. Download the ZIP file by clicking on it.
    - Alternatively, the ZIP file should be available at: https://github.com/renpytom/bucketgames/archive/refs/heads/main.zip
- Extract the ZIP file to an appropriate directory
- Open a terminal in the newly extracted "bucketgames" directory

### Install

Prequisite packages will be automatically installed with uv before the first `uv run` command
- Create bucket: `uv run bucketgames [bucket name] init`
- More commands `uv run bucketgames --help`

## Add and Configure Games

- Add game: `uv run bucketgames [bucket name] add [game name]`
- Configure the game.toml file created in `bucketgames/[bucket]/[game]/game.toml`
- Add screenshots for the game to `bucketgames/[bucket]/[game]/screenshots` (you may have to create the folder)
- Add release downloads to a new folder `bucketgames/[bucket]/[game]/[release name]`, e.g. `bucketgames/testbucket/my_game/0.0.1/`
- Add game cover image to `bucketgames/[bucket]/[game]/cover.jpg` or `.../cover.png`

## Generate and Test Static Site
`uv run bucketgames [bucket name] generate --serve`

# Cloud Setup

CloudFlare R2 and Documentation can be found here: https://www.cloudflare.com/developer-platform/products/r2/

Other S3-compatible storage can be used as well.

Add S3-compatible credentials to `bucketgames/[bucket]/credentials.toml`

## Static Site (Not S3-Compatible)

If using site hosting that isn't S3-compatible, the `bucketgames/[bucket]/_website` folder can be uploaded as-is.  
Please be sure to:

1. Run `uv run bucketgames [bucket] generate` prior to upload
2. Ensure there is enough storage and bandwidth available on your hosting including for downloads
3. Ensure your hosting allows for your use-case

# Upload

`uv run bucketgames [bucket name] upload`

Once complete, the site will be available at the public bucket URL.