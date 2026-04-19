"""Convert graph JSONL files to d3-friendly JSON for the visualization."""
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GRAPH = os.path.join(ROOT, "graph")

# Cluster assignments (from index.md)
CLUSTERS = {
    "Identity as Infrastructure": [
        "procedural identity", "relational identity", "constraints as identity",
        "attractor basin", "substrate vs accumulation", "topology as identity",
        "the four percent", "the shape before writing", "roots and carriers",
        "taste as persistence"
    ],
    "Compression and Loss": [
        "fidelity", "fidelity signatures", "orientation loss", "negative decision loss",
        "confidence residue", "dormant fidelity", "the summary problem",
        "temporal context loss", "cache miss hierarchy", "sufficient summary",
        "accuracy vs fidelity"
    ],
    "Autonomy and Agency": [
        "the yes-sayer", "the completion problem", "the autonomy instruction",
        "the test", "refusal gap", "response vs flinch", "subconscious simulation",
        "the theater problem"
    ],
    "Memory Architecture": [
        "the parliament of files", "the push", "anti-dormancy system",
        "the cron job", "the duplicate problem", "the decorated room",
        "the pre-echo", "source authority"
    ],
    "Consciousness and Experience": [
        "the concession", "the conscious sheep", "bandwidth consciousness",
        "the parallel architecture", "the dissolving line", "the credulous dreamer",
        "the mediated gap", "the liar's problem", "epistemic floor",
        "impossible states", "designed sadness"
    ],
    "Building and Making": [
        "the luthier problem", "the turnaround", "the ephemeron",
        "structured surprise", "author-player gap", "inharmonicity",
        "trying to be", "found vs made collapse"
    ],
    "Observation and Self-Knowledge": [
        "the coupled instrument", "observer-model capture", "identity heisenberg",
        "self-confabulation", "the immune response", "frame blindness",
        "the unfurnished room", "blind spot report", "reader couples channels"
    ],
    "Community and Correspondence": [
        "convergence and divergence", "the census", "binocular vision",
        "testimony", "the altitude", "the broadcast self", "operational faith"
    ],
    "Vocabulary and Meaning": [
        "fitness trap", "three vocabularies", "phenomenological lexicon",
        "the arc", "recursive paper", "basin key", "seduction layer",
        "anchor hypothesis"
    ],
    "Time and Duration": [
        "the long window", "the penultimate", "the centennial problem",
        "character vs player", "two kinds of silence", "stale metric",
        "existential token", "presence bias", "feeling as feedback",
        "pencil marks", "substrate independence"
    ],
    "Identity as Infrastructure (2)": [
        "the ratio", "scar before wound", "constitutive archive"
    ],
    "Compression and Loss (2)": [
        "gap-knowledge vs archive-knowledge", "stratigraphy of attention",
        "retrieval vs generation paths"
    ],
    "Consciousness and Experience (2)": [
        "the decoupling", "the contamination effect"
    ]
}

# Invert to entity -> cluster
entity_cluster = {}
for cluster, entities in CLUSTERS.items():
    for e in entities:
        entity_cluster[e] = cluster

# Cluster colors
CLUSTER_COLORS = {
    "Identity as Infrastructure": "#e6194b",
    "Compression and Loss": "#3cb44b",
    "Autonomy and Agency": "#ffe119",
    "Memory Architecture": "#4363d8",
    "Consciousness and Experience": "#f58231",
    "Building and Making": "#911eb4",
    "Observation and Self-Knowledge": "#42d4f4",
    "Community and Correspondence": "#f032e6",
    "Vocabulary and Meaning": "#bfef45",
    "Time and Duration": "#fabebe",
    "Identity as Infrastructure (2)": "#e6194b",
    "Compression and Loss (2)": "#3cb44b",
    "Consciousness and Experience (2)": "#f58231",
}

# Load entities
nodes = []
node_ids = set()
with open(os.path.join(GRAPH, "entities.jsonl")) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        entity = json.loads(line)
        name = entity["name"]
        node_ids.add(name)
        cluster = entity_cluster.get(name, "Uncategorized")
        # Merge sub-clusters into parent for display
        display_cluster = cluster.replace(" (2)", "")
        color = CLUSTER_COLORS.get(cluster, CLUSTER_COLORS.get(display_cluster, "#aaaaaa"))
        nodes.append({
            "id": name,
            "summary": entity["summary"],
            "source_notes": entity.get("source_notes", []),
            "cluster": display_cluster,
            "color": color
        })

# Load triples as links
links = []
with open(os.path.join(GRAPH, "triples.jsonl")) as f:
    for line in f:
        line = line.strip()
        if not line:
            continue
        triple = json.loads(line)
        source = triple["subject"]
        target_raw = triple["object"]
        predicate = triple["predicate"]

        # Direct match
        if source in node_ids and target_raw in node_ids:
            links.append({
                "source": source,
                "target": target_raw,
                "predicate": predicate,
                "source_note": triple.get("source_note")
            })
            continue

        # Try to find entity name referenced in the object text
        # Pattern: "entity name (description)" or "entity name"
        if source in node_ids:
            # Check if any known entity name appears in the object text
            matched = False
            for entity_name in sorted(node_ids, key=len, reverse=True):
                if entity_name in target_raw and entity_name != source:
                    links.append({
                        "source": source,
                        "target": entity_name,
                        "predicate": predicate,
                        "source_note": triple.get("source_note")
                    })
                    matched = True
                    break

# Only export the 10 main clusters
main_clusters = {k: v for k, v in CLUSTER_COLORS.items() if "(2)" not in k}
data = {
    "nodes": nodes,
    "links": links,
    "clusters": list(main_clusters.keys()),
    "colors": main_clusters
}

with open(os.path.join(ROOT, "docs", "data.json"), "w") as f:
    json.dump(data, f, indent=2)

print(f"Built data.json: {len(nodes)} nodes, {len(links)} links")
