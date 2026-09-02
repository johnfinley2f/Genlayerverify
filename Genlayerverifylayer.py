# { "Depends": "py-genlayer:1jb45aa8ynh2a9c9xn3b7qqh8sm5q93hwfp7jqmwsfhh8jpz09h6" }
# Deployed: 0x0D1A1f2889897cFCb440A194fedaeC131101E0E8
# Network:  Asimov Mainnet
# Chain ID: 0x1A4

from genlayer import *

class GenlayerVerifyLayer(gl.Contract):
    latest_address: str
    latest_network: str
    latest_status: str
    latest_response_code: u32
    latest_source_url: str
    latest_found: bool
    total_checks: u32

    def __init__(self):
        self.latest_address = ""
        self.latest_network = ""
        self.latest_status = "not_checked"
        self.latest_response_code = 0
        self.latest_source_url = ""
        self.latest_found = False
        self.total_checks = 0

    @gl.public.write
    def verify_from_page(self, contract_address: str, source_url: str, network: str):
        normalized = contract_address.lower()
        def fetch() -> bool:
            page = gl.nondet.web.get(source_url).body.decode("utf-8").lower()
            return normalized in page
        found = gl.eq_principle.strict_eq(fetch)
        self.latest_address = contract_address
        self.latest_network = network
        self.latest_status = "reachable" if found else "not_found"
        self.latest_response_code = 200
        self.latest_source_url = source_url
        self.latest_found = found
        self.total_checks += 1

    @gl.public.view
    def get_status(self) -> str:
        return self.latest_status

    @gl.public.view
    def get_total_checks(self) -> u32:
        return self.total_checks
