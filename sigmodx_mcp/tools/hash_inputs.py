import hashlib
import json

from mcp import types


async def hash_inputs_tool(arguments: dict) -> list[types.TextContent]:
    payload = arguments.get("payload", {})
    canonical = json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
    )
    digest = hashlib.sha256(canonical.encode("utf-8")).hexdigest()
    result = f"sha256:{digest}"
    return [
        types.TextContent(
            type="text",
            text=json.dumps({"input_hash": result, "algo": "sha256"}),
        )
    ]
