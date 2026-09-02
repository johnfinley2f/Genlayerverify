# GenlayerVerifyLayer

A wallet-aware GenLayer contract preflight desk for builders. Validate an EVM contract address against a public page and reach strict consensus via GenLayer validators.

## Live Demo

🌐 **[View Live](https://johnfinley2f.github.io/genlayer-contract-verify)**

## Deployed Contract

| Field | Value |
|-------|-------|
| Address | `0x0D1A1f2889897cFCb440A194fedaeC131101E0E8` |
| Network | Asimov Mainnet |
| Chain ID | `0x1A4` |
| Validator Set | Bradbury Testnet |

## Features

- Injected EVM dummy wallet connect and disconnect flow
- Account and chain ID detection
- Bradbury Testnet, Asimov Mainnet, and Local Studio selector
- EVM address validation and optional read-only eth_getCode check
- Demo-only Prepare → Simulate → Consensus → Complete lifecycle
- GenLayer Intelligent Contract for GenLayer Studio
- Submission PDF and portal checklist
- 1 GEN transaction simulation with full consensus flow
- Transaction history tracking

## Run Locally

```bash
# Just open index.html in browser — no build needed!
open index.html
```

## Repository Map

```
index.html                  Main frontend app
contracts/
  GenlayerVerifyLayer.py    GenLayer Studio contract
src/
  config.ts                 Contract address config
docs/
  SUBMISSION.md             Reviewer-facing submission packet
```

## GenLayer Studio

Open [studio.genlayer.com](https://studio.genlayer.com), paste contract address:

```
0x0D1A1f2889897cFCb440A194fedaeC131101E0E8
```

## Safety

The browser demo never calls `eth_sendTransaction`, requests a signature, or moves funds.

## Submission

See [docs/SUBMISSION.md](docs/SUBMISSION.md) for the final GitHub and GenLayer Builder submission checklist.
