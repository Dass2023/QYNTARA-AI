"""
Qyntara AI - Setup Script
=========================

Build and installation configuration.

Usage:
    pip install -e .              # Development install
    pip install -e ".[usd]"       # With USD support
    pip install -e ".[all]"       # All optional features
    python -m build               # Build distribution
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_file = Path(__file__).parent / "README.md"
long_description = readme_file.read_text(encoding='utf-8') if readme_file.exists() else ""

setup(
    name="qyntara-core",
    version="5.0.0",
    author="Dass2023",
    author_email="dass2023@qyntara.ai",
    description="Spatial Intelligence Operating System - Universal 3D pipeline with AI-powered optimization",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Dass2023/Qyntara-AI",
    project_urls={
        "Documentation": "https://qyntara.ai/docs",
        "Source": "https://github.com/Dass2023/Qyntara-AI",
        "Tracker": "https://github.com/Dass2023/Qyntara-AI/issues",
    },
    packages=find_packages(include=['qyntara_core*', 'qyntara_dcc*', 'qyntara_ai*']),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Multimedia :: Graphics :: 3D Modeling",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=[
        "numpy>=1.19.0",
        "packaging>=20.0",
    ],
    extras_require={
        "usd": ["usd-core>=22.11"],
        "scipy": ["scipy>=1.7.0"],
        "ai": [
            "torch>=2.0.0",
            "diffusers>=0.20.0",
            "transformers>=4.30.0",
            "accelerate>=0.20.0",
            "safetensors>=0.3.0",
            "torch-geometric>=2.3.0",
        ],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=3.0.0",
            "black>=22.0.0",
            "flake8>=4.0.0",
            "mypy>=0.950",
            "build>=0.8.0",
            "twine>=4.0.0",
        ],
        "all": [
            "usd-core>=22.11",
            "scipy>=1.7.0",
            "torch>=2.0.0",
            "diffusers>=0.20.0",
            "transformers>=4.30.0",
            "accelerate>=0.20.0",
            "safetensors>=0.3.0",
            "torch-geometric>=2.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "qyntara-convert=qyntara_core.cli:convert_main",
            "qyntara-validate=qyntara_core.cli:validate_main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
