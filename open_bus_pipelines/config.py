import os


STRIDE_VENV = os.environ.get('STRIDE_VENV')
if not STRIDE_VENV:
    STRIDE_VENV = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'venv', 'stride')

OPEN_BUS_PIPELINES_ROOTDIR = os.environ.get('OPEN_BUS_PIPELINES_ROOTDIR')
if not OPEN_BUS_PIPELINES_ROOTDIR:
    OPEN_BUS_PIPELINES_ROOTDIR = os.path.join(os.path.dirname(os.path.dirname(__file__)))

OPEN_BUS_PIPELINES_DOWNLOAD_SIRI_SNAPSHOTS = os.environ.get('OPEN_BUS_PIPELINES_DOWNLOAD_SIRI_SNAPSHOTS') == 'yes'
OPEN_BUS_PIPELINES_PIP_INSTALL_DEPS = os.environ.get('OPEN_BUS_PIPELINES_PIP_INSTALL_DEPS') == 'yes'
