def has_keys(d: dict, keys: list) -> bool:
    cur = d
    for k in keys:
        if k in cur:
            cur = cur[k]
        else:
            return False
    return True

# for entries lile [{'type': 'a', ...}, {'type': 'b', ...}]
def get_object(entries: list, type: str):
    if len(entries) == 0: return None
    for entry in entries:
        if 'type' not in entry:
            continue
        if entry['type'] == type:
            return entry
    return None