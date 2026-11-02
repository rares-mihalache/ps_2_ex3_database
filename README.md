# PS 2 Ex 3

# Setup

## Environment

This project uses [Pixi](https://pixi.sh) for the environment. Install Pixi if you
do not have it yet, then from the repository root run:

```bash
pixi install
```

Activate the environment by running:

```bash
pixi shell
```

You can also run commands without activating the shell, for example
`pixi run python nba/data_loader.py ...`.

## Pre-commit

This repository uses pre-commit to run some checks before each commit. To install pre-commit, run:

```bash
pixi run pre-commit install
```

To run the checks manually, run:

```bash
pixi run pre-commit run --all-files
```

# Getting the data

1. create a Kaggle account: https://www.kaggle.com/
2. get API keys and user name
   - Go to your account, and click on your profile in the top right
   - Then click on "Settings"
   - Scroll down to the API section and click on "Create New Token"
   - Get your username and API key from there

We have written a data loader function for you in the "nba/data_loader.py".This allows you to
download the data with by running the script from the terminal. Run the following command in the
terminal being at the root of the repository.

```bash
pixi run python nba/data_loader.py -u "your_user_name" -k "your_api_key" -d "wyattowalsh/basketball"
```

Replace "your_user_name" and "your_api_key" with your username and API key. This creates a json
file at "~/.kaggle/kaggle.json" with your username and API key, which is used to authenticate your
account and download the data.

## Explanations

### `if __name__ == "__main__":`
Every Python file has a built-in variable `__name__`. When the file is run directly (e.g. `python nba/data_loader.py`), it is set to `"__main__"`, so the block runs and calls `main()`. When the file is imported by another module, `__name__` is the module name instead, so `main()` does not run and only the functions are loaded. This lets the file work both as a script and as an importable module.

### How `click` enables the CLI
`click` turns a Python function into a command-line command using decorators. `@click.command()` marks `main()` as a command, and `@click.option()` / `@click.argument()` define the inputs that can be passed from the terminal (for example the dataset name). click parses and validates these inputs, passes them to the function as arguments, and automatically generates a `--help` page.
