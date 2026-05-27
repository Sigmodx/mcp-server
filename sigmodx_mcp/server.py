"""
Sigmodx MCP Server

Exposes Sigmodx audit infrastructure as MCP tools.
Any MCP-compatible agent framework can call these tools directly
to log decisions, verify attestations, and check agent reliability.

Usage:
    sigmodx-mcp

    SIGMODX_API_KEY=your-key \\
    SIGMODX_AGENT_ID=your-agent-uuid \\
    sigmodx-mcp
"""

import asyncio
import logging
import os

from mcp import types
from mcp.server import Server
from mcp.server.stdio import stdio_server

from sigmodx_mcp.tools.hash_inputs import hash_inputs_tool
from sigmodx_mcp.tools.log_decision import (
    log_anomaly_decision,
    log_gl_decision,
    log_invoice_decision,
)
from sigmodx_mcp.tools.reliability import get_agent_reliability
from sigmodx_mcp.tools.verify import verify_attestation

logger = logging.getLogger(__name__)

server = Server("sigmodx")


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name="sigmodx_log_invoice_decision",
            description=(
                "Log an invoice approval decision to Sigmodx for "
                "cryptographic attestation. Use when an AI agent "
                "approves, rejects, or escalates an invoice. "
                "The input payload is hashed client-side — "
                "invoice data never leaves your environment."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "decision_type": {
                        "type": "string",
                        "enum": ["approve", "reject", "escalate"],
                        "description": "The agent's decision",
                    },
                    "inputs": {
                        "type": "object",
                        "description": "What the agent consumed (will be hashed)",
                    },
                    "rationale": {
                        "type": "string",
                        "description": "Why the agent made this decision (min 10 chars)",
                    },
                    "invoice_amount": {"type": "number", "description": "Invoice amount"},
                    "vendor_id": {
                        "type": "string",
                        "description": "Vendor reference (internal ID, not name)",
                    },
                    "confidence": {
                        "type": "number",
                        "description": "Confidence score 0.0-1.0",
                    },
                },
                "required": ["decision_type", "inputs", "rationale"],
            },
        ),
        types.Tool(
            name="sigmodx_log_gl_decision",
            description=(
                "Log a GL entry review decision to Sigmodx. Use when "
                "an AI agent approves, flags, or blocks a journal entry. "
                "Segregation of duties violations are auto-blocked."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "decision_type": {
                        "type": "string",
                        "enum": ["approve", "flag", "block"],
                    },
                    "inputs": {"type": "object"},
                    "rationale": {"type": "string"},
                    "flag_subtype": {
                        "type": "string",
                        "enum": [
                            "duplicate_risk",
                            "round_number",
                            "unusual_poster",
                            "outside_hours",
                            "threshold_skirting",
                            "segregation_of_duties",
                            "backdated",
                            "suspense_account",
                            "missing_documentation",
                            "other",
                        ],
                    },
                    "flag_severity": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                    },
                    "entry_amount": {"type": "number"},
                    "gl_account_code": {"type": "string"},
                    "sod_violation_detected": {"type": "boolean"},
                },
                "required": ["decision_type", "inputs", "rationale"],
            },
        ),
        types.Tool(
            name="sigmodx_log_anomaly_decision",
            description=(
                "Log an anomaly detection decision to Sigmodx. Use when "
                "an AI agent flags, clears, or escalates a financial "
                "transaction anomaly. Critical severity items are "
                "automatically escalated for immediate review."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "decision_type": {
                        "type": "string",
                        "enum": ["flag", "clear", "escalate"],
                    },
                    "inputs": {"type": "object"},
                    "rationale": {"type": "string"},
                    "anomaly_subtype": {
                        "type": "string",
                        "enum": [
                            "duplicate_payment",
                            "vendor_not_approved",
                            "unusual_amount",
                            "unusual_timing",
                            "round_number",
                            "new_vendor_immediate_payment",
                            "revenue_reversal",
                            "intercompany_mismatch",
                            "expense_policy_violation",
                            "velocity_anomaly",
                            "split_transaction",
                            "dormant_account_activity",
                            "contra_entry",
                            "other",
                        ],
                    },
                    "severity": {
                        "type": "string",
                        "enum": ["low", "medium", "high", "critical"],
                    },
                    "anomaly_score": {"type": "number"},
                    "transaction_amount": {"type": "number"},
                    "entity_reference": {"type": "string"},
                    "confidence": {"type": "number"},
                },
                "required": ["decision_type", "inputs", "rationale"],
            },
        ),
        types.Tool(
            name="sigmodx_verify_attestation",
            description=(
                "Verify a Sigmodx attestation using a verification string. "
                "Returns the attestation record and confirms the cryptographic "
                "hash is intact. No authentication required."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "verification_string": {
                        "type": "string",
                        "description": (
                            "Verification string e.g. SIGMODX-INVOICE-6DFC-D331..."
                        ),
                    }
                },
                "required": ["verification_string"],
            },
        ),
        types.Tool(
            name="sigmodx_get_reliability",
            description=(
                "Get the current reliability state (ALLOW/LIMIT/BLOCK) "
                "for an agent in a specific scenario."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "scenario": {
                        "type": "string",
                        "enum": ["invoice_approval", "gl_review", "anomaly_detection"],
                    }
                },
                "required": ["scenario"],
            },
        ),
        types.Tool(
            name="sigmodx_hash_inputs",
            description=(
                "Hash an input payload using Sigmodx's deterministic "
                "SHA-256 method. The payload itself is never sent to Sigmodx."
            ),
            inputSchema={
                "type": "object",
                "properties": {
                    "payload": {
                        "type": "object",
                        "description": "The input data to hash",
                    }
                },
                "required": ["payload"],
            },
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    api_key = os.environ.get("SIGMODX_API_KEY")
    agent_id = os.environ.get("SIGMODX_AGENT_ID")

    if name == "sigmodx_hash_inputs":
        return await hash_inputs_tool(arguments)

    if name == "sigmodx_verify_attestation":
        return await verify_attestation(arguments)

    if not api_key or not agent_id:
        return [
            types.TextContent(
                type="text",
                text=(
                    "Error: SIGMODX_API_KEY and SIGMODX_AGENT_ID "
                    "environment variables are required."
                ),
            )
        ]

    if name == "sigmodx_log_invoice_decision":
        return await log_invoice_decision(arguments, api_key, agent_id)
    if name == "sigmodx_log_gl_decision":
        return await log_gl_decision(arguments, api_key, agent_id)
    if name == "sigmodx_log_anomaly_decision":
        return await log_anomaly_decision(arguments, api_key, agent_id)
    if name == "sigmodx_get_reliability":
        return await get_agent_reliability(arguments, api_key, agent_id)

    return [types.TextContent(type="text", text=f"Unknown tool: {name}")]


async def main():
    async with stdio_server() as (read, write):
        await server.run(read, write, server.create_initialization_options())


def run():
    asyncio.run(main())
