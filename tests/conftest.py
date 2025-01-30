"""The conftest file for pytest"""
import pytest
from web3 import Web3


@pytest.fixture
def amount_staked():
    """The fixture for the amount staked

    Returns:
        Ether: 1 ether
    """
    return Web3.toWei(1, "ether")
