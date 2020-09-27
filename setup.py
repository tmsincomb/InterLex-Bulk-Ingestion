from setuptools import setup, find_packages

setup(
    name='interlex_bulk_ingestion',
    version='0.1.2',
    description='InterLex bulk ingestion via CSV and Google Sheets',
    long_description='',
    url='https://github.com/tmsincomb/InterLex-Bulk-Ingestion',
    author='Troy Sincomb',
    author_email='troysincomb@gmail.com',
    license='MIT',
    keywords='interlex bulk ingestion',
    packages=find_packages('interlex_bulk_ingestion'),
    python_requires='>=3.7',
    classifiers=[
        'Development Status :: 1 - BETA',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    install_requires=[
        'docopt',
        'ontquery',
        'pandas',
    ],
    entry_points={
        'console_scripts': [
            'interlex-bulk-ingestion=interlex_bulk_ingestion.interlex_bulk_ingestion:main',
        ],
    },
)