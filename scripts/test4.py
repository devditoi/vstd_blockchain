
from layer0.utils.crypto.ECDSA_adapter import ECDSAAdapter
w = ECDSAAdapter.load_pub("mint_key")
print(w.to_string().hex())
