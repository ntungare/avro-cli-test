from pathlib import Path

from avro import schema
from avro.datafile import DataFileReader, DataFileWriter
from avro.io import DatumReader, DatumWriter
from rich.console import Console
from typer import Typer

app = Typer(help="Commands for IDL files")
console = Console()


@app.command()
def trial() -> None:
    avsc_location = Path("./") / "resource" / "avsc" / "example.avsc"

    schema_json = avsc_location.open("r").read()

    parsed_schema = schema.parse(schema_json)

    output_dir = Path("./") / "resource" / "output"
    output_dir.mkdir(parents=True, exist_ok=True)
    output_location = output_dir / "output.avro"

    with DataFileWriter(
        output_location.open("wb"), DatumWriter(), parsed_schema, codec="deflate"
    ) as writer:
        writer.append({"name": "Alyssa", "favorite_number": 256})
        writer.append({"name": "Ben", "favorite_number": 7, "favorite_color": "red"})

    with DataFileReader(output_location.open("rb"), DatumReader()) as reader:
        print(reader.schema)
        for user in reader:
            print(user)
