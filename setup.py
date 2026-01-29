#!/usr/bin/env python
from setuptools import setup, find_packages
from pathlib import Path

# Read the long description from README.md
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='spriteforge',
    version="1.0.0",
    description='Forge your sprites with precision - A modern tool for extracting sprites from images.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author="merhovon",
    author_email='merhovon@users.noreply.github.com',
    packages=find_packages(),
    include_package_data=True,
    python_requires='>=3.10',
    install_requires=[
        'numpy>=1.21.0',
        'PyQt6>=6.6.0',
        'pillow>=10.0.0',
        'loguru>=0.7.0'
    ],
    entry_points={
        'console_scripts': ['spriteforge = spriteforge.app:main'],
        'gui_scripts': ['spriteforge-gui = spriteforge.app:main']
    },
    license='GPL-3.0-or-later',
    url='https://github.com/merhovon/SpriteForge',
    zip_safe=False,
    keywords=['spriteforge', 'sprite', 'forge', 'extractor', 'unique color', 'ai', 'ml', 'image processing', 'game-dev'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Topic :: Multimedia :: Graphics :: Editors :: Raster-Based',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12'
    ]
)
