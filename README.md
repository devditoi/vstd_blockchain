# 💵🇻🇳 VSTD Blockchain Network

[![Build and Release](https://github.com/devditoi/vstd_blockchain/actions/workflows/build_and_release.yaml/badge.svg)](https://github.com/devditoi/vstd_blockchain/actions/workflows/build_and_release.yaml)
[![Run Tests](https://github.com/devditoi/vstd_blockchain/actions/workflows/test.yaml/badge.svg)](https://github.com/devditoi/vstd_blockchain/actions/workflows/test.yaml)

**VSTD Blockchain** is a custom-built experimental blockchain system designed from scratch with a modular, multi-layered architecture. It features a basic **Proof of Authority (PoA)** consensus, built-in smart contract handling, and support for decentralized applications (dApps) via a web interface.

---

## 🔧 System Architecture

The system is organized into **three primary layers**:

### 🧩 Layer 0 – Core Blockchain (Consensus & Networking)
- Full blockchain engine: blocks, mempool, hashing
- **PoA Consensus**: only authorized leaders are allowed to sign blocks
- Peer-to-peer node communication and block propagation
- Each node has its own private/public keypair (RSA or ECDSA)
- Signature validation and block rejection logic

### 📜 Layer 1 – Smart Contract & Token Layer
- Transaction types supported:
  - `mintburn` (native VSTD token)
  - `native`, `transfer`
  - `stake`, `deploy_contract`, `call_contract` (under development)
- Smart contract data handled via `transactionData` field
- Cryptographic abstraction layer: pluggable sign/verify adapters (RSA, ECDSA)

### 🌐 Layer 2 – dApps & Web3 Interface
- User-facing frontend interfaces (in progress)
- Features: Wallets, Token Dashboard, Custom DEX
- Support for Web3 or custom RPC API

---

## ✅ Completed Features

- [x] PoA-based block creation and signature validation
- [x] Node synchronization and propagation of valid blocks
- [x] Cryptographic adapter system (RSA, ECDSA)
- [x] Minting restricted to authorized keys
- [x] Hex-encoded block outputs for readability
- [x] Validator configuration via TOML file

---

## ⚙️ Configuration

The blockchain uses a TOML configuration file for validator management:

1. Create `config/validators.toml`
2. Add validator public keys in the format:
```toml
validators = [
    "public_key_1",
    "public_key_2"
]
```

---

## 🚧 Roadmap

- [ ] Lightweight VM engine for smart contracts
- [ ] Stake-based validator rotation
- [ ] REST/Web3 APIs and explorer UI
- [ ] Cross-chain bridge & asset-backed token logic (e.g., USDT, BTC)
- [ ] NFT & DAO modules

---

## 📜 License

MIT License – this project is intended for educational and experimental purposes.

---

## 👤 Developer

**Lê Minh Quân** – Independent blockchain researcher and developer.
