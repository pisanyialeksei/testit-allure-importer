from setuptools import setup

setup(
    name='testit-importer-allure',
    version='1.0.0',
    description='Allure report importer for Test IT',
    long_description=open('README.md', "r").read(),
    long_description_content_type="text/markdown",
    url='https://pypi.org/project/testit-importer-allure/',
    author='Pavel Butuzov',
    author_email='pavel.butuzov@testit.software',
    license='Apache-2.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
    ],
    packages=['testit_importer_allure'],
    package_data={'testit_importer_allure': ['../connection_config.ini']},
    package_dir={'testit_importer_allure': 'src'},
    install_requires=['testit-api-client'],
    entry_points={'console_scripts': ['testit = testit_importer_allure.__main__:console_main']}
)
