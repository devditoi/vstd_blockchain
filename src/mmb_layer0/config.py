from dataclasses import dataclass

@dataclass
class MMBConfig:
    decimals: int = 9
    mmbi: int = 1
    gmmbi: int = 1e6
    NativeToken: str = 'mmbi'
    NativeTokenSymbol: str = 'MMB'
    NativeTokenValue = 1e9
    NativeTokenQuantity = 1e9
    MinimumGasPrice: int = 100
    FaucetAddress = "0x00000000000000000000000000000000faucet"
    MINT_KEY = "public_key.pem"
