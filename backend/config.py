import os
from dotenv import load_dotenv

load_dotenv()

def get_env(key, default):
    val = os.getenv(key)
    if not val or val.strip() == "":
        return default
    return val

ETHERSCAN_API_KEY = get_env("ETHERSCAN_API_KEY", "")
LLM_API_KEY = get_env("LLM_API_KEY", "")
LLM_BASE_URL = get_env("LLM_BASE_URL", "https://generativelanguage.googleapis.com/v1beta/openai/")
LLM_MODEL = get_env("LLM_MODEL", "gemini-3.8-flash")
OFFLINE = get_env("OFFLINE", "0") == "1"

CHAINS = {
    "ethereum": {
        "id": "ethereum",
        "chainid": 1,
        "history_provider": "etherscan",
        "base_url": "https://api.etherscan.io/v2/api",
        "rpc_url": get_env("RPC_URL_1", "https://ethereum-rpc.publicnode.com"),
        "explorer_tx_url": "https://etherscan.io/tx/{h}",
        "explorer_addr_url": "https://etherscan.io/address/{a}"
    },
    "base": {
        "id": "base",
        "chainid": 8453,
        "history_provider": "blockscout",
        "base_url": "https://base.blockscout.com/api",
        "rpc_url": get_env("RPC_URL_8453", "https://mainnet.base.org"),
        "explorer_tx_url": "https://basescan.org/tx/{h}",
        "explorer_addr_url": "https://basescan.org/address/{a}"
    },
    "arbitrum": {
        "id": "arbitrum",
        "chainid": 42161,
        "history_provider": "etherscan",
        "base_url": "https://api.etherscan.io/v2/api",
        "rpc_url": get_env("RPC_URL_42161", "https://arb1.arbitrum.io/rpc"),
        "explorer_tx_url": "https://arbiscan.io/tx/{h}",
        "explorer_addr_url": "https://arbiscan.io/address/{a}"
    }
}
