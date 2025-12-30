import subprocess
from pathlib import Path

from avro_cli.config import Config


def avdl_converter(config: Config, input_file: Path, output_dir: Path):
    extract_avpr(config, input_file, output_dir)
    extract_avsc(config, input_file, output_dir)


def extract_avpr(config: Config, input_file: Path, output_dir: Path):
    tools_jar = config.avro.tools_jar
    file_name = input_file.stem.capitalize()

    output_avpr_dir = output_dir / "avpr"
    output_file = output_avpr_dir / f"{file_name}.avpr"
    ensure_dir(output_avpr_dir)

    # avpr generation
    command = ["java", "-jar", tools_jar, "idl", input_file, output_file]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.stderr:
        raise Exception(result.stderr)


def extract_avsc(config: Config, input_file: Path, output_dir: Path):
    tools_jar = config.avro.tools_jar

    output_avsc_dir = output_dir / "avsc"
    ensure_dir(output_avsc_dir)

    # avsc generation
    command = ["java", "-jar", tools_jar, "idl2schemata", input_file, output_avsc_dir]
    result = subprocess.run(command, capture_output=True, text=True)
    if result.stderr:
        raise Exception(result.stderr)


def ensure_dir(location: Path):
    if not location.exists():
        location.mkdir(parents=True)
