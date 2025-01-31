// Show token values from the wallet
// Get the address of different tokens
// Get the balance of the user's wallet

import { useEthers } from "@usedapp/core";
import helperConfig from "../helper-config.json";

// Sending the brownie config to the src folder
// Send the build folder

function Main() {
	const { chainId } = useEthers();
	const networkName = chainId ? helperConfig[chainId] : "dev";

	return <div>MainComponent</div>;
}

export default Main;
