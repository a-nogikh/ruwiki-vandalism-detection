import os
import re
import click
import importlib

@click.group()
def main():
    pass

# import all cli_tools
for file in os.listdir("./cli_utils"):
    match = re.match(r"([A-z0-9_]+)\.py$", file, re.M)
    if match is None:
        continue

    res = importlib.import_module("cli_utils." + match.group(1))
    if not hasattr(res, 'get_command'):
        continue
    
    main.add_command(res.get_command())

if __name__ == "__main__":
    main()
