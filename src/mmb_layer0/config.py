from dataclasses import dataclass

@dataclass
class MMBConfig:
    decimals: int = 9
    mmbi: int = 1
    gmmbi: int = 1e6
    NativeToken: str = 'mmbi'
    NativeTokenSymbol: str = 'MMB'
    NativeTokenValue = 1e9 # 1 MMB
    NativeTokenQuantity = 1e18 # Total token
    MinimumGasPrice: int = 0
    FaucetAddress = "0x00000000000000000000000000000000faucet"
    MINT_KEY = "public_key.pem"
    BLOCK_HISTORY_LIMIT = 1000
