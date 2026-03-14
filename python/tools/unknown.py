from python.helpers.tool import Tool, Response
from python.extensions.system_prompt._10_system_prompt import (
    get_tools_prompt,
    get_mcp_tools_prompt,
)


class Unknown(Tool):
    async def execute(self, **kwargs):
        tools = get_tools_prompt(self.agent)
        try:
            mcp_tools = get_mcp_tools_prompt(self.agent)
        except Exception:
            mcp_tools = ""
        if mcp_tools:
            tools += "\n\n" + mcp_tools
        return Response(
            message=self.agent.read_prompt(
                "fw.tool_not_found.md", tool_name=self.name, tools_prompt=tools
            ),
            break_loop=False,
        )
