// static/wallet.js
import {
  createThirdwebClient,
  getContract,
} from "thirdweb";

import {
  getBalance,
  transfer as transferERC20,
} from "thirdweb/extensions/erc20";

import {
  balanceOf,
  claimTo,
  safeTransferFrom,
  lazyMint,
} from "thirdweb/extensions/erc1155";

import {
  prepareContractCall,
  sendTransaction,
} from "thirdweb";

// ✅ Initialize Thirdweb client
const client = createThirdwebClient({
  clientId: "YOUR_CLIENT_ID", // <-- already added by you
});

// ✅ Define Ethereum chain
import { defineChain } from "thirdweb/chains";
const chain = defineChain(1); // Ethereum Mainnet

// ✅ Contracts (hard-coded with your addresses)
const tokenContract = getContract({
  client,
  chain,
  address: "0x244a5cEb1F7Fc19BfbD38dE859f1FCA4a6Fa8527", // ERC-20 token
});

const nftContract = getContract({
  client,
  chain,
  address: "0x6cf2eb73f97262F4A2a7Fb5fA7c2cd22715eAA51", // ERC-1155 NFT
});

// ✅ Globals
let currentAccount = null;

// -----------------------------
// 🦊 Connect Wallet
// -----------------------------
async function connectWallet() {
  if (typeof window.ethereum !== "undefined") {
    try {
      const accounts = await window.ethereum.request({
        method: "eth_requestAccounts",
      });
      currentAccount = accounts[0];
      document.getElementById("wallet-address").innerText = `Connected: ${currentAccount}`;
      console.log("Wallet connected:", currentAccount);

      // Send address to Flask backend
      fetch("/api/save_wallet", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ address: currentAccount }),
      });

      // Load token balance
      await fetchTokenBalance();

    } catch (err) {
      console.error("User rejected connection:", err);
    }
  } else {
    alert("MetaMask not detected! Please install it.");
  }
}

// -----------------------------
// 💰 Fetch Token Balance
// -----------------------------
async function fetchTokenBalance() {
  if (!currentAccount) return;
  try {
    const bal = await getBalance({
      contract: tokenContract,
      address: currentAccount,
    });
    document.querySelector(".header p").innerText = `Tokens: ${bal.displayValue}`;
  } catch (err) {
    console.error("Error fetching balance:", err);
  }
}

// -----------------------------
// 🖼️ NFT Ownership Check
// -----------------------------
async function checkNFTOwnership() {
  if (!currentAccount) return alert("Connect wallet first!");
  try {
    const bal = await balanceOf({
      contract: nftContract,
      owner: currentAccount,
      tokenId: 0, // default tokenId
    });
    updateStatus(`NFT Ownership: ${bal}`);
  } catch (err) {
    console.error(err);
    updateStatus("Error checking ownership");
  }
}

// -----------------------------
// 🎁 Claim NFT
// -----------------------------
async function claimNFT() {
  if (!currentAccount) return alert("Connect wallet first!");
  try {
    const tx = claimTo({
      contract: nftContract,
      to: currentAccount,
      tokenId: 0, // default tokenId
      quantity: 1,
    });
    const { transactionHash } = await sendTransaction({
      transaction: tx,
      account: currentAccount,
    });
    updateStatus(`✅ NFT Claimed! Tx: ${transactionHash}`);
  } catch (err) {
    console.error(err);
    updateStatus("❌ Error claiming NFT");
  }
}

// -----------------------------
// 🖼️ Transfer NFT
// -----------------------------
async function transferNFT() {
  if (!currentAccount) return alert("Connect wallet first!");
  const to = prompt("Enter recipient wallet address:");
  if (!to) return;
  try {
    const tx = safeTransferFrom({
      contract: nftContract,
      from: currentAccount,
      to,
      tokenId: 0, // default tokenId
      amount: 1,
    });
    const { transactionHash } = await sendTransaction({
      transaction: tx,
      account: currentAccount,
    });
    updateStatus(`✅ NFT Transferred! Tx: ${transactionHash}`);
  } catch (err) {
    console.error(err);
    updateStatus("❌ Error transferring NFT");
  }
}

// -----------------------------
// 🪙 Send Tokens
// -----------------------------
async function sendTokens() {
  if (!currentAccount) return alert("Connect wallet first!");
  const to = prompt("Enter recipient wallet address:");
  const amount = prompt("Enter amount to send:");
  if (!to || !amount) return;
  try {
    const tx = transferERC20({
      contract: tokenContract,
      to,
      amount: amount.toString(),
    });
    const { transactionHash } = await sendTransaction({
      transaction: tx,
      account: currentAccount,
    });
    updateStatus(`✅ Tokens Sent! Tx: ${transactionHash}`);
  } catch (err) {
    console.error(err);
    updateStatus("❌ Error sending tokens");
  }
}

// -----------------------------
// 🛠️ Lazy Mint NFT
// -----------------------------
async function lazyMintNFT() {
  if (!currentAccount) return alert("Connect wallet first!");
  const uri = prompt("Enter metadata URI (IPFS/URL):");
  if (!uri) return;
  try {
    const tx = await prepareContractCall({
      contract: nftContract,
      method: "function lazyMint(uint256 _amount, string _baseURIForTokens, bytes _data) returns (uint256 batchId)",
      params: [1, uri, "0x"],
    });
    const { transactionHash } = await sendTransaction({
      transaction: tx,
      account: currentAccount,
    });
    updateStatus(`✅ Lazy Minted! Tx: ${transactionHash}`);
  } catch (err) {
    console.error(err);
    updateStatus("❌ Error lazy minting NFT");
  }
}

// -----------------------------
// 📢 UI Helper
// -----------------------------
function updateStatus(message) {
  const statusBox = document.getElementById("status-box");
  if (statusBox) {
    statusBox.innerText = message;
  } else {
    alert(message);
  }
}

// Expose functions to HTML
window.connectWallet = connectWallet;
window.checkNFTOwnership = checkNFTOwnership;
window.claimNFT = claimNFT;
window.transferNFT = transferNFT;
window.sendTokens = sendTokens;
window.lazyMintNFT = lazyMintNFT;
