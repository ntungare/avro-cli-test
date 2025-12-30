from typing import Annotated

from typer import Context, Option, Typer

from avro_cli import idl_commands, trial
from avro_cli.avro_tools import check_version_and_download_jar
from avro_cli.config import Config, load_config
from avro_cli.state import state

app = Typer(
    help="""
Avro CLI: Codegen tool for all (most) language

(Let me know if there is a language that you would like that is missing,
all codegen happens v)
"""
)


@app.callback()
def cli_callback(
    ctx: Context,
    config_file: Annotated[
        str, Option(help="Name and location of the config file")
    ] = "config.yaml",
    verbose: Annotated[bool, Option(help="Enable verbose logging")] = True,
):
    config = load_config(config_file)
    if ctx.obj is None:
        ctx.obj = dict()

    ctx.obj["config"] = config

    if verbose != state.verbose:
        state.verbose = verbose


@app.command(help="Command to download Avro Tools JAR file")
def download_avro_jar(
    ctx: Context,
    force_download: Annotated[
        bool,
        Option(help="By default, if the jar is present download is not attempted"),
    ] = False,
):
    config: Config = ctx.obj["config"]
    check_version_and_download_jar(config, force_download)


app.add_typer(idl_commands.app, name="idl")

app.add_typer(trial.app, name="trial")
