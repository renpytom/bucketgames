# Bucket Games
Host games on S3-compatible buckets. 

## Installation

### Prequisites
- Python, version 3.13 recommended (https://www.python.org/downloads/)
- uv (https://docs.astral.sh/uv/getting-started/installation/)
- git (optional)
- R2 OR S3-compatible storage OR storage capable of hosting all your site files.

### Download or Clone the files
/!\ Using the green "Code" button at the top of the github page, the following are available:

#### Option 1: Git

-  Clone the repository `git clone https://github.com/renpytom/bucketgames.git` 
- Switch the folder in the terminal with `cd bucketgames`

#### Option 2: ZIP
- Extract ZIP files to the folder where you'll be working
- Open a terminal in the new "bucketgames" directory

### Install and Run
- Packages will be automatically installed before the first `uv run` command
- Initialize bucket: `uv run bucketgames [bucket name] init`
- More commands `uv run bucketgames --help`

## Add and Configure Games
- Add game: `uv run bucketgames [bucket name] add [game name]`
- Configure the game.toml file created in bucketgames/[bucket]/[game]/game.toml
- Add screenshots for the game to bucketgames/[bucket]/[game]/screenshots (you may have to create the folder)
- Add release downloads to a new folder bucketgames/[bucket]/[game]/[release name], e.g. bucketgames/testbucket/my_game/0.0.1/
- Add game cover image to bucketgames/[bucket]/[game]/cover.jpg or .../cover.png

## Generate and Test Static Site
`uv run bucketgames [bucket name] generate --serve`

# CloudFlare R2 Setup

CloudFlare R2 and Documentation can be found here: https://www.cloudflare.com/developer-platform/products/r2/

Other S3 compatible storage can be used as well.

Add credentials to bucketgames/[bucket]/credentials.toml

# Upload
`uv run bucketgames [bucket name] upload`