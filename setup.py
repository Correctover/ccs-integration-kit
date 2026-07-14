from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="ccs-integration-kit",
    version="1.0.0",
    author="Correctover Research Group",
    author_email="wangguigui@correctover.com",
    description="4-line runtime conformance verification for LLM agents",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Correctover/ccs-integration-kit",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[],
    extras_require={
        "crewai": ["crewai>=0.28.0"],
        "langchain": ["langchain>=0.1.0", "langchain-openai>=0.1.0"],
        "autogen": ["pyautogen>=0.2.0"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "isort>=5.12.0",
            "mypy>=1.0.0",
        ],
    },
)
