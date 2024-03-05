from setuptools import setup, find_namespace_packages

setup(
    name='gsystemctl',
    version='0.3.0',
    description='Control the systemd service manager',
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
        'gsystemctl.ui.icons.160x160': ['*.png'],
    },
    entry_points={
        'gui_scripts': [
            'gsystemctl=gsystemctl.ui.application:run',
        ],
    },
    install_requires=['PyGObject>=3.40'],
    include_package_data=True,
    python_requires='>=3.10'
)
