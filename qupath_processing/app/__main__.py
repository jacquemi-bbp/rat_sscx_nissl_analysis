"""
Processing for rat somatosensory cortex QuPath Nissl data
"""

import click

from qupath_processing.app.density.single import density
from qupath_processing.app.density.batch import batch_density
from qupath_processing.version import VERSION

@click.group('pyqupath_processing', help=__doc__.format(esc='\b'))
@click.option("-v", "--verbose", count=True, help="-v for INFO, -vv for DEBUG")
@click.version_option(VERSION)
def app(verbose=0):
    # pylint: disable=missing-docstring
    pass


app.add_command(name='density', cmd=density)
app.add_command(name='batch_density', cmd=batch_density)

if __name__ == '__main__':
    app()