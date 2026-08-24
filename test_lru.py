from lru import LRU

def test_eviction_order():
    c = LRU(2)
    c.put("a", 1)
    c.put("b", 2)
    c.get("a")          # a is now most recently used
    c.put("c", 3)       # evicts b
    assert c.get("b") is None
    assert c.get("a") == 1
    assert c.get("c") == 3

def test_get_refreshes_recency():
    c = LRU(2)
    c.put("a", 1)
    c.put("b", 2)
    c.get("a")
    c.put("c", 3)       # should evict b, not a
    assert c.get("a") == 1, "get() must refresh recency"
