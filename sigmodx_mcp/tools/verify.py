import json

import httpx
from mcp import types

SIGMODX_API = "https://api.sigmodx.com"


async def verify_attestation(args: dict) -> list[types.TextContent]:
    verification_string = args.get("verification_string", "")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{SIGMODX_API}/attestations/verify",
                params={"verification_string": verification_string},
                timeout=10.0,
            )
        if response.status_code == 200:
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps({"verified": True, "data": response.json()}),
                )
            ]
        if response.status_code == 404:
            return [
                types.TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "verified": False,
                            "error": "Verification string not found",
                        }
                    ),
                )
            ]
        return [
            types.TextContent(
                type="text",
                text=json.dumps({"verified": False, "error": response.text}),
            )
        ]
    except Exception as e:
        return [
            types.TextContent(
                type="text",
                text=json.dumps({"verified": False, "error": str(e)}),
            )
        ]
