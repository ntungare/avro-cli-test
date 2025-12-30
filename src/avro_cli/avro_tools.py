import requests
from avro import __version__ as python_package_version
from requests import Response
from rich.console import Console
from rich.progress import (
    DownloadColumn,
    Progress,
    TimeRemainingColumn,
    TransferSpeedColumn,
)

from avro_cli.config import Config
from avro_cli.state import state

console = Console()


def does_jar_exists(config: Config) -> bool:
    return config.avro.tools_jar.exists()


def does_latest_match_python_package_version() -> tuple[bool, str]:
    search_url = "https://search.maven.org/solrsearch/select"
    query = "g:org.apache.avro AND a:avro-tools"

    if state.verbose:
        console.log("Checking latest version")

    response: Response = requests.get(
        search_url, params={"q": query, "rows": 100, "wt": "json"}
    )

    try:
        response.raise_for_status()
        data = response.json()
        docs = data.get("response", {}).get("docs", [])
        if not docs:
            raise Exception(f"Package matching query not found: '{query}'")

        doc = docs[0]
        latest_version = doc["latestVersion"]

        matches_latest = latest_version == python_package_version

        if state.verbose and not matches_latest:
            console.log(
                f"Latest version: {latest_version} and Python version: {python_package_version}"
            )
            console.log(f"Using latest version of the jar file: {latest_version}")

        return matches_latest, latest_version
    except Exception:
        console.print_exception()

    if state.verbose:
        console.log(
            f"Artifact version not found, using python package version: {python_package_version}"
        )

    return False, python_package_version


def check_version_and_download_jar(config: Config, force_download: bool) -> None:
    jar_exists = does_jar_exists(config)

    if jar_exists and not force_download:
        if state.verbose:
            console.log("[bold]JAR File exists, skipping download[/bold]")
        return

    if jar_exists and force_download:
        if state.verbose:
            console.log("[bold]JAR File exists but forcing download[/bold]")

    group = "org.apache.avro"
    group_path = group.replace(".", "/")
    artifact_id = "avro-tools"

    matches_package, version = does_latest_match_python_package_version()

    filename = f"{artifact_id}-{version}.jar"
    url = f"https://repo1.maven.org/maven2/{group_path}/{artifact_id}/{version}/{filename}"

    if state.verbose:
        console.log(f"Downloading jar from: {url}")

    ensure_path(config)
    tools_jar_location = config.avro.tools_jar

    if state.verbose:
        console.log(f"Saving jar to: {tools_jar_location}")

    with Progress(
        *Progress.get_default_columns(),
        DownloadColumn(),
        TransferSpeedColumn(),
        TimeRemainingColumn(),
    ) as progress:
        response: Response = requests.get(url, stream=True)
        total_size = int(response.headers.get("Content-Length", 0))
        try:
            response.raise_for_status()
        except Exception:
            console.print_exception()
            return

        task = progress.add_task("[cyan]Downloading...", total=total_size)

        block_size = 1024

        with tools_jar_location.open("wb") as file:
            for data in response.iter_content(block_size):
                progress.update(task, advance=len(data))
                file.write(data)


def ensure_path(config: Config):
    path = config.avro.tools_jar.parent
    path.mkdir(parents=True, exist_ok=True)
