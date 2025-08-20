from setuptools import setup, find_packages

setup(
    name="ragtutor",
    version="1.0.0",
    description="AI-powered document Q&A system with full observability",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.0",
        "uvicorn[standard]>=0.24.0",
        "gradio>=4.7.0",
        "pydantic>=2.5.0",
        "pydantic-settings>=2.1.0",
        "prometheus-fastapi-instrumentator>=6.1.0",
        "tenacity>=8.2.0",
        "pypdf>=3.17.0",
        "chromadb>=0.4.18",
        "sentence-transformers>=2.2.0",
        "ollama>=0.1.7",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.0",
            "pytest-asyncio>=0.21.0",
            "pytest-cov>=4.1.0",
            "httpx>=0.25.0",
        ]
    },
    python_requires=">=3.11",
    entry_points={
        "console_scripts": [
            "ragtutor-api=ragtutor.api.main:main",
            "ragtutor-ui=ragtutor.ui.gradio_app:main",
        ],
    },
)

