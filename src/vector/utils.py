import numpy as np

def minmax_scale(x):
    arr = np.array(list(x), dtype=float)
    if arr.size == 0:
        return arr
    mn, mx = float(np.min(arr)), float(np.max(arr))
    if mx - mn < 1e-12:
        return np.zeros_like(arr)
    return (arr - mn) / (mx - mn)

def safe_div(a, b, eps=1e-9):
    return float(a) / float(b + eps)

def normalize_dict(d):
    keys = list(d.keys())
    vals = np.array([d[k] for k in keys], dtype=float)
    mn, mx = float(np.min(vals)), float(np.max(vals))
    if mx - mn < 1e-12:
        scaled = np.zeros_like(vals)
    else:
        scaled = (vals - mn) / (mx - mn)
    return {k: float(v) for k, v in zip(keys, scaled)}

def round_robin_by_group(items, group_fn, k):
    from collections import defaultdict, deque
    groups = defaultdict(list)
    for it in items:
        groups[group_fn(it)].append(it)
    for g in groups:
        groups[g] = deque(groups[g])
    order = sorted(groups.keys(), key=lambda g: -len(groups[g]))
    out = []
    while len(out) < k and any(groups[g] for g in order):
        for g in order:
            if groups[g]:
                out.append(groups[g].popleft())
                if len(out) >= k:
                    break
    return out
