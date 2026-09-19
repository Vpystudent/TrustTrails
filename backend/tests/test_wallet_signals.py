import pytest
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.wallet_signals import get_latest_approvals

def test_get_latest_approvals():
    logs = [
        {"topics": ["0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925", "0x000", "0x000000000000000000000000spender1"], "address": "0xtoken1", "data": "0x1"},
        {"topics": ["0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925", "0x000", "0x000000000000000000000000spender1"], "address": "0xtoken1", "data": "0x2"},
        {"topics": ["0x17307eab39ab6107e8899845ad3d59bd9653f200f220920489ca2b5937696c31", "0x000", "0x000000000000000000000000spender2"], "address": "0xtoken2", "data": "0x1"}
    ]
    logs_desc = list(reversed(logs))
    latest_approvals, latest_nfts = get_latest_approvals(logs_desc)
    
    assert ("0xtoken1", "0xspender1") in latest_approvals
    assert latest_approvals[("0xtoken1", "0xspender1")]["data"] == "0x2"
    assert ("0xtoken2", "0xspender2") in latest_nfts

