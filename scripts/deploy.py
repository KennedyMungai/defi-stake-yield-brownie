"""The contract deployment script"""
import json
import yaml
from brownie import DappToken, TokenFarm, config, network
from web3 import Web3

from scripts.utils import get_account, get_contract

KEPT_BALANCE = Web3.toWei(100, "ether")


def deploy_token_farm_and_dapp_token(update_front_end=False):
    """
    Deploys the DappToken and TokenFarm contracts, and transfers most of the DappToken supply to the TokenFarm contract.
    The DappToken contract is deployed with the specified account as the owner.
    The TokenFarm contract is deployed with the DappToken contract address as the only argument.
    Most of the DappToken supply is transferred to the TokenFarm contract.
    The specified account is then set as the authorized sender for the DappToken contract.
    The dai price feed contract is added as an allowed token on the TokenFarm contract with the specified account.
    Finally, the TokenFarm and DappToken contracts are returned.
    """
    account = get_account()
    dapp_token = DappToken.deploy({"from": account})
    token_farm = TokenFarm(
        dapp_token.address,
        {
            "from": account
        },
        publish_source=config["networks"][network.show_active()].get(
            "verify", False)
    )
    tx = dapp_token.transfer(
        token_farm.address,
        dapp_token.totalSupply() - KEPT_BALANCE,
        {
            "from": account
        }
    )
    tx.wait(1)

    # Tokens: dapp_token,weth_token, fau_token / dai
    dict_of_allowed_tokens = {
        dapp_token: get_contract("dai_usd_price_feed"),
    }

    add_allowed_tokens(
        token_farm,
        dict_of_allowed_tokens,
        account
    )

    if update_front_end:
        update_front_end()

    return token_farm, dapp_token


def add_allowed_tokens(token_farm, dict_of_allowed_tokens, account):
    """
    Adds allowed tokens to the TokenFarm contract and sets their respective price feed contracts.

    Args:
        token_farm: The TokenFarm contract instance.
        dict_of_allowed_tokens (dict): A dictionary where keys are token instances and values are 
                                       the corresponding price feed contract addresses.
        account: The account from which transactions will be sent.

    Returns:
        The updated TokenFarm contract instance.
    """

    for token in dict_of_allowed_tokens:
        add_tx = token_farm.addAllowedTokens(token.address, {"from": account})
        add_tx.wait(1)
        set_tx = token_farm.setPriceFeedContract(
            token.address,
            dict_of_allowed_tokens[token],
            {
                "from": account
            }
        )
        set_tx.wait(1)

    return token_farm


def update_front_end():
    """Sending the config information to the frontend"""
    with open('../brownie-config.yaml', "r", encoding="utf-8") as brownie_config:
        config_dict = yaml.load(brownie_config, Loader=yaml.FullLoader)

        with open("../front-end/src/brownie-config.json", "w", encoding="utf-8") as brownie_config_json:
            json.dump(config_dict, brownie_config_json, indent=4)

    print('Frontend updated')


def main():
    """
    The main deployment script

    This script will deploy a DappToken and a TokenFarm and will transfer
    almost all of the DappToken supply to the TokenFarm (so that the owner
    of the TokenFarm has little to no DappTokens)
    """
    deploy_token_farm_and_dapp_token()
