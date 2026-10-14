import hashlib
def unit_float(seed): return int.from_bytes(hashlib.sha256(seed.encode()).digest()[:8],'big')/float(2**64-1)
def bounded(seed,low,high): return low if high<=low else low+(high-low)*unit_float(seed)
def choose(seed,items):
    if not items:return None
    idx=min(len(items)-1,int(unit_float(seed)*len(items))); return items[idx]
