from setuptools import setup, find_packages

setup(
    name="github-activity",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "fire>=0.5.0",
        "rich>=10.0.0",
    ],
    entry_points={
        'console_scripts': [
            'github-activity=github_activity.github_activity:main',
        ],
    },
) 