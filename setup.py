#!/usr/bin/env python3
from setuptools import setup, find_packages

setup(
    name="dom_auditor",
    version="0.1.0",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "beautifulsoup4>=4.9.0",
        "requests>=2.25.0",
        "flask>=2.0.0",
        "esprima>=4.0.0",
        "jinja2>=3.0.0",
        "colorama>=0.4.4",
        "lxml>=4.6.0",
    ],
    entry_points={
        "console_scripts": [
            "dom-auditor=dom_auditor.main:main",
            "dom-auditor-gui=dom_auditor.gui.server:start_gui_server",
        ],
    },
    author="Your Name",
    author_email="your.email@example.com",
    description="DOM Auditor is a tool for scanning and analyzing HTML and JavaScript files for DOM vulnerabilities.",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/b0llull0s/DOM-Auditor",
    keywords="security, dom, web-security, vulnerability-scanner, javascript-security",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Intended Audience :: Information Technology",
        "Topic :: Security",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.7",
)