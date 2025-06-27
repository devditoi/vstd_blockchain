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
- I think transaction need more data like timestamp and stuff lol\

## Solutions
- [x] Implement blockscan REST API (Ok it fine)
- [x] Save and search transaction
- [ ] Implemnt wallet
- [x] Implement web interface for blockscan (Yo it so niceeeee)
- [x] Yo we need to fix the test!!! (EZ:D)