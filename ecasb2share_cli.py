import click
from ecasb2share.ecasb2shareclient import EcasShare

@click.group()
def main():
    """
    Simple CLI for ecasb2share
    """
    pass

@main.command()
def cli():
    click.echo('Hello world!')

@main.command()
@click.argument('metadata_json_file')
def load_metadata(metadata_json_file):
    """This loads and returns metadata from json file"""

    client = EcasShare()
    click.echo(client.load_metadata_from_json(metadata_json_file))


