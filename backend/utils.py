import re
import os
from collections import defaultdict

def parse_edges(edge_list):
    accepted = []
    rejected = []
    seen_edges = set()
    repeated = set()

    for raw in edge_list:
        item = raw.strip()

        if not re.fullmatch(r"[A-Z]->[A-Z]", item) or item[0] == item[3]:
            rejected.append(item)
            continue

        if item in seen_edges:
            repeated.add(item)
            continue

        seen_edges.add(item)
        accepted.append(item)

    return accepted, rejected, list(repeated)

def create_adjacency(edges):
    adj = defaultdict(dict)
    child_tracker = {}
    child_nodes = set()

    for e in edges:
        src, dst = e.split("->")

        # multi-parent rule: first wins
        if dst in child_tracker:
            continue

        adj[src][dst] = {}
        child_tracker[dst] = src
        child_nodes.add(dst)

    return adj, child_nodes

def collect_nodes(adj):
    nodes = set(adj.keys())
    for p in adj:
        for c in adj[p]:
            nodes.add(c)
    return nodes

def to_undirected(adj):
    undirected = defaultdict(set)

    for p in adj:
        for c in adj[p]:
            undirected[p].add(c)
            undirected[c].add(p)

    return undirected


def split_into_groups(adj):
    graph = to_undirected(adj)
    visited = set()
    groups = []

    for node in collect_nodes(adj):
        if node in visited:
            continue

        stack = [node]
        group = set()

        while stack:
            current = stack.pop()
            if current in visited:
                continue

            visited.add(current)
            group.add(current)

            for neighbour in graph[current]:
                if neighbour not in visited:
                    stack.append(neighbour)

        groups.append(group)

    return groups


def check_cycle(start, adj, seen, path):
    if start in path:
        return True
    if start in seen:
        return False

    seen.add(start)
    path.add(start)

    for nxt in adj.get(start, {}):
        if check_cycle(nxt, adj, seen, path):
            return True

    path.remove(start)
    return False


def compute_depth(node, adj):
    children = adj.get(node, {})
    if not children:
        return 1

    return 1 + max(compute_depth(child, adj) for child in children)

def expand_tree(node, adj):
    result = {}
    for child in adj.get(node, {}):
        result[child] = expand_tree(child, adj)
    return result

def process_data(data):

    valid_edges, invalid_entries, duplicate_edges = parse_edges(data)

    adj, _ = create_adjacency(valid_edges)
    groups = split_into_groups(adj)

    output = []
    tree_count = 0
    cycle_count = 0
    deepest_root = ""
    max_depth = 0

    for group in groups:

        sub_adj = {node: adj.get(node, {}) for node in group}

        sub_children = set()
        for node in sub_adj:
            for child in sub_adj[node]:
                sub_children.add(child)

        roots = [n for n in group if n not in sub_children]

        # cycle group (no root)
        if len(roots) == 0:
            root = min(group)

            output.append({
                "root": root,
                "tree": {},
                "has_cycle": True
            })

            cycle_count += 1
            continue

        root = min(roots)

        visited = set()
        stack = set()

        if check_cycle(root, sub_adj, visited, stack):
            output.append({
                "root": root,
                "tree": {},
                "has_cycle": True
            })
            cycle_count += 1
        else:
            depth = compute_depth(root, sub_adj)

            output.append({
                "root": root,
                "tree": {root: expand_tree(root, sub_adj)},
                "depth": depth
            })

            tree_count += 1

            if depth > max_depth or (depth == max_depth and root < deepest_root):
                max_depth = depth
                deepest_root = root

    output.sort(key=lambda x: x["root"])

    return {
        "user_id": os.getenv("USER_ID", "default_user"),
        "email_id": os.getenv("EMAIL_ID", "default@email.com"),
        "college_roll_number": os.getenv("COLLEGE_ROLL_NUMBER", "0000"),
        "hierarchies": output,
        "invalid_entries": invalid_entries,
        "duplicate_edges": duplicate_edges,
        "summary": {
            "total_trees": tree_count,
            "total_cycles": cycle_count,
            "largest_tree_root": deepest_root
        }
    }