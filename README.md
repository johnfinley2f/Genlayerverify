# GenlayerVerifyLayer

An Intelligent Contract that performs **network-aware, AI-powered verification**
of EVM addresses on GenLayer Studionet.

## Deployed Contract

| Field            | Value                                        |
|------------------|----------------------------------------------|
| Contract Address | `0x84509cA0D2a676461a4966d0392f50e73c45C6a8` |
| Network          | GenLayer Studionet                           |
| Chain ID         | 61999                                        |
| Deploy Tx        | `0xe6fd413aeef9c478e19f91673938405bdbd28d9d0bdd7913c8b106fd6542efaf` |
| Status           | ACCEPTED ✅                                  |

## How it works

1. Caller calls `verify_contract("0xAddress")`
2. Contract calls **live Studionet RPC** (`eth_getCode`) via `gl.get_webpage()`
   — fetches real bytecode, not caller-supplied data
3. AI validator writes a factual verdict from the bytecode evidence
   via `gl.exec_prompt()`
4. Result stored on-chain after **5-validator consensus**

Every validator runs the RPC call independently.
Fake results are impossible — consensus fails if validators disagree.

## Public Methods

### Write
| Method | Params | Description |
|--------|--------|-------------|
| `verify_contract` | `address: str` | Runs full verification, stores result |

### Read (free, no gas)
| Method | Returns | Description |
|--------|---------|-------------|
| `get_last_result` | `str` | Address + status + AI verdict |
| `get_verdict` | `str` | AI verdict only |
| `is_deployed` | `bool` | True if bytecode found at address |
| `get_total_checks` | `u32` | Total verifications completed |

## Test it in Studio

1. Open [studio.genlayer.com](https://studio.genlayer.com)
2. Connect to **GenLayer Studio** (chain 61999)
3. Go to contract: `0x84509cA0D2a676461a4966d0392f50e73c45C6a8`
4. Call `verify_contract("0x84509cA0D2a676461a4966d0392f50e73c45C6a8")`
   (verifies itself!)
5. Call `get_last_result()` to read the on-chain verdict

## Why this qualifies as an Intelligent Contract

- `gl.get_webpage()` makes a **live network call** — data comes from
  the blockchain, not from the caller
- `gl.exec_prompt()` produces an **AI-written verdict** from real evidence
- **5 validators** verify independently — consensus required to write storage
- Caller cannot manipulate the result by passing fake data

## Repository

This repo contains only the Intelligent Contract.
Submitted under **Intelligent Contracts** category.
