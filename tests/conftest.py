"""Shared pytest configuration and fixtures for all tests."""

import pytest
import sys
from pathlib import Path

# Add project root to Python path for imports
PROJECT_ROOT = Path(__file__).parent.parent
sys.path.insert(0, str(PROJECT_ROOT))


@pytest.fixture
def sample_linked_list():
    """Fixture providing sample list data for linked list problems."""
    return [9, 9, 9, 9, 9, 9, 9]


@pytest.fixture
def sample_array():
    """Fixture providing sample array data."""
    return [1, 2, 3, 4, 5]


@pytest.fixture
def sample_tree_data():
    """Fixture providing sample tree node data."""
    return {
        'values': [3, 9, 20, 15, 7],
        'structure': 'binary'
    }


def pytest_configure(config):
    """Configure pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
