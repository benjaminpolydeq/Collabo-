"""
Setup configuration for Collabo application
"""

from setuptools import setup, find_packages
from pathlib import Path

# Lire le README pour la description longue
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

# Lire les requirements
requirements = (this_directory / "requirements.txt").read_text().splitlines()
requirements = [req.strip() for req in requirements if req.strip() and not req.startswith('#')]

setup(
    name="collabo-app",
    version="1.0.0",
    author="Collabo Team",
    author_email="contact@collabo-app.com",
    description="Application de networking intelligent et sécurisée",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/votre-username/collabo",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Communications :: Chat",
        "Topic :: Office/Business",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Framework :: Streamlit",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-cov>=4.1.0",
            "black>=23.12.1",
            "flake8>=6.1.0",
            "mypy>=1.7.1",
        ],
        "docs": [
            "mkdocs>=1.5.3",
            "mkdocs-material>=9.5.2",
        ],
        "audio": [
            "streamlit-webrtc>=0.47.1",
            "pydub>=0.25.1",
            "SpeechRecognition>=3.10.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "collabo=app.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "app": [
            "assets/css/*.css",
            "assets/images/*.png",
            "*.yaml",
        ],
    },
    zip_safe=False,
    keywords=[
        "networking",
        "contacts",
        "crm",
        "ai",
        "secure",
        "encryption",
        "professional",
        "chat",
        "messaging",
    ],
    project_urls={
        "Bug Reports": "https://github.com/votre-username/collabo/issues",
        "Source": "https://github.com/votre-username/collabo",
        "Documentation": "https://github.com/votre-username/collabo/wiki",
    },
)