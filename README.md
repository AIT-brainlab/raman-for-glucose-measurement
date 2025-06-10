# Raman-for-glucose-measurement
This is a repository for all necessary Raman experiment

## For Raman starter

Are you new to Raman?
If yes, this section is for you.

What you need to know about Raman is compiled [here](https://github.com/AIT-brainlab/raman-for-glucose-measurement/wiki)

## How to use this repository

This repository use `devcontainer`.
To start developing `Python`, simply spawn a container with <kbd>Ctrl+Shift+P</kbd> and select `Dev Containers:  Rebuild and Reopen in Container` then select `Python`.

After the container started, you will have to run `uv sync` to rebuild the dependencies.
Two things will happen:
1. `.venv/` and `.python` will be created in the root direcoty
2. All python dependencies will be installed in the `.venv/` directory and `python` will be installed in `.python/` directory.

`uv` does not care much about Python system, it simply downloads a new one and symlink from `.python/` to the `.venv/` directory.
This means experimenting with Python version is easy and fast because they are all isolated in the `.venv/` and `.python/` directory.

To change python version, first, get the python version `uv python install <version>` then use `uv python pin <version>` to pin the version.
This will create a `.python-version` file in the root directory.
Recreate the environment with `uv sync` to reinstall the dependencies.