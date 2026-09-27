# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }

from genlayer import *
import json

STUDIONET_RPC = "https://studio.genlayer.com/api"
EXPLORER_API  = "https://explorer.genlayer.com/api/v1/contracts"

class VerificationRecord(gl.Record):
    address:            str
    has_bytecode:       bool
    bytecode_size:      u32
    explorer_confirmed: bool
    is_active:          bool
    contract_type:      str
    trust_score:        u32
    ai_verdict:         str
    checked_at:         u32

class GenlayerVerifyLayer(gl.Contract):
    records:        TreeMap[str, VerificationRecord]
    total_verified: u32
    last_address:   str

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
        raw = gl.get_webpage(STUDIONET_RPC, method="POST", payload=body)
        try:
            return json.loads(raw).get("result", "")
        except Exception:
            return ""

    @gl.public.write
    def verify_contract(self, address: str) -> None:
        if not address.startswith("0x") or len(address) != 42:
            raise Exception("Invalid address — must be 0x + 40 hex chars.")

        addr_lower = address.lower()

        def fetch_bytecode() -> str:
            return self._rpc("eth_getCode", [address, "latest"])

        bytecode      = gl.eq_principle_strict_eq(fetch_bytecode)
        has_bytecode  = len(bytecode) > 4
        bytecode_size = u32((len(bytecode) - 2) // 2) if has_bytecode else u32(0)

        def fetch_explorer() -> str:
            url = f"{EXPLORER_API}/{address}"
            return gl.get_webpage(url)

        explorer_raw       = gl.eq_principle_strict_eq(fetch_explorer)
        explorer_confirmed = (
            addr_lower in explorer_raw.lower()
            and "error" not in explorer_raw.lower()
        )

        def fetch_nonce() -> str:
            return self._rpc("eth_getTransactionCount", [address, "latest"])

        nonce_hex = gl.eq_principle_strict_eq(fetch_nonce)
        try:
            is_active = int(nonce_hex, 16) > 0
        except Exception:
            is_active = False

        evidence = (
            f"Address: {address}\n"
            f"Network: GenLayer Studionet (chain 61999)\n"
            f"Source 1 — eth_getCode: "
            f"{'bytecode present, ' + str(int(bytecode_size)) + ' bytes' if has_bytecode else 'empty — no contract'}\n"
            f"Source 2 — Explorer registry: "
            f"{'confirmed' if explorer_confirmed else 'not found'}\n"
            f"Source 3 — Transaction count: "
            f"{'active (nonce > 0)' if is_active else 'no outgoing transactions'}\n"
        )

        def ai_analysis() -> str:
            return gl.exec_prompt(
                "You are an expert blockchain contract analyst.\n"
                "Based ONLY on the evidence below, return a JSON object with "
                "exactly these keys:\n"
                "  contract_type: one of [ERC-20, ERC-721, ERC-1155, Custom, EOA, Unknown]\n"
                "  trust_score: integer 0-100 based on how many sources confirm deployment\n"
                "  verdict: one factual sentence max 25 words\n"
                "Scoring guide:\n"
                "  bytecode + explorer + active  = 85-100\n"
                "  bytecode + explorer           = 65-84\n"
                "  bytecode only                 = 35-64\n"
                "  nothing confirmed             = 0-34\n"
                "Return ONLY the JSON, no extra text.\n\n"
                f"Evidence:\n{evidence}"
            )

        ai_raw = gl.eq_principle_prompt_comparative(ai_analysis)

        try:
            clean   = ai_raw.strip().strip("```json").strip("```").strip()
            ai_data = json.loads(clean)
            c_type  = str(ai_data.get("contract_type", "Unknown"))
            t_score = u32(min(100, max(0, int(ai_data.get("trust_score", 0)))))
            verdict = str(ai_data.get("verdict", ai_raw[:120]))
        except Exception:
            c_type  = "Unknown"
            t_score = u32(0)
            verdict = ai_raw[:120]

        self.records[addr_lower] = VerificationRecord(
            address            = address,
            has_bytecode       = has_bytecode,
            bytecode_size      = bytecode_size,
            explorer_confirmed = explorer_confirmed,
            is_active          = is_active,
            contract_type      = c_type,
            trust_score        = t_score,
            ai_verdict         = verdict,
            checked_at         = u32(gl.message.timestamp),
        )

        self.last_address    = address
        self.total_verified += 1

    @gl.public.view
    def get_record(self, address: str) -> str:
        rec = self.records.get(address.lower())
        if rec is None:
            return "Not verified yet."
        return (
            f"Address:   {rec.address}\n"
            f"Type:      {rec.contract_type}\n"
            f"Bytecode:  {'YES (' + str(int(rec.bytecode_size)) + ' bytes)' if rec.has_bytecode else 'NO'}\n"
            f"Explorer:  {'Confirmed' if rec.explorer_confirmed else 'Not found'}\n"
            f"Active:    {'Yes' if rec.is_active else 'No'}\n"
            f"Trust:     {int(rec.trust_score)}/100\n"
            f"Verdict:   {rec.ai_verdict}\n"
            f"Checked:   {int(rec.checked_at)}"
        )

    @gl.public.view
    def get_trust_score(self, address: str) -> u32:
        rec = self.records.get(address.lower())
        return rec.trust_score if rec else u32(0)

    @gl.public.view
    def get_verdict(self, address: str) -> str:
        rec = self.records.get(address.lower())
        return rec.ai_verdict if rec else "Not verified yet."

    @gl.public.view
    def get_contract_type(self, address: str) -> str:
        rec = self.records.get(address.lower())
        return rec.contract_type if rec else "Unknown"

    @gl.public.view
    def is_trusted(self, address: str) -> bool:
        rec = self.records.get(address.lower())
        return bool(rec and rec.trust_score >= 70)

    @gl.public.view
    def get_total_verified(self) -> u32:
        return self.total_verified

    @gl.public.view
    def get_last_address(self) -> str:
        return self.last_address
