import toml
from dataclasses import dataclass
from typing import List

@dataclass
class ChainConfig:
    decimals: int = 9
    NativeTokenWeiValue: int = 1
    NativeTokenGigaweiValue: int = int(1e6)
    NativeToken: str = 'Vietnam Stable Digital'
    NativeTokenSymbol: str = 'VSTD'
    NativeTokenValue = 1e9
    NativeTokenQuantity = 1e18
    MinimumGasPrice: int = 0
    FaucetAddress = "0x00000000000000000000000000000000faucet"
    MINT_KEY = "public_key.pem"
    BLOCK_HISTORY_LIMIT = 1000
    MAX_PEERS = 10
    validators: List[str] = []
    try:
        with open('config/validators.toml', 'r') as f:
            config = toml.load(f)
            validators = config['validators']
    except FileNotFoundError:
        validators = []

@dataclass
class FeatureFlags:
    DEBUG = False