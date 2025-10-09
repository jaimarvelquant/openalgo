#!/usr/bin/env python3
"""
Setup script for Playwright MCP Server
"""

from setuptools import setup, find_packages

setup(
    name="playwright-mcp-server",
    version="1.0.0",
    description="Playwright MCP Server for browser automation",
    author="OpenAlgo",
    author_email="support@openalgo.in",
    packages=find_packages(),
    install_requires=[
        "playwright>=1.55.0",
        "mcp>=1.11.0",
    ],
    entry_points={
        "console_scripts": [
            "playwright-mcp-server=mcp.playwright_mcp_global:main",
        ],
    },
    python_requires=">=3.8",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)
