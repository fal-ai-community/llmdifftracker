from setuptools import setup, find_packages

setup(
    name="llmdifftracker",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "openai>=1.0.0",
    ],
    extras_require={
        "wandb": ["wandb>=0.15.0"],
    },
    author="Simo Ryu",
    author_email="cloneofsimo@gmail.com",
    description="A package that tracks and summarizes code changes using LLMs",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/cloneofsimo/llmdifftracker",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
)
