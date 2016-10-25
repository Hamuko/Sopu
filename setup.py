from setuptools import find_packages, setup


setup(
    name='Sopu',
    version=0.0,
    description='Unofficial Syncplay client',
    url='https://github.com/Hamuko/Sopu',
    author='Hamuko',
    author_email='hamuko@burakku.com',
    license='Apache2',
    classifiers=[
        'Environment :: Console',
        'Intended Audience :: End Users/Desktop',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
    ],
    packages=find_packages(),
    install_requires=[
        'click',
        'Twisted'
    ],
    entry_points={
        'console_scripts': ['sopu=sopu.cli:main'],
    }
)
