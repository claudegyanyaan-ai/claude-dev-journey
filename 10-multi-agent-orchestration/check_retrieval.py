from src.rag_core import retrieve

checks = [
    ("What is noise figure in an EDFA?", "data/index/dwdm_osnr"),
    ("What is the maximum cable length for 1000BASE-T?", "data/index/ethernet"),
    ("What does a router do?", "data/index/ip"),
]

for query, index_dir in checks:
    print(f"=== {index_dir} : {query!r} ===")
    for r in retrieve(query, index_dir):
        preview = r["text"][:150].replace("\n", " ")
        print(f"[{r['score']:.3f}] pages {r['pages']}: {preview!r}")
    print()

print("=== full ranking for the router query ===")
all_results = retrieve("What does a router do?", "data/index/ip", k=16)
for i, r in enumerate(all_results, 1):
    marker = " <-- REAL ANSWER CHUNK" if "facilitate communication" in r["text"] else ""
    print(f"{i}. [{r['score']:.3f}] pages {r['pages']}{marker}")