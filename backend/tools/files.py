import os
import aiofiles

from agent.tools import register_tool


async def _read_file(path: str) -> str:
    if not os.path.exists(path):
        return f"Error: file not found at {path}"
    async with aiofiles.open(path, mode="r", encoding="utf-8", errors="replace") as f:
        return await f.read()


async def _list_directory(path: str) -> str:
    if not os.path.isdir(path):
        return f"Error: not a directory: {path}"
    entries = os.listdir(path)
    return "\n".join(sorted(entries)) or "(empty)"


async def _delete_file(path: str, confirmed: bool = False) -> str:
    if not confirmed:
        return f"Confirmation required. Call again with confirmed=true to delete: {path}"
    if not os.path.exists(path):
        return f"Error: file not found at {path}"
    os.remove(path)
    return f"Deleted: {path}"


register_tool(
    name="read_file",
    description="Read the contents of a file at the given path.",
    input_schema={
        "type": "object",
        "properties": {"path": {"type": "string", "description": "Absolute file path"}},
        "required": ["path"],
    },
    handler=_read_file,
)

register_tool(
    name="list_directory",
    description="List files and directories at the given path.",
    input_schema={
        "type": "object",
        "properties": {"path": {"type": "string", "description": "Absolute directory path"}},
        "required": ["path"],
    },
    handler=_list_directory,
)

register_tool(
    name="delete_file",
    description="Delete a file. Requires confirmed=true to actually delete.",
    input_schema={
        "type": "object",
        "properties": {
            "path": {"type": "string"},
            "confirmed": {"type": "boolean", "default": False},
        },
        "required": ["path"],
    },
    handler=_delete_file,
)
