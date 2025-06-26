from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import Dict, Any, List
import uvicorn
from layer0.node.node import Node
from layer0.p2p.peer_type.remote_peer import RemotePeer
from layer0.p2p.udp_protocol import UDPProtocol
from layer0.blockchain.core.block import Block  # Assuming this is the correct import for Block

# Initialize FastAPI app
app = FastAPI(title="VSTD Blockchain Node API", version="1.0.0")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
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
    blockchain = master.blockchain
    
    latest_block = blockchain.get_latest_block()
    return {
        "block": block_to_dict(latest_block)
    }

@app.get("/blocks/height/{height}", response_model=Dict[str, Any])
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

@app.get("/blockchain/status", response_model=Dict[str, Any])
async def get_blockchain_status() -> Dict[str, Any]:
    """Get the current status of the blockchain."""
    blockchain = master.blockchain
    return {
        "height": blockchain.get_height(),
        "peer_count": len(master.node_event_handler.peers)
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

# @app.post("/transaction/post", response_model=Dict[str, Any])
# async def post_transaction(transaction: Dict[str, Any]) -> Dict[str, Any]:
#     """Post a transaction to the blockchain."""
#     print(transaction)

def block_to_dict(block: Block) -> str:
    """Convert a Block object to a dictionary."""
    return block.to_string()

if __name__ == "__main__":
    # import threading
    
    # Start the FastAPI server in a separate thread
    # def run_api():
    uvicorn.run(app, host="0.0.0.0", port=8000) # Just use main thread lol
    #
    # api_thread = threading.Thread(target=run_api, daemon=True)
    # api_thread.start()
