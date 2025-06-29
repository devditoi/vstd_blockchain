from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import uvicorn
import threading
import time
import random
from layer0.blockchain.core.transaction_type import MintBurnTransaction
from layer0.blockchain.processor.transaction_processor import TransactionProcessor
from layer0.node.node import Node
from layer0.p2p.peer_type.remote_peer import RemotePeer
from layer0.p2p.udp_protocol import UDPProtocol
from layer0.blockchain.core.block import Block  # Assuming this is the correct import for Block
from layer0.utils.hash import HashUtils
from layer0.wallet.wallet import Wallet
from layer0.wallet.wallet_remote import WalletRemote

# Initialize FastAPI app
app = FastAPI(title="VSTD Blockchain Node API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
    ],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize node
master = Node()
# master.import_key("validator_key")
master.debug()

# Setup P2P network
protocol = UDPProtocol(master.node_event_handler, 9999)
master.set_origin("127.0.0.1:9999")
other = RemotePeer("127.0.0.1", 5000)
master.node_event_handler.subscribe(other)

# API Endpoints
@app.get("/", response_model=Dict[str, str])
async def root() -> Dict[str, str]:
    """Root endpoint that returns a welcome message."""
    return {"message": "Welcome to VSTD Blockchain Node API"}

@app.get("/blocks/latest", response_model=Dict[str, Any])
async def get_latest_block() -> any:
    """Get the latest block in the blockchain."""
    latest_block = master.blockchain.get_latest_block()
    return {
        "block": block_to_dict(latest_block)
    }

@app.get("/blocks", response_model=Dict[str, Any])
async def get_blocks(skip: int = 0, limit: int = 10):
    blocks = []
    # Actually Skips are down movement
    actual_start = master.blockchain.get_height() - skip - 1 # Offset by 1
    actual_end = max(actual_start - limit, 0)
    print(actual_start, actual_end)
    for i in range(actual_start, actual_end, -1):
        block = master.get_block(i)
        blocks.append(block_to_dict(block))
    return {"blocks": blocks}

@app.get("/block/{height}/transactions", response_model=Dict[str, Any])
async def get_block_transactions(height: int, skip: int = 0, limit: int = 10) -> any:
    block = master.get_block(height)
    return {
        "transactions": block.data
    }

@app.get("/transaction/{tx_hash}", response_model=Dict[str, Any])
async def get_transaction(tx_hash: str) -> any:
    return {
        "transaction": master.get_tx(tx_hash).to_string_with_offchain_data()
    }

@app.get("/transactions", response_model=Dict[str, Any])
async def get_transactions() -> any:
    return {
        "transactions": master.get_txs()
    }

@app.get("/address/{address}", response_model=Dict[str, Any])
async def get_balance(address: str) -> any:
    return {
        "address": address,
        "balance": master.get_balance(address),
        "nonce": master.get_nonce(address),
    }

@app.get("/address/{address}/transactions", response_model=Dict[str, Any])
async def get_transactions(address: str) -> any:
    txs = master.query_tx(address, "sender")
    txs2 = master.query_tx(address, "to")
    txs.extend(txs2)
    # Need to clear out duplicates hashes
    # print(txs)
    # print(type(txs[0]))
    unique_hashes = set()
    unique_txs = []
    for tx in txs:
        if tx["hash"] not in unique_hashes:
            unique_hashes.add(tx["hash"])
            unique_txs.append(tx)
    return {
        "transactions": unique_txs
    }

@app.get("/blocks/{height}", response_model=Dict[str, Any])
async def get_block_by_height(height: int) -> any:
    """Get a block by its height."""
    blockchain = master.blockchain
    try:
        block = blockchain.get_block(height)
        return {
            "block": block_to_dict(block)
        }
    except (IndexError, ValueError) as e:
        raise HTTPException(status_code=404, detail=str(e))

@app.get("/network-status", response_model=Dict[str, Any])
async def get_blockchain_status() -> Dict[str, Any]:
    """Get the current status of the blockchain."""
    blockchain = master.blockchain
    return {
        "height": blockchain.get_height(),
    }

@app.get("/transaction/{tx_hash}", response_model=Dict[str, Any])
async def get_transaction(tx_hash: str) -> Dict[str, Any]:
    """Get a transaction by its hash."""
    blockchain = master.blockchain
    transaction = blockchain.get_tx(tx_hash)

    if transaction is None:
        raise HTTPException(status_code=404, detail="Transaction not found")

    return {
        "transaction": transaction.to_string()
    }

@app.post("/transaction/post", response_model=Dict[str, Any])
async def post_transaction(transaction: str) -> Dict[str, Any]:
    """Post a transaction to the blockchain."""
    if not TransactionProcessor.check_valid_transaction(transaction):
        raise HTTPException(status_code=400, detail="Invalid transaction format")
    transaction = TransactionProcessor.cast_transaction(transaction)

    return {
        "transaction_hash": transaction.hash
    }


def block_to_dict(block: Block) -> str:
    """Convert a Block object to a dictionary."""
    return block.to_string()

if __name__ == "__main__":
    # import threading
    
    # Start the FastAPI server in a separate thread
    # def run_api():
    uvicorn.run(app, host="127.0.0.1", port=8000) # Just use main thread lol

    # api_thread = threading.Thread(target=run_api, daemon=True)
    # api_thread.start()

    # RPeer = RemotePeer("127.0.0.1", 5000)
    # w = WalletRemote(RPeer, "127.0.0.1", 8001)
    # i = 1
    # while True:
    #     time.sleep(5)
    #     # Mock data (transaction) for test (aka add random transaction to mempool)
    #     random_people = random.randint(1, 999999)
    #     addr = HashUtils.sha256(str(random_people))
    #     tx = MintBurnTransaction(w.address ,addr, 1000, int(time.time() * 1000), i, 0)
    #     i += 1
    #
    #     w.sign_and_post_transaction(tx)

