import click
from qupath_processing.convert import single_image_conversion


@click.command()
@click.option(
    "--cells-detection-path",
    required=True,
    help="The directory path that contains cells feature files",
)
@click.option(
    "--annotations-path",
    required=False,
    help="The directory path that contains annotations files(S1HL, top_left, ...",
)
@click.option(
    "--output-path",
    required=True,
    help="Path that will contain the converted data into two Dataframes",
)
@click.option(
    "--qupath-project-path",
    required=False,
    help="qupath project path that contains images metadata",
)
@click.option(
    "--image-name", required=True, help="iamge name inside the qupath project"
)
@click.option(
    "--pixel-size", required=True, type=float, help="The pixel size in the QuPath project"
)
@click.option("--exclude",  help="Randomly exclude cells on z axis boundaries.", is_flag=True)

def cmd(
    cells_detection_path,
    annotations_path,
    output_path,
    qupath_project_path,
    image_name,
    pixel_size,
    exclude
):
    single_image_conversion(output_path, qupath_project_path, image_name,
                            cells_detection_path, annotations_path,
                            pixel_size, exclude)