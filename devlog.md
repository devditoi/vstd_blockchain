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

### Solutions
- [x] Depricated any chain sync and remove any other chain dummy objects.
- [x] Finish replacing all imports from mmb_layer0 to layer0
- [?] Refactor all `self.chain` references to use new storage wrapper.
    - [x] Replace all `self.chain` to the new storage wrapper
    - [x] Make normal block sync work
    - [ ] REWRITE all the old dummy chain logic for like, serialize, deserialize. 
    - [ ] Rewrite chain sync, chain deserialization