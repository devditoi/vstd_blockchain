import toml
from dataclasses import dataclass, field
from typing import List, ClassVar

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
    _DEFAULT_VALIDATORS: ClassVar[List[str]] = []
    try:
        with open('config/validators.toml', 'r') as f:
            config = toml.load(f)
            _DEFAULT_VALIDATORS = config['validators']
    except FileNotFoundError:
        _DEFAULT_VALIDATORS = []
    validators: List[str] = field(default_factory=lambda: list(ChainConfig._DEFAULT_VALIDATORS))

@dataclass
class FeatureFlags:
    DEBUG = False