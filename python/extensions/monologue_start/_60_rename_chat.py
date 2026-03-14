from python.helpers import persist_chat, tokens
from python.helpers.extension import Extension
from agent import LoopData
import asyncio


class RenameChat(Extension):
    async def execute(self, loop_data: LoopData = LoopData(), **kwargs):
        asyncio.create_task(self._change_name_with_timeout())

    async def _change_name_with_timeout(self):
        """Wrap change_name with a timeout so a stalled utility model doesn't hang."""
        try:
            await asyncio.wait_for(self.change_name(), timeout=30)
        except asyncio.TimeoutError:
            pass  # non-critical, just abandon

    async def change_name(self):
        try:
            # prepare history
            history_text = self.agent.history.output_text()
            ctx_length = min(
                int(self.agent.config.utility_model.ctx_length * 0.7), 5000
            )
            history_text = tokens.trim_to_tokens(history_text, ctx_length, "start")
            # prepare system and user prompt
            system = self.agent.read_prompt("fw.rename_chat.sys.md")
            current_name = self.agent.context.name
            message = self.agent.read_prompt(
                "fw.rename_chat.msg.md", current_name=current_name, history=history_text
            )
            # call utility model
            new_name = await self.agent.call_utility_model(
                system=system, message=message, background=True
            )
            # update name
            if new_name:
                # trim name to max length if needed
                if len(new_name) > 40:
                    new_name = new_name[:40] + "..."
                # apply to context and save
                self.agent.context.name = new_name
                persist_chat.save_tmp_chat(self.agent.context)
        except Exception:
            pass  # non-critical
