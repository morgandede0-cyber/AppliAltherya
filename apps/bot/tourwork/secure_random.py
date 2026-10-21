"""OS-backed randomness for outcomes; seeded Random is for reproducible plans only.

SystemRandom exposes no reusable generator state. Never replace it with the
seeded helper for loot, cards, money outcomes or heist combinations.
"""
from random import Random, SystemRandom

class OutcomeRandom(SystemRandom):
    # Explicit seeded generators remain available for cosmetic race ordering.
    Random = Random

random = OutcomeRandom()
