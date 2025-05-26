#!/usr/bin/env python3
"""
Setup script para o Enrollment API
"""

from setuptools import setup, find_packages

# Ler requirements.txt
with open("requirements.txt", "r", encoding="utf-8") as f:
    requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Ler requirements-dev.txt
with open("requirements-dev.txt", "r", encoding="utf-8") as f:
    dev_requirements = [line.strip() for line in f if line.strip() and not line.startswith("#")]

# Ler README
with open("README.md", "r", encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="enrollment-api",
    version="1.0.0",
    description="Sistema completo de gerenciamento de inscrições com processamento assíncrono",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="Lucas Maximino Torres",
    author_email="lucasmaximinotorres@gmail.com",
    url="https://github.com/lksmaxx/enroll_api",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.12",
    install_requires=requirements,
    extras_require={
        "dev": dev_requirements,
        "test": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "coverage>=7.3.0",
            "requests>=2.31.0",
        ],
    },
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Framework :: FastAPI",
        "Topic :: Internet :: WWW/HTTP :: HTTP Servers",
        "Topic :: Software Development :: Libraries :: Application Frameworks",
    ],
    keywords="fastapi enrollment api mongodb rabbitmq async",
    project_urls={
        "Bug Reports": "https://github.com/lksmaxx/enroll_api/issues",
        "Source": "https://github.com/lksmaxx/enroll_api",
        "Documentation": "https://github.com/lksmaxx/enroll_api/blob/main/README.md",
    },
) 