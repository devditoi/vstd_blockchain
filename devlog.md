# Dev Log

## June 25, 2025

### Problems
- Current `self.chain` stores all blocks in memory → leads to scaling issues on long run.
- Old test case failed after changing gas rules → now transactions with `gasLimit = 0` are considered valid.
- The name `MMB` (old brand) feels unprofessional and lacks clarity.

### Solutions
- [x] Added `FileStorage` as new persistent chain backend (off-memory).
- [x] Created initial devlog to track major decisions.
- [x] Renamed project from `MMB` → `VSTD` (Vietnam Stable Digital) to improve clarity and positioning.
- [x] Updated test logic to reflect gas-free transaction support.
- [ ] Refactor all `self.chain` references to use new storage wrapper.
