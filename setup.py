from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="seeker-o1-ai",
    version="0.1.0",
    author="Ibrahim Rayamah",
    author_email="ibz04.dev@gmail.com",
    description="An upgrade of seeker, with a python implementation and multi-agent support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iBz-0/seeker-o1",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.11",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "seeker-o1=seeker_o1.main:main",
        ],
    },
)
