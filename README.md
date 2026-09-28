# GenlayerVerifyLayer

An Intelligent Contract that performs 3-source, AI-powered trust scoring of EVM addresses on GenLayer Studionet.

## Deployed Contract

| Field            | Value |
|------------------|-------|
| Contract Address | `0x2A89B86Fe8B95Ccd72C435F3812d976822B7A9AC` |
| Network          | GenLayer Studionet |
| Chain ID         | 61999 |
| Status           | FINALIZED ✅ |

[View Contract on Explorer](https://explorer-studio.genlayer.com/address/0x2A89B86Fe8B95Ccd72C435F3812d976822B7A9AC)

[View Deploy Transaction](https://explorer-studio.genlayer.com/tx/0x7de7d2b04bcd0f7db91cf80fb8d919cf9e5bd99d9a8187c899bd4df1d08a40f5)

## What is this?

GenlayerVerifyLayer is a GenLayer Intelligent Contract that takes any EVM address and runs it through 3 independent on-chain data sources. Each GenLayer validator fetches the data independently. The result is only written to storage when all validators reach consensus — making it impossible to fake a verification result.

## How it works

1. `verify_contract(address)` call karo
2. Source 1 — `eth_getCode` via live RPC → bytecode present hai ya nahi?
3. Source 2 — GenLayer Studio Explorer page → address explorer pe hai ya nahi?
4. Source 3 — `eth_getTransactionCount` via live RPC → address active hai ya nahi?
5. AI Analysis via `gl.exec_prompt` → contract_type, trust_score (0-100), verdict
6. Result stored permanently in TreeMap after 5-validator consensus

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

| Method            | Params         | Description                                               |
|-------------------|----------------|-----------------------------------------------------------|
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

Each address maps to a JSON string in TreeMap:
{
"address":            "0x...",
"has_bytecode":       true/false,
"bytecode_size":      1234,
"explorer_confirmed": true/false,
"is_active":          true/false,
"contract_type":      "Custom",
"trust_score":        92,
"ai_verdict":         "This address holds a deployed GenLayer contract confirmed on explorer.",
"checked_at":         1727123456
}

All records are permanent and publicly queryable — any address verified once can be looked up by anyone forever.

## Test it in Studio

1. Open [studio.genlayer.com](https://studio.genlayer.com)
2. Connect to GenLayer Studio (chain 61999)
3. Open contract [0x2A89B86Fe8B95Ccd72C435F3812d976822B7A9AC](https://explorer-studio.genlayer.com/address/0x2A89B86Fe8B95Ccd72C435F3812d976822B7A9AC)
4. Call `verify_contract("0x2A89B86Fe8B95Ccd72C435F3812d976822B7A9AC")`
5. Wait for consensus
6. Call `get_record("0x2A89B86Fe8B95Ccd72C435F3812d976822B7A9AC")` to read result

## Why this qualifies as an Intelligent Contract

- Uses `gl.get_webpage()` to make 3 live network calls — no static or caller-supplied data
- Uses `gl.exec_prompt()` for AI classification and trust scoring from real evidence
- Uses `gl.eq_principle_strict_eq` and `gl.eq_principle_prompt_comparative` for proper consensus
- TreeMap permanent history — anyone can query any past address
- 5 validators run independently — result is authoritative, not gameable

## Repository

This repository contains only the Intelligent Contract.
No frontend, no wallet demo, no transaction UI.
Submitted under the Intelligent Contracts category.
