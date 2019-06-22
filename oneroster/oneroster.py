

from oneroster.classlink import ClasslinkConnector
from oneroster.clever import CleverConnector


def get_connector(options):
    platform = options['platform']
    if platform == 'classlink':
        return ClasslinkConnector(options)
    elif platform == 'clever':
        return CleverConnector(options)

    raise NotImplementedError("No module for " + platform +
                              " was found. Supported are: [classlink, clever]")

