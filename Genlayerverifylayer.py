# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json

STUDIONET_RPC = "https://studio.genlayer.com/api"
EXPLORER_API  = "https://explorer-studio.genlayer.com"

class GenlayerVerifyLayer(gl.Contract):
    total_verified: u32
    last_address:   str
    records: TreeMap[str, str]

    def __init__(self):
        self.total_verified = 0
        self.last_address   = ""

    def _rpc(self, method: str, params: list) -> str:
        body = json.dumps({
            "jsonrpc": "2.0",
            "method":  method,
            "params":  params,
            "id":      1,
        })
        try:
            raw = gl.get_webpage(STUDIONET_RPC, method="POST", payload=body)
            return json.loads(raw).get("result", "")
        except Exception:
            return ""

    @gl.public.write
    def verify_contract(self, address: str) -> None:
        if not address.startswith("0x") or len(address) != 42:
            raise Exception("Invalid address — must be 0x + 40 hex chars.")

        addr_lower = address.lower()

        # Source 1: eth_getCode — deterministic
        def fetch_bytecode() -> str:
            return self._rpc("eth_getCode", [address, "latest"])

        bytecode      = gl.eq_principle_strict_eq(fetch_bytecode)
        has_bytecode  = len(bytecode) > 4
        bytecode_size = (len(bytecode) - 2) // 2 if has_bytecode else 0

        # Source 2: Explorer — deterministic
        def fetch_explorer() -> str:
            url = f"{EXPLORER_API}/address/{address}"
            return gl.get_webpage(url)

        explorer_raw       = gl.eq_principle_strict_eq(fetch_explorer)
        explorer_confirmed = addr_lower in explorer_raw.lower()

        # Source 3: eth_getTransactionCount — deterministic
        def fetch_nonce() -> str:
            return self._rpc("eth_getTransactionCount", [address, "latest"])

        nonce_hex = gl.eq_principle_strict_eq(fetch_nonce)
        try:
            is_active = int(nonce_hex, 16) > 0
        except Exception:
            is_active = False

        # Trust decision — fully deterministic, no AI involvement
        # bytecode AND explorer both confirmed = trusted
        is_trusted = has_bytecode and explorer_confirmed

        # AI verdict — informational only, does NOT affect trust decision
        evidence = (
            f"Address: {address}\n"
            f"Network: GenLayer Studionet (chain 61999)\n"
            f"Source 1 — eth_getCode: "
            f"{'bytecode present, ' + str(bytecode_size) + ' bytes' if has_bytecode else 'empty — no contract'}\n"
            f"Source 2 — Explorer: "
            f"{'address confirmed on explorer' if explorer_confirmed else 'not found on explorer'}\n"
            f"Source 3 — Transaction count: "
            f"{'active (nonce > 0)' if is_active else 'no outgoing transactions'}\n"
            f"Deterministic trust decision: {'TRUSTED' if is_trusted else 'NOT TRUSTED'}\n"
        )

        def ai_analysis() -> str:
            return gl.exec_prompt(
                "You are a blockchain contract analyst.\n"
                "Based ONLY on the evidence below, return a JSON object with "
                "exactly these three keys:\n"
                "  contract_type: one of [ERC-20, ERC-721, ERC-1155, Custom, EOA, Unknown]\n"
                "  trust_score: integer, MUST be exactly one of [10, 40, 70, 90] — "
                "pick based on: nothing confirmed=10, bytecode only=40, "
                "bytecode+explorer=70, bytecode+explorer+active=90\n"
                "  verdict: one factual sentence, max 25 words\n"
                "Return ONLY valid JSON, no extra text.\n\n"
                f"Evidence:\n{evidence}"
            )

        ai_raw = gl.eq_principle_prompt_comparative(ai_analysis)

        try:
            clean   = ai_raw.strip().strip("```json").strip("```").strip()
            ai_data = json.loads(clean)
            c_type  = str(ai_data.get("contract_type", "Unknown"))
            t_score = int(ai_data.get("trust_score", 10))
            # Clamp to allowed values only
            allowed = [10, 40, 70, 90]
            t_score = min(allowed, key=lambda x: abs(x - t_score))
            verdict = str(ai_data.get("verdict", ai_raw[:120]))
        except Exception:
            c_type  = "Unknown"
            t_score = 10
            verdict = ai_raw[:120]

        record = json.dumps({
            "address":            address,
            "has_bytecode":       has_bytecode,
            "bytecode_size":      bytecode_size,
            "explorer_confirmed": explorer_confirmed,
            "is_active":          is_active,
            "is_trusted":         is_trusted,
            "contract_type":      c_type,
            "trust_score":        t_score,
            "ai_verdict":         verdict,
            "checked_at":         gl.message.timestamp,
        })

        self.records[addr_lower] = record
        self.last_address        = address
        self.total_verified     += 1

    @gl.public.view
    def get_record(self, address: str) -> str:
        raw = self.records.get(address.lower())
        if raw is None:
            return "Not verified yet."
        try:
            r = json.loads(raw)
            return (
                f"Address:   {r['address']}\n"
                f"Trusted:   {'YES' if r['is_trusted'] else 'NO'}\n"
                f"Type:      {r['contract_type']}\n"
                f"Bytecode:  {'YES (' + str(r['bytecode_size']) + ' bytes)' if r['has_bytecode'] else 'NO'}\n"
                f"Explorer:  {'Confirmed' if r['explorer_confirmed'] else 'Not found'}\n"
                f"Active:    {'Yes' if r['is_active'] else 'No'}\n"
                f"Score:     {r['trust_score']}/100 (informational)\n"
                f"Verdict:   {r['ai_verdict']}\n"
                f"Checked:   {r['checked_at']}"
            )
        except Exception:
            return raw

    @gl.public.view
    def get_trust_score(self, address: str) -> u32:
        raw = self.records.get(address.lower())
        if raw is None:
            return u32(0)
        try:
            return u32(json.loads(raw).get("trust_score", 0))
        except Exception:
            return u32(0)

    @gl.public.view
    def get_verdict(self, address: str) -> str:
        raw = self.records.get(address.lower())
        if raw is None:
            return "Not verified yet."
        try:
            return str(json.loads(raw).get("ai_verdict", ""))
        except Exception:
            return ""

    @gl.public.view
    def get_contract_type(self, address: str) -> str:
        raw = self.records.get(address.lower())
        if raw is None:
            return "Unknown"
        try:
            return str(json.loads(raw).get("contract_type", "Unknown"))
        except Exception:
            return "Unknown"

    @gl.public.view
    def is_trusted(self, address: str) -> bool:
        raw = self.records.get(address.lower())
        if raw is None:
            return False
        try:
            return bool(json.loads(raw).get("is_trusted", False))
        except Exception:
            return False

    @gl.public.view
    def get_total_verified(self) -> u32:
        return self.total_verified

    @gl.public.view
    def get_last_address(self) -> str:
        return self.last_address