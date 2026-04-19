"""Generate embeddings for all entities and compute semantic neighbors."""
import json
import os
import numpy as np
from openai import OpenAI

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH = os.path.join(ROOT, "graph")
DOCS = os.path.join(ROOT, "docs")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# Load entities
entities = []
with open(os.path.join(GRAPH, "entities.jsonl")) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        entities.append(json.loads(line))

print(f"Embedding {len(entities)} entities with text-embedding-3-large...")

# Prepare texts for embedding (name + summary for richer semantics)
texts = [f"{e['name']}: {e['summary']}" for e in entities]

# Batch embed (API supports up to 2048 inputs)
response = client.embeddings.create(
    model="text-embedding-3-large",
    input=texts
)

embeddings = [item.embedding for item in response.data]
print(f"Got {len(embeddings)} embeddings, dimension {len(embeddings[0])}")

# Compute cosine similarities
def cosine_sim(a, b):
    a = np.array(a)
    b = np.array(b)
    return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))

# For each entity, find top-10 nearest neighbors
print("Computing pairwise similarities...")
neighbors = {}
for i, entity in enumerate(entities):
    sims = []
    for j, other in enumerate(entities):
        if i == j:
            continue
        sim = cosine_sim(embeddings[i], embeddings[j])
        sims.append((other["name"], sim))
    sims.sort(key=lambda x: x[1], reverse=True)
    neighbors[entity["name"]] = [
        {"id": name, "score": round(score, 3)}
        for name, score in sims[:10]
    ]

# Save embeddings (for future use / re-embedding queries)
embeddings_data = {
    entities[i]["name"]: embeddings[i]
    for i in range(len(entities))
}
with open(os.path.join(GRAPH, "embeddings.json"), "w") as f:
    json.dump(embeddings_data, f)
print(f"Saved raw embeddings to graph/embeddings.json")

# Save neighbors into the data.json for the UI
data_path = os.path.join(DOCS, "data.json")
with open(data_path) as f:
    data = json.load(f)

# Add neighbors to each node
for node in data["nodes"]:
    node["neighbors"] = neighbors.get(node["id"], [])

with open(data_path, "w") as f:
    json.dump(data, f, indent=2)

print(f"Updated data.json with semantic neighbors for {len(neighbors)} entities")
print("Done!")
