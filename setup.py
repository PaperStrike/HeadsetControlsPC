"""
Usage instructions:
- If you are installing: `pip install . [--user]`
"""
import setuptools

with open('./README.md', 'r', encoding='utf-8') as readme:
    long_description = readme.read()

setuptools.setup(
    name='headset',
    version='0.0.1a1',
    author='PaperStrike',
    author_email='1395348685z@gmail.com',
    description='为 PC 提供 3.5mm 耳机线控支持',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/PaperStrike/HeadsetControlsPC',
    packages=setuptools.find_packages(),
    install_requires=[
        'keyboard',
        'numpy',
        'sounddevice'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: Microsoft :: Windows',
        'Operating System :: POSIX :: Linux',
    ],
    python_requires='>=3.6',
)
