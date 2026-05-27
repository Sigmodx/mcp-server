import json

from mcp import types
from sigmodx import SigmodxClient


async def get_agent_reliability(
    args: dict, api_key: str, agent_id: str
) -> list[types.TextContent]:
    try:
        client = SigmodxClient(api_key=api_key, agent_id=agent_id)
        scenario = args.get("scenario", "anomaly_detection")

        if scenario == "invoice_approval":
            response = client._client.get(f"/agents/{agent_id}/reliability/invoice")
            response.raise_for_status()
            data = response.json()
        elif scenario == "gl_review":
            data = client.get_gl_reliability()
        elif scenario == "anomaly_detection":
            data = client.get_anomaly_reliability()
        else:
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({"error": f"Unknown scenario: {scenario}"}),
                )
            ]

        return [types.TextContent(type="text", text=json.dumps(data))]
    except Exception as e:
        return [types.TextContent(type="text", text=json.dumps({"error": str(e)}))]
