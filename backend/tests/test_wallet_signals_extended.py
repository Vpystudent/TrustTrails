import pytest
import os
import sys
from unittest.mock import patch
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from backend.wallet_signals import run

@patch('backend.wallet_signals.get_txs')
@patch('backend.wallet_signals.get_token_transfers')
@patch('backend.wallet_signals.get_approval_logs')
@patch('backend.wallet_signals.get_allowance')
@patch('backend.wallet_signals.check_contract')
def test_unlimited_approval(mock_check, mock_allowance, mock_logs, mock_transfers, mock_txs):
    mock_txs.return_value = []
    mock_transfers.return_value = []
    
    # 2**256 - 1 is FFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFF
    max_uint = "0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff"
    mock_logs.return_value = [
        {"topics": ["0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925", "0x00", "0x000000000000000000000000spender1"], "address": "0xtoken1", "data": max_uint, "transactionHash": "0x123", "blockNumber": "0x1"},
        {"topics": ["0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925", "0x00", "0x000000000000000000000000spender2"], "address": "0xtoken2", "data": "0x01", "transactionHash": "0x456", "blockNumber": "0x2"},
        {"topics": ["0x8c5be1e5ebec7d5bd14f71427d1e84f3dd0314c0f7b2291e5b200ac8c7c3b925", "0x00", "0x000000000000000000000000spender3"], "address": "0xtoken3", "data": max_uint, "transactionHash": "0x789", "blockNumber": "0x3"}
    ]
    
    # Spender 1: unlimited but allowance = 0 (revoked)
    # Spender 2: small amount, allowance > 0
    # Spender 3: unlimited, allowance > 0
    def allowance_side_effect(token, owner, spender, chain_id):
        if spender == '0xspender1': return 0
        if spender == '0xspender2': return 1
        if spender == '0xspender3': return 2**255 + 1
        return 0
    mock_allowance.side_effect = allowance_side_effect
    
    mock_check.return_value = []
    
    findings = run('0xowner', 'ethereum')
    
    unlimited = [f for f in findings if f['signal_id'] == 'unlimited_approval']
    assert len(unlimited) == 1
    assert "0x789" in unlimited[0]['evidence'][0]['tx_hash']

