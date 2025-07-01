# Dev Log

## June 25, 2025

### Problems
- Current `self.chain` stores all blocks in memory → leads to scaling issues on long run.
- Old test case failed after changing gas rules → now transactions with `gasLimit = 0` are considered valid.
- The name `MMB` (old brand) feels unprofessional and lacks clarity.
- Current `self.chain` are used everywhere because in many cases I need to create a dummy chain, dummy node to fast compare, or deploy simplify abstract.
- Current chain deserialization assumes loading the entire chain at once, which is inefficient and unrealistic for syncing nodes in a real network.
- Block synchronization logic should not rely on serializing/deserializing the full chain, but rather support range-based fetching from peers.

### Solutions
- [x] Added `FileStorage` as new persistent chain backend (off-memory).
- [x] Created initial devlog to track major decisions.
- [x] Renamed project from `MMB` → `VSTD` (Vietnam Stable Digital) to improve clarity and positioning.
- [x] Updated test logic to reflect gas-free transaction support.
- [ ] Refactor all `self.chain` references to use new storage wrapper.
    - [ ] Replace all `self.chain` to the new storage wrapper
    - [ ] REWRITE all the old dummy chain logic for like, serialize, deserialize. 
    - [ ] Rewrite chain sync, chain deserialization

## June 26, 2025

### Problems
- Continue solving the chain sync problems and chain deserialization problems.
- Continue solving `Current chain deserialization assumes loading the entire chain at once, which is inefficient and unrealistic for syncing nodes in a real network.`
- Rename mmb_layer0 to layer0 for better naming
- Write some more test just in case for furthur testing environment
- Rewrite chain sync
- When reorg -> State change, need to save state diff to block for reverse.
- Create Fast API (temporary) for the blockscan -> Need to create block scan website
- Future task: Implement dynamic minting transaction!!!
- Save and request transaction
- Execution fail doesn't mean block is invalid

### Solutions
- [x] Depricated any chain sync and remove any other chain dummy objects.
- [x] Finish replacing all imports from mmb_layer0 to layer0
- [x] Refactor all `self.chain` references to use new storage wrapper.
    - [x] Replace all `self.chain` to the new storage wrapper
    - [x] Make normal block sync work
    - [x] ~~REWRITE~~ Depricated all the old dummy chain logic for like, serialize, deserialize. 
    - [x] Rewrite chain sync, chain deserialization
- [x] Rewrite chain sync logic
- [ ] Implement state diff logic
  - [ ] Capture state diff during tx execution
  - [ ] Store diff mapped to block height
  - [ ] Revert logic on reorg using diff
  - [ ] Optional: persist diff to disk (future-proof)
- [ ] Implement blockscan REST API
- [ ] Save and search transaction
- [x] Fix unexpected bug of nonce where nonce updated for 0x0 not for the sender
- [x] Refactor gas for transaction

## June 27, 2025

### Problems
- The state diff -> Not planed
- Now implement REST API (or RPC) for blockscan and a smallest wallet
- Make a chrome extension for a wallet
- Need to fix pytest error
- Finish blockscan
- Refactor gas for transaction 
- Need some addition metadata for transaction tho :D
- Very wierd worldstate mismatch for syncher ??
- I think transaction need more data like timestamp and stuff lol

## Solutions
- [x] Implement blockscan REST API (Ok it fine)
- [x] Save and search transaction
- [ ] Implement wallet
- [x] Implement web interface for blockscan (Yo it so niceeeee)
- [x] Yo we need to fix the test!!! (EZ:D)

## June 28, 2025

### Problems
- Need some addition metadata for transaction tho :D
- Very wierd worldstate mismatch for syncher ??
- I think transaction need more data like timestamp and stuff lol
- Make a chrome extension for a wallet (maybe :D)
- Need to fix network test, either implement multiserver testing or find a better way to test network

### Solutions
- [ ] Implement wallet
- [x] Check the worldstate mismatch
- [x] Implement transaction metadata
- [x] Fix integration test for node (because of peer limit)
- [x] Fix unit test when append metadata for transaction
- [x] Actually use those metadata for transaction
- [x] Fix why the node can't connect to the network (Or luck?)

## June 29, 2025

### Problems
- Make a chrome extension for a wallet (maybe :D)
- Nah Just make a react app for wallet
```python
# Sign block
consensus.sign_block(block)
block.miner = consensus.get_validators() # Hardcoded
```
- This shit took me many hours to figure out
- Not a error, Just signing (seal) block before setting the miner and it make me struggle :DDDD


### Solutions
- [x] Implement wallet UI
- [x] Fix some wallet bugs (Because the UI is so cool (AI generated))
- [x] Fix python typing because I switch to `vscode` :DD
- [x] Rewrite the address logic
- [ ] Implement wallet connetivity to the network
- [ ] Somewhere they need to implement miner that cause signature error

## June 30, 2025
### Problems
- The address logic is so bad (ok my life is suck it I don't care anymore)
- Continue interact react app for wallet
- Very weird transaction mismatch for client to server (Client side signing fail!!!)
- WHYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYYY
- ok my life is suck
- Javascript ECDSA SUCK
- Why there is space between the string because of jsonlight dumps??????
- {a: b} is not {a:b} ok my life is suckK
- Nah this bug make me sick
- Still not fixed it yet. The message is sync but still bad signature error
- Again, ok my life is suck today

### Solutions
- [ ] Implement wallet connetivity to the network
- [ ] Somewhere they need to implement miner that cause signature error
- [ ] First step at smart contract
- [ ] Dynamic config (mint, validator, ...) 


## July 1, 2025

## Problems
- Swtich to daemon wallet, CLI wallet.
- CLI wallet but UI is Webase (Nah you know what)
- Cry, rage, scream into the logs — but don’t stop.
- Because that bug?
- It didn't beat you.
- It forged you. 🔥
- Now I fix the bug
- No one can beat me.

The bug is relatively simple
```ts
tx.signature = signature.slice(2); // Assumes signature starts with '0x'
```
There is no 0x so cutting the first 2 characters mean cut the whole signature. lol


> “Sometimes, it’s just a damn 1-line bug that makes you beg your entire ecosystem of JavaScript.”
> — “Quanvndzai 2025”

## Solutions
~~- [ ] Implement CLI daemon wallet that provide API for the wallet web app~~
~~- [ ] Rewrite the wallet web app.~~
- [Status: FIXED] 
- [ ] First step at smart contract
- [ ] Dynamic config (mint, validator, ...) 