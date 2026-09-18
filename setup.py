"""
Setup configuration for AI Test Generator
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

# Read requirements
requirements = []
with open('requirements.txt') as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="ai-test-generator",
    version="0.1.0",
    author="Naysrania18",
    author_email="sandeepnaysrania@gmail.com",
    description="AI-powered test case generation tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/ai-test-generator",
    project_urls={
        "Bug Tracker": "https://github.com/Naysrania18/ai-test-generator/issues",
        "Documentation": "https://github.com/Naysrania18/ai-test-generator/wiki",
        "Source Code": "https://github.com/Naysrania18/ai-test-generator",
    },
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Testing",
        "Topic :: Software Development :: Quality Assurance",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.990",
        ],
    },
    entry_points={
        "console_scripts": [
            "ai-test-gen=ai_test_generator.cli:main",
        ],
    },
    include_package_data=True,
    keywords="testing test-automation ai machine-learning test-generation pytest",
)
