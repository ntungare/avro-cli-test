import shutil
from pathlib import Path
from typing import Annotated

from rich.console import Console
from typer import Argument, Context, Option, Typer

from avro_cli.config import Config
from avro_cli.parser.avdl_reader import avdl_converter

app = Typer(help="Commands for IDL files")
console = Console()


@app.command()
def parse(
    ctx: Context,
    avdls: Annotated[str, Argument(help="Glob location of avdl files")] = "**/*.avdl",
    output: Annotated[
        str, Argument(help="Location to output avpr and avsc files")
    ] = "./generated",
    clear_output_dir: Annotated[
        bool, Option(help="Clear output location before emitting files?")
    ] = True,
) -> None:
    config: Config = ctx.obj["config"]
    current_location = Path("./")
    output_location = Path(output)

    if output_location.exists() and clear_output_dir:
        shutil.rmtree(output_location)

    if not avdls.endswith(".avdl"):
        raise Exception(f"Can only process glob for avdl files, received: {avdls}")

    for file_location in current_location.glob(avdls):
        avdl_converter(config, file_location, output_location)

    console.log("[bold]Generated the following files:[/bold]")
    for file_location in output_location.glob("**/*.avpr"):
        console.log(str(file_location).replace("/avpr/", "/[bold][cyan]avpr[/bold]/"))

    for file_location in output_location.glob("**/*.avsc"):
        console.log(str(file_location).replace("/avsc/", "/[bold][green]avsc[/bold]/"))
