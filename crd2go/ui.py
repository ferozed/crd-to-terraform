import click
from .gen import process
#import gen

@click.command()
@click.argument("crd_path")
@click.argument("output_path")
def run(crd_path:str, output_path:str):
    # msg
    process(crd_path, output_path)
