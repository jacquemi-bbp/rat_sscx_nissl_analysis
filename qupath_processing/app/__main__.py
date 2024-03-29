"""
Processing for rat somatosensory cortex QuPath Nissl data
"""

import click

from qupath_processing.app.convert.single import cmd as convert_cmd
from qupath_processing.app.convert.batch import cmd as batch_convert
from qupath_processing.app.convert.project import cmd as qpproj_convert
from qupath_processing.app.density.single import density
from qupath_processing.app.density.batch import batch_density
from qupath_processing.app.exclude.single import cmd as exclude

from qupath_processing.version import VERSION


@click.group("pyqupath_processing", help=__doc__.format(esc="\b"))
@click.option("-v", "--verbose", count=True, help="-v for INFO, -vv for DEBUG")
@click.version_option(VERSION)
def app(verbose=0):
    # pylint: disable=missing-docstring
    pass


app.add_command(name="convert", cmd=convert_cmd)
app.add_command(name="batch-convert", cmd=batch_convert)
app.add_command(name="qpproj-convert", cmd=qpproj_convert)
app.add_command(name="density", cmd=density)
app.add_command(name="batch-density", cmd=batch_density)
app.add_command(name="exclude-cells", cmd=exclude)
if __name__ == "__main__":
    app()
