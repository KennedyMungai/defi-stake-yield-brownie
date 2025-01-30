import { DAppProvider, Mainnet } from "@usedapp/core";
import { StrictMode } from "react";
import { createRoot } from "react-dom/client";
import App from "./App.tsx";
import "./index.css";
import Header from "./components/Header.tsx";

const config = {
	readOnlyChainId: Mainnet.chainId,
	readOnlyUrls: {
		[Mainnet.chainId]: `https://mainnet.infura.io/v3/${
			import.meta.env.VITE_INFURA_KEY
		}`,
	},
};

createRoot(document.getElementById("root")!).render(
	<StrictMode>
		<DAppProvider config={config}>
			<Header />
			<App />
		</DAppProvider>
	</StrictMode>,
);
