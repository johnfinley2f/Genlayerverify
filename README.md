# GenlayerVerifyLayer

An Intelligent Contract that performs 3-source, AI-powered trust scoring of EVM addresses on GenLayer Studionet.

## Deployed Contract

| Field            | Value                                                                 |
|------------------|-----------------------------------------------------------------------|
| Contract Address | `0x84509cA0D2a676461a4966d0392f50e73c45C6a8`                         |
| Network          | GenLayer Studionet                                                    |
| Chain ID         | 61999                                                                 |
| Deploy Tx        | `0xe6fd413aeef9c478e19f91673938405bdbd28d9d0bdd7913c8b106fd6542efaf` |
| Status           | ACCEPTED ✅                                                           |

## What is this?

GenlayerVerifyLayer is a GenLayer Intelligent Contract that takes any EVM address and runs it through 3 independent on-chain data sources. Each GenLayer validator fetches the data independently. The result is only written to storage when all validators reach consensus — making it impossible to fake a verification result.

## How it works

verify_contract(address)
│
├── Source 1: eth_getCode via live RPC
│   → Is there real bytecode at this address?
│
├── Source 2: GenLayer Explorer API
│   → Is this address in the verified contracts registry?
│
├── Source 3: eth_getTransactionCount via live RPC
│   → Has this address ever sent a transaction?
│
└── AI Analysis (gl.exec_prompt)
→ contract_type  (ERC-20 / ERC-721 / ERC-1155 / Custom / EOA / Unknown)
→ trust_score    (0–100)
→ verdict        (one factual sentence, max 25 words)
│
└── Stored permanently in TreeMap
after 5-validator consensus

## Trust Score Guide

| Score  | What it means                          |
|--------|----------------------------------------|
| 85–100 | Bytecode + Explorer confirmed + Active |
| 65–84  | Bytecode + Explorer confirmed          |
| 35–64  | Bytecode only                          |
| 0–34   | Nothing confirmed                      |

## Why caller cannot manipulate results

- All 3 source URLs are hardcoded in the contract
- Caller only passes an address — nothing else
- Every validator fetches data independently from live network
- If validators get different results, consensus fails and nothing is stored

## Methods

### Write

| Method            | Params         | Description                                              |
|-------------------|----------------|----------------------------------------------------------|
| `verify_contract` | `address: str` | Runs 3-source verification, stores result after consensus |

### Read (no gas)

| Method               | Params         | Returns | Description                     |
|----------------------|----------------|---------|---------------------------------|
| `get_record`         | `address: str` | `str`   | Full record — all fields        |
| `get_trust_score`    | `address: str` | `u32`   | Trust score 0–100               |
| `get_verdict`        | `address: str` | `str`   | AI verdict sentence             |
| `get_contract_type`  | `address: str` | `str`   | ERC-20 / ERC-721 / Custom / EOA |
| `is_trusted`         | `address: str` | `bool`  | True if trust score >= 70       |
| `get_total_verified` | —              | `u32`   | Total verifications completed   |
| `get_last_address`   | —              | `str`   | Last address that was verified  |

## Storage Design

class VerificationRecord(gl.Record):
address:            str    # verified EVM address
has_bytecode:       bool   # eth_getCode returned non-empty
bytecode_size:      u32    # size in bytes
explorer_confirmed: bool   # found in explorer registry
is_active:          bool   # nonce > 0
contract_type:      str    # AI classification
trust_score:        u32    # 0-100
ai_verdict:         str    # AI one-sentence verdict
checked_at:         u32    # block timestamp
records: TreeMap[str, VerificationRecord]  # permanent history

All records are permanent and publicly queryable — any address verified once can be looked up by anyone forever.

## Test it in Studio

1. Open studio.genlayer.com
2. Connect to GenLayer Studio (chain 61999)
3. Open contract 0x84509cA0D2a676461a4966d0392f50e73c45C6a8
4. Call verify_contract("0x84509cA0D2a676461a4966d0392f50e73c45C6a8")
5. Wait for consensus
6. Call get_record("0x84509cA0D2a676461a4966d0392f50e73c45C6a8") to read the result

## Why this qualifies as an Intelligent Contract

- Uses gl.get_webpage() to make 3 live network calls — no static or caller-supplied data
- Uses gl.exec_prompt() for AI classification and trust scoring from real evidence
- Uses gl.eq_principle_strict_eq and gl.eq_principle_prompt_comparative for proper consensus
- TreeMap storage — permanent history, anyone can query any past address
- 5 validators run independently — result is authoritative, not gameable

## Repository

This repository contains only the Intelligent Contract.
No frontend, no wallet demo, no transaction UI.
Submitted under the Intelligent Contracts category.
