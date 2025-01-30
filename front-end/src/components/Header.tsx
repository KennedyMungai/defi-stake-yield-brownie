import { useEthers } from "@usedapp/core";

const Header = () => {
	const { account, activateBrowserWallet, deactivate } = useEthers();

	const isConnected = account !== undefined;

	return (
		<header className="h-14 shadow-sm flex items-center p-2">
			{isConnected ? (
				<button
					className="bg-slate-400 p-2 rounded-sm hover:bg-slate-400/90 ml-auto"
					onClick={deactivate}
				>
					Disconnect
				</button>
			) : (
				<button
					className="bg-slate-400 p-2 rounded-sm hover:bg-slate-400/90 ml-auto"
					onClick={activateBrowserWallet}
				>
					Connect
				</button>
			)}
		</header>
	);
};

export default Header;
