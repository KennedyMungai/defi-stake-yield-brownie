"""Script containing some utility logic for the deployment script"""
import time

from brownie import (Contract, MockOperator, MockV3Aggregator,
                     VRFCoordinatorV2Mock, accounts, config, network, web3)

NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS = [
    "hardhat", "development", "ganache"]
LOCAL_BLOCKCHAIN_ENVIRONMENTS = NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS + [
    "mainnet-fork",
    "binance-fork",
    "matic-fork",
]

INITIAL_PRICE_FEED_VALUE = 2000_000_000_000_000_000_000

# Etherscan usually takes a few blocks to register the contract has been deployed
BLOCK_CONFIRMATIONS_FOR_VERIFICATION = (
    1 if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS else 6
)

contract_to_mock = {
    "eth_usd_price_feed": MockV3Aggregator,
}

DECIMALS = 18
INITIAL_VALUE = web3.toWei(2000, "ether")
BASE_FEE = 100000000000000000  # The premium
GAS_PRICE_LINK = 1e9  # Some value calculated depending on the Layer 1 cost and Link


def is_verifiable_contract() -> bool:
    """Function that returns True if the current network is a testnet

    Returns:
        bool: The nature of the network
    """
    return config["networks"][network.show_active()].get("verify", False)


def get_account(_index=None, _id=None):
    """The function to get an account

    Args:
        _index (int, optional): The index of the account. Defaults to None.
        _id (int, optional): The id of the account. Defaults to None.

    Returns:
        None: Nothing is returned
    """
    if _index:
        return accounts[_index]
    if network.show_active() in LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        return accounts[0]
    if _id:
        return accounts.load(_id)
    return accounts.add(config["wallets"]["from_key"])


def get_contract(contract_name):
    """If you want to use this function, go to the brownie config and add a new entry for
    the contract that you want to be able to 'get'. Then add an entry in the variable 'contract_to_mock'.
    You'll see examples like the 'link_token'.
        This script will then either:
            - Get a address from the config
            - Or deploy a mock to use for a network that doesn't have it

        Args:
            contract_name (string): This is the name that is referred to in the
            brownie config and 'contract_to_mock' variable.

        Returns:
            brownie.network.contract.ProjectContract: The most recently deployed
            Contract of the type specified by the dictionary. This could be either
            a mock or the 'real' contract on a live network.
    """
    contract_type = contract_to_mock[contract_name]
    if network.show_active() in NON_FORKED_LOCAL_BLOCKCHAIN_ENVIRONMENTS:
        if len(contract_type) <= 0:
            deploy_mocks()
        contract = contract_type[-1]
    else:
        try:
            contract_address = config["networks"][network.show_active(
            )][contract_name]
            contract = Contract.from_abi(
                contract_type._name, contract_address, contract_type.abi
            )
        except KeyError:
            print(
                f"{network.show_active()} address not found, perhaps you should add it to the config or deploy mocks?"
            )
            print(
                f"brownie run scripts/deploy_mocks.py --network {network.show_active()}"
            )
    return contract


def fund_with_link(
    contract_address,
    account=None,
    link_token=None,
    amount=1000000000000000000
):
    """The function to implement funding with Link tokens

    Args:
        contract_address (str): The address of the contract
        account (str, optional): The address of the funder. Defaults to None.
        link_token (int, optional): The token type. Defaults to None.
        amount (int, optional): THe amount being funded. Defaults to 1000000000000000000.

    Returns:
        None: Nothing is returned
    """
    account = account if account else get_account()
    link_token = link_token if link_token else get_contract("link_token")
    # Keep this line to show how it could be done without deploying a mock
    # tx = interface.LinkTokenInterface(link_token.address).transfer(
    #     contract_address, amount, {"from": account}
    # )
    tx = link_token.transfer(contract_address, amount, {"from": account})
    print(f"Funded {contract_address}")
    return tx


def deploy_mocks(decimals=DECIMALS, initial_value=INITIAL_PRICE_FEED_VALUE):
    """
    Use this script if you want to deploy mocks to a testnet
    """
    print(f"The active network is {network.show_active()}")
    print("Deploying Mocks...")
    account = get_account()
    print("Deploying Mock Price Feed...")
    mock_price_feed = MockV3Aggregator.deploy(
        decimals, initial_value, {"from": account}
    )
    print(f"Deployed to {mock_price_feed.address}")
    print("Deploying Mock VRFCoordinator...")
    mock_vrf_coordinator = VRFCoordinatorV2Mock.deploy(
        BASE_FEE, GAS_PRICE_LINK, {"from": account}
    )
    print(f"Deployed to {mock_vrf_coordinator.address}")



def listen_for_event(brownie_contract, event, timeout=200, poll_interval=2):
    """Listen for an event to be fired from a contract.
    We are waiting for the event to return, so this function is blocking.

    Args:
        brownie_contract ([brownie.network.contract.ProjectContract]):
        A brownie contract of some kind.

        event ([string]): The event you'd like to listen for.

        timeout (int, optional): The max amount in seconds you'd like to
        wait for that event to fire. Defaults to 200 seconds.

        poll_interval ([int]): How often to call your node to check for events.
        Defaults to 2 seconds.
    """
    web3_contract = web3.eth.contract(
        address=brownie_contract.address, abi=brownie_contract.abi
    )
    start_time = time.time()
    current_time = time.time()
    event_filter = web3_contract.events[event].createFilter(fromBlock="latest")
    while current_time - start_time < timeout:
        for event_response in event_filter.get_new_entries():
            if event in event_response.event:
                print("Found event!")
                return event_response
        time.sleep(poll_interval)
        current_time = time.time()
    print("Timeout reached, no event found.")
    return {"event": None}
