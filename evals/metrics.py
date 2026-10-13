def find_rank(retrieved: list[str], expected: str) -> int | None:
    """Return the position (1 = first) of the line that contains `expected`.
    Return None if no retrieved line contains it."""
    for position, text in enumerate(retrieved, start=1):
        if expected in text:
            return position
    return None

# Recall says whether the line was found at all. 
def recall_at_k(rank: int | None, k: int) -> float:
    """1.0 if the correct line is inside the top k, otherwise 0.0."""
    if rank is not None and rank <= k:
        return 1.0
    return 0.0

# MRR says how close to the top it was
def reciprocal_rank(rank: int | None) -> float:
    """1/rank. Rank 1 gives 1.0, rank 2 gives 0.5, rank 3 gives 0.33.
    Not found gives 0.0."""
    if rank is None:
        return 0.0
    return 1.0 / rank