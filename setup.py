import glob
import os
from setuptools import setup, find_namespace_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

_data_files = [('share/applications',
                ['src/gsystemctl/share/applications/gsystemctl.desktop'])]
_exclude_package_data = {'gsystemctl.share.applications': ['*']}
for icon_path in glob.glob('src/gsystemctl/share/icons/hicolor/*x*'):
    size = os.path.basename(icon_path)
    icons = glob.glob(os.path.join(icon_path, 'apps', 'gsystemctl.png'))
    _data_files.append((f'share/icons/hicolor/{size}/apps', icons))

setup(
    name='gsystemctl',
    version='0.5.0',
    description='Control the systemd service manager with Gtk GUI, instead of console',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='GPLv3',
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications :: GTK',
        'Topic :: System :: Monitoring',
        'Topic :: System :: Systems Administration',
        'Natural Language :: English',
    ],
    url='https://github.com/ferkretz/gsystemctl',
    author='Ferenc Kretz',
    author_email='ferkretz@gmail.com',
    package_dir={'': 'src'},
    packages=find_namespace_packages(
        where='src',
        exclude=[],
    ),
    package_data={
        'gsystemctl': ['*.ini'],
        'gsystemctl.ui.images': ['*.png'],
    },
    data_files=_data_files,
    entry_points={
        'gui_scripts': [
            'gsystemctl=gsystemctl.ui.application:run',
        ],
    },
    install_requires=['PyGObject>=3.40'],
    python_requires='>=3.10'
)
