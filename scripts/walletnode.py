from layer0.utils.crypto.signer import SignerFactory
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from layer0.p2p.peer_type.remote_peer import RemotePeer
from layer0.wallet.wallet_remote import WalletRemote
import random
from pathlib import Path
import json


CONFIG_PATH = Path("config.json")
if not CONFIG_PATH.exists():
    # Config file not found, create a default one
    (pk, prk) = SignerFactory().get_signer().gen_key()
    SignerFactory().get_signer().save("keypair", pk, prk)
    default_config = {
        "keypair": "keypair",
        "peers": [
            "127.0.0.1:5000"
        ]
    }
    
    # Save to config.json
    with open(CONFIG_PATH, "w") as f:
        json.dump(default_config, f)

with open(CONFIG_PATH, "r") as f:
    config = json.load(f)

# --- Khởi tạo dynamic port và kết nối peer ---
PORT: int = random.randint(8000, 9999)
master: RemotePeer = RemotePeer("127.0.0.1", 5000)
wallet: WalletRemote = WalletRemote(master, "127.0.0.1", PORT)

# --- Khởi tạo FastAPI ---
app = FastAPI()

# --- Thiết lập CORS ---
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],  # Vite default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Route test frontend gọi thử ---
@app.get("/api/address")
def get_address():
    return {"address": wallet.address}

# --- Route gửi transaction thử ---
@app.post("/api/send")
async def send_transaction(req: Request):
    # data = await req.json()
    # to_address = data.get("to")
    # amount = int(data.get("amount"))

    # Tạo transaction dummy — bạn sửa lại tùy loại tx bạn cần
    # tx = MintBurnTransaction(wallet.address, to_address, amount)
    # wallet.sign_and_post_transaction(tx)

    return {"status": "sent"}

# --- Run bằng uvicorn ---
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("server:app", host="127.0.0.1", port=PORT, reload=False)
