# backend/utils/config_loader.py

import os
import yaml


def load_config(config_path="config/config.yaml"):
    """
    Load configuration from a YAML file.
    """
    with open(config_path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def get_groq_model():
    """
    Get model name from config or fallback to default.
    """
    config = load_config()
    return config.get("groq", {}).get("model", "llama3-70b-8192")


def get_vectorstore_path():
    """
    Get vectorstore path from config.
    """
    config = load_config()
    return config.get("vectorstore_path", "data/vectorstore/ipc_vectorstore.faiss")