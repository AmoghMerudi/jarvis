import psutil

from agent.tools import register_tool


async def _battery_status() -> str:
    battery = psutil.sensors_battery()
    if battery is None:
        return "No battery detected (desktop machine)."
    plugged = "plugged in" if battery.power_plugged else "on battery"
    return f"{battery.percent:.0f}% — {plugged}"


async def _ram_usage() -> str:
    mem = psutil.virtual_memory()
    used_gb = mem.used / 1e9
    total_gb = mem.total / 1e9
    return f"{used_gb:.1f} GB used of {total_gb:.1f} GB ({mem.percent}%)"


register_tool(
    name="battery_status",
    description="Return the current battery percentage and charging state.",
    input_schema={"type": "object", "properties": {}, "required": []},
    handler=_battery_status,
)

register_tool(
    name="ram_usage",
    description="Return current RAM usage.",
    input_schema={"type": "object", "properties": {}, "required": []},
    handler=_ram_usage,
)
