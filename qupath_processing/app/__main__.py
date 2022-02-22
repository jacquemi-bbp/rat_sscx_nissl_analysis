"""
Processing for rat somatosensory cortex QuPath Nissl data
"""

import click

from qupath_processing.app.convert.single import cmd as convert_cmd
from qupath_processing.app.convert.batch import cmd as batch_convert
from qupath_processing.app.density.single import density
from qupath_processing.app.density.batch import batch_density
from qupath_processing.app.boundary.single import cmd
from qupath_processing.version import VERSION


@click.group('pyqupath_processing', help=__doc__.format(esc='\b'))
@click.option("-v", "--verbose", count=True, help="-v for INFO, -vv for DEBUG")
@click.version_option(VERSION)
def app(verbose=0):
    # pylint: disable=missing-docstring
    pass


app.add_command(name='convert', cmd=convert_cmd)
app.add_command(name='batch_convert', cmd=batch_convert)
app.add_command(name='density', cmd=density)
app.add_command(name='batch_density', cmd=batch_density)
app.add_command(name='boundary', cmd=cmd)
if __name__ == '__main__':
    app()
