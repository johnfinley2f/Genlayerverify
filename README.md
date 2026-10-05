# GenlayerVerifyLayer

An Intelligent Contract that performs 3-source, deterministic trust scoring of EVM addresses on GenLayer Studionet.

Trust decision is fully deterministic - AI is used only for classification and informational scoring.

## Deployed Contract

| Field            | Value |
|------------------|-------|
| Contract Address | `0xc1f0126f83660caE3837f0E6D0fe1C5ceaCde708` |
| Network          | GenLayer Studionet |
| Chain ID         | 61999 |
| Status           | FINALIZED ✅ |

[View Contract on Explorer](https://explorer-studio.genlayer.com/address/0xc1f0126f83660caE3837f0E6D0fe1C5ceaCde708)

[View Deploy Transaction](https://explorer-studio.genlayer.com/tx/0x1b8ccd34a9d51f4f1067f4a918e947af35c7c84d2ce1dfa6a27d3f31cd36d4b6)

## What is this?

GenlayerVerifyLayer is a GenLayer Intelligent Contract that verifies any EVM address through 3 independent on-chain sources.

The trust decision is fully deterministic - it is based only on bytecode presence and explorer confirmation, both fetched via strict equality consensus.

AI is used only to classify the contract type and provide an informational score - it has no effect on the trust result.

## How it works

1. `verify_contract(address)` call karo
2. Source 1 - `eth_getCode` via live RPC — bytecode present?
3. Source 2 - GenLayer Studio Explorer page — address confirmed?
4. Source 3 - `eth_getTransactionCount` via live RPC — address active?
5. Trust decision - `has_bytecode AND explorer_confirmed` — fully deterministic
6. AI analysis - contract type + informational score (10, 40, 70, or 90 only)
7. Result stored permanently in TreeMap after 5-validator consensus

## Trust Decision Logic

is_trusted = has_bytecode AND explorer_confirmed

This is deterministic - no AI, no range, no threshold ambiguity. Every validator will reach the same result for the same address state.

## AI Score Guide (informational only)

| Score | Condition |
|-------|-----------|
| 90 | Bytecode + Explorer + Active |
| 70 | Bytecode + Explorer |
| 40 | Bytecode only |
| 10 | Nothing confirmed |

AI score is clamped to exactly one of these 4 values — it cannot cross any threshold unpredictably.

## Why consensus is guaranteed

- All 3 sources use `gl.eq_principle_strict_eq` — validators must return identical raw data
- Trust decision is pure boolean logic on deterministic data — no AI involvement
- AI score is forced to 4 fixed values only — no ambiguous ranges
- If any validator gets different data, consensus fails and nothing is stored

## Methods

### Write

| Method | Params | Description |
|--------|--------|-------------|
| `verify_contract` | `address: str` | Full 3-source verification, stores result after consensus |

### Read (no gas)

| Method | Params | Returns | Description |
|--------|--------|---------|-------------|
| `get_record` | `address: str` | `str` | Full record — all fields |
| `get_trust_score` | `address: str` | `u32` | Informational score: 10, 40, 70, or 90 |
| `get_verdict` | `address: str` | `str` | AI verdict sentence |
| `get_contract_type` | `address: str` | `str` | ERC-20 / ERC-721 / Custom / EOA |
| `is_trusted` | `address: str` | `bool` | True if bytecode AND explorer confirmed |
| `get_total_verified` | — | `u32` | Total verifications completed |
| `get_last_address` | — | `str` | Last verified address |

## Storage Design

Each address maps to a JSON string in TreeMap:

{
"address":            "0x...",
"has_bytecode":       true/false,
"bytecode_size":      1234,
"explorer_confirmed": true/false,
"is_active":          true/false,
"is_trusted":         true/false,
"contract_type":      "Custom",
"trust_score":        90,
"ai_verdict":         "This address holds a verified GenLayer Intelligent Contract.",
"checked_at":         1727123456
}

All records are permanent and publicly queryable.

## Test it in Studio

1. Open [studio.genlayer.com](https://studio.genlayer.com)
2. Connect to GenLayer Studio (chain 61999)
3. Open contract [0xc1f0126f83660caE3837f0E6D0fe1C5ceaCde708](https://explorer-studio.genlayer.com/address/0xc1f0126f83660caE3837f0E6D0fe1C5ceaCde708)
4. Call `verify_contract("0xc1f0126f83660caE3837f0E6D0fe1C5ceaCde708")`
5. Wait for consensus
6. Call `get_record("0xc1f0126f83660caE3837f0E6D0fe1C5ceaCde708")` to read result

## LICENCE

MIT