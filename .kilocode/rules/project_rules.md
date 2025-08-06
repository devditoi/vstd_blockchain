# BlockchainNetwork Project Rules

## 1. Naming Conventions
   - Variable names use: `snake_case` (e.g., `public_key`, `private_key`, `world_state`)
   - Function names follow: `snake_case` (e.g., `get_height()`, `process_tx()`, `propose_block()`)
   - File names use: `snake_case.py` (e.g., `block.py`, `node.py`, `hash.py`)
   - Constants: `UPPER_SNAKE_CASE` (e.g., `DEBUG`, `NativeTokenValue`, `MinimumGasPrice`)
   - Class names: `PascalCase` (e.g., `Block`, `Node`, `HashUtils`)

## 2. Code Style
   - Indentation: 4 spaces
   - Quotes: Single `'` quotes for strings, double `"` for docstrings
   - Trailing commas: allowed in multi-line structures
   - Semicolons: optional (not typically used)

## 3. Linting & Formatting
   - Linter used: None explicitly configured
   - Formatter: None explicitly configured
   - Config files: `pyproject.toml`, `pytest.ini`

## 4. Typing & Docs
   - Type system: Python typing (e.g., `tuple[PublicKey, PrivateKey]`, `str | None`)
   - Required docstrings or JSDoc for functions/classes: Yes, for public methods
   - Interface naming: Not using `I` prefix (e.g., `ChainConfig` not `IChainConfig`)

## 5. Project Structure
   - Folder structure style: layer-based (src/layer0/) with feature-based subdirectories
   - Common entry points: `scripts/run_node.py`, `src/layer0/node/node.py`
   - Test location: `/tests` with `/tests/units` and `/tests/integration` subdirectories

## 6. Framework/Library Usage
   - Core frameworks: Custom blockchain implementation
   - State management: Custom world state implementation
   - HTTP clients: None (UDP-based P2P protocol)
   - Dependencies: rsa, ecdsa, jsonlight, rich, streamlit, pydantic

## 7. Test Strategy
   - Test framework: pytest
   - Required coverage: No specific requirement
   - Mocks/stubs location: Within test files

## 8. Git & Branching
   - Branch naming: Not explicitly defined
   - Commit message style: Freeform
   - Default branch: Not explicitly defined

## 9. CI/CD Integration
   - CI platform: None explicitly configured
   - Test commands: `pytest`
   - Deployment steps: None configured

## 10. Environment Handling
    - Config format: TOML (`config/validators.toml`), Python classes
    - Secrets handling: File-based (e.g., `validator_key`, `mint_key`)
    - Environment separation: Feature flags in code (e.g., `FeatureFlags.DEBUG`)

## 11. Logging & Debugging
    - Logging tools: Custom logging configuration with `get_logger()`
    - Debugging artifacts allowed in PR: Yes (conditional on `FeatureFlags.DEBUG`)
    - Error handling pattern: Try-catch blocks with logging

## 12. Localization
    - i18n strategy: None implemented
    - Key format: Not applicable
    - File structure: Not applicable

## 13. Code Generation / Tools
    - Custom CLI tools / generators in use: None
    - Codegen folders or auto-generated files to avoid editing: None
    - Required hooks or scaffolds when adding modules: None

## 14. Security Practices
    - Input sanitization libraries: Custom validation
    - Token handling pattern: ECDSA and RSA cryptographic signatures
    - Encryption usage: SHA-256 hashing, ECDSA and RSA signatures