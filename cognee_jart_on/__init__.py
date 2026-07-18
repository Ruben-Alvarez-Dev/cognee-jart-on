"""
COGNEE-jart-on — Cognee jarta on

P2P integration for Cognee with LiteLLM proxy and local Ollama embeddings.
Designed for multi-device LAN setups with shared knowledge base.
"""

__version__ = "0.2.0"
__author__ = "Ruben Alvarez Dianez"

from .bootstrap import setup_cognee, CogneeConfig

__all__ = ["setup_cognee", "CogneeConfig"]
