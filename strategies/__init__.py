"""
Strategy registry - automatically discovers and registers all strategies.
"""

from .base import BaseStrategy
from .support_resistance import SupportResistanceStrategy


# Registry of all available strategies
STRATEGIES = {
    'support_resistance': SupportResistanceStrategy(),
}


def get_all_strategies():
    """Get all registered strategies."""
    return STRATEGIES


def get_strategy(strategy_id: str) -> BaseStrategy:
    """Get a specific strategy by ID."""
    return STRATEGIES.get(strategy_id)


def get_strategy_ids():
    """Get list of all strategy IDs."""
    return list(STRATEGIES.keys())


def get_strategy_names():
    """Get list of all strategy names."""
    return [strategy.name for strategy in STRATEGIES.values()]
