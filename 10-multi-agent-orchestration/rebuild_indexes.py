"""Rebuild all three RAG indexes from their source PDFs."""
from src.rag_core import build_index

build_index("docs/dwdm_osnr/dwdm_osnr.pdf", "data/index/dwdm_osnr")
build_index("docs/ethernet/ethernet.pdf", "data/index/ethernet")
build_index("docs/ip/IP.pdf", "data/index/ip")