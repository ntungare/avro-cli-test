import os
from pathlib import Path

from pydantic import BaseModel
from rich.console import Console
from strictyaml import YAML, load

console = Console()


class AvroConfig(BaseModel):
    """App config class."""

    tools_jar: Path = Path(os.path.expanduser("~/.avro-cli/avro-tools.jar"))


class Config(BaseModel):
    """CLI config class."""

    avro: AvroConfig = AvroConfig()

    @staticmethod
    def default_config() -> Config:
        return Config()

    @staticmethod
    def read_yml_config(path: Path) -> YAML | None:
        """Classmethod returns YAML config"""

        try:
            with path.open("r") as file:
                file_content = file.read()
                return load(yaml_string=file_content)

        except FileNotFoundError:
            console.print_exception()

    @staticmethod
    def load_yml_config(path: Path) -> Config:
        yaml = Config.read_yml_config(path)
        if yaml is None:
            return Config.default_config()

        return Config(**yaml.data)


def load_config(path: str) -> Config:
    config_file_path = Path(os.path.realpath(os.path.expanduser(path)))
    return Config.load_yml_config(config_file_path)
