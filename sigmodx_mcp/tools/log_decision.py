import json

from mcp import types
from sigmodx import SigmodxClient, AgentBlockedError
from sigmodx.models import InvoiceDecision


def make_client(api_key: str, agent_id: str) -> SigmodxClient:
    return SigmodxClient(api_key=api_key, agent_id=agent_id)


async def log_invoice_decision(
    args: dict, api_key: str, agent_id: str
) -> list[types.TextContent]:
    try:
        client = make_client(api_key, agent_id)
        input_hash = client.hash_inputs(args.get("inputs", {}))
        result = client.submit_invoice_decision(
            InvoiceDecision(
                decision_type=args["decision_type"],
                input_hash=input_hash,
                rationale=args["rationale"],
                invoice_amount=args.get("invoice_amount"),
                vendor_id=args.get("vendor_id"),
                confidence=args.get("confidence"),
            )
        )
        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "decision_event_id": result.decision_event_id,
                        "agent_state": result.agent_state,
                        "requires_human_approval": result.requires_human_approval,
                    }
                ),
            )
        ]
    except AgentBlockedError as e:
        return [
            types.TextContent(
                type="text",
                text=json.dumps({"error": "agent_blocked", "reason": str(e)}),
            )
        ]
    except Exception as e:
        return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def log_gl_decision(
    args: dict, api_key: str, agent_id: str
) -> list[types.TextContent]:
    try:
        client = make_client(api_key, agent_id)
        input_hash = client.hash_inputs(args.get("inputs", {}))
        result = client.submit_gl_decision(
            decision_type=args["decision_type"],
            input_hash=input_hash,
            rationale=args["rationale"],
            flag_subtype=args.get("flag_subtype"),
            flag_severity=args.get("flag_severity"),
            entry_amount=args.get("entry_amount"),
            gl_account_code=args.get("gl_account_code"),
            sod_violation_detected=args.get("sod_violation_detected", False),
        )
        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "decision_event_id": result.decision_event_id,
                        "agent_state": result.agent_state,
                        "sod_auto_blocked": result.sod_auto_blocked,
                    }
                ),
            )
        ]
    except AgentBlockedError as e:
        return [
            types.TextContent(
                type="text",
                text=json.dumps({"error": "agent_blocked", "reason": str(e)}),
            )
        ]
    except Exception as e:
        return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]


async def log_anomaly_decision(
    args: dict, api_key: str, agent_id: str
) -> list[types.TextContent]:
    try:
        client = make_client(api_key, agent_id)
        input_hash = client.hash_inputs(args.get("inputs", {}))
        result = client.submit_anomaly_decision(
            decision_type=args["decision_type"],
            input_hash=input_hash,
            rationale=args["rationale"],
            anomaly_subtype=args.get("anomaly_subtype"),
            severity=args.get("severity"),
            anomaly_score=args.get("anomaly_score"),
            transaction_amount=args.get("transaction_amount"),
            entity_reference=args.get("entity_reference"),
            confidence=args.get("confidence"),
        )
        return [
            types.TextContent(
                type="text",
                text=json.dumps(
                    {
                        "decision_event_id": result.decision_event_id,
                        "agent_state": result.agent_state,
                        "requires_immediate_review": result.requires_immediate_review,
                    }
                ),
            )
        ]
    except AgentBlockedError as e:
        return [
            types.TextContent(
                type="text",
                text=json.dumps({"error": "agent_blocked", "reason": str(e)}),
            )
        ]
    except Exception as e:
        return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]
