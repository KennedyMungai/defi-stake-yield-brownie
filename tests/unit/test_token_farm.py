"""Test token farm test script"""
import pytest
from brownie import network, exceptions

from scripts.deploy import deploy_token_farm_and_dapp_token
from scripts.utils import (INITIAL_PRICE_FEED_VALUE, LOCAL_BLOCKCHAIN_ENVIRONMENTS, get_account,
                           get_contract)


def set_price_feed_contract():
    """
    Test that the price feed contract can be set for a given token, and that
    only the owner of the contract can do so.
    """
    # Arrange
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
    """
    Test that a user can stake tokens to the TokenFarm contract, and that their
    staking balance is updated, as well as the number of unique tokens they have
    staked. Also tests that the user is added to the list of stakers.
    """
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
            dapp_token.address, account.address)
    ) == amount_staked
    assert token_farm.uniqueTokensStaked(account.address) == 1
    assert token_farm.stakers(0) == account.address
    return token_farm, dapp_token


def test_issue_tokens(amount_staked):
    # Arrange
    if network.show_active() not in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        pytest.skip("Only for local network testing")

    account = get_account()
    token_farm, dapp_token = test_stake_tokens(amount_staked)
    starting_balance = dapp_token.balanceOf(account.address)

    # Act
    token_farm.issueTokens({"from": account})

    # Arrange
    # We are staking 1 dapp_token ==in price to 1 ETH
    assert (dapp_token.balanceOf(account.address) ==
            starting_balance + INITIAL_PRICE_FEED_VALUE)
