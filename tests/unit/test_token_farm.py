"""Test token farm test script"""
import pytest
from brownie import network, exceptions

from scripts.deploy import deploy_token_farm_and_dapp_token
from scripts.utils import (LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account,
                           get_contract)


def set_price_feed_contract():
    # Arrange
    """
    Test that the price feed contract can be set for a given token, and that
    only the owner of the contract can do so.
    """
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local network testing")

    account = get_account()
    non_owner = get_account(_index=1)
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()

    # Act
    price_feed_address = get_contract("eth_price_feed_address")
    token_farm.setPriceFeedContract(
        dapp_token.address,
        price_feed_address,
        {
            "from": account
        }
    )

    # Assert
    assert token_farm.tokenPriceFeedMapping[dapp_token.address] == price_feed_address

    with pytest.raises(exceptions.VirtualMachineError):
        token_farm.setPriceFeedContract(
            dapp_token.address,
            price_feed_address,
            {
                "from": non_owner
            }
        )


def test_stake_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local network testing")

    account = get_account()
    token_farm, dapp_token = deploy_token_farm_and_dapp_token()

    # Act
    dapp_token.approve(
        token_farm.address,
        amount_staked,
        {
            "from": account
        }
    )

    token_farm.stakeTokens(
        amount_staked,
        dapp_token.address,
        {
            "from": account
        }
    )

    # Assert
    assert (
        token_farm.stakingBalance(
            dapp_token.address, account.address) == amount_staked
    )


def test_issue_tokens():
    # Arrange
    pass
