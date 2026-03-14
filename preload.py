import asyncio
import sys
from python.helpers import runtime, whisper, settings
from python.helpers.print_style import PrintStyle
from python.helpers import kokoro_tts
import models


def resolve_preload_settings(*, defaults_only: bool = False) -> settings.Settings:
    """Resolve preload settings for build-time or runtime use."""
    if defaults_only:
        return settings.get_default_settings()
    return settings.get_settings()


async def preload(*, defaults_only: bool = False):
    try:
        set = resolve_preload_settings(defaults_only=defaults_only)

        # preload whisper model
        async def preload_whisper():
            try:
                return await whisper.preload(set["stt_model_size"])
            except Exception as e:
                PrintStyle().error(f"Error in preload_whisper: {e}")

        # preload embedding model
        async def preload_embedding():
            if set["embed_model_provider"].lower() == "huggingface":
                try:
                    # Use the new LiteLLM-based model system
                    emb_mod = models.get_embedding_model(
                        "huggingface", set["embed_model_name"]
                    )
                    emb_txt = await emb_mod.aembed_query("test")
                    return emb_txt
                except Exception as e:
                    PrintStyle().error(f"Error in preload_embedding: {e}")

        # preload kokoro tts model if enabled
        async def preload_kokoro():
            if set["tts_kokoro"]:
                try:
                    return await kokoro_tts.preload()
                except Exception as e:
                    PrintStyle().error(f"Error in preload_kokoro: {e}")

        # async tasks to preload
        tasks = [
            preload_embedding(),
            # preload_whisper(),
            # preload_kokoro()
        ]

        await asyncio.gather(*tasks, return_exceptions=True)
        PrintStyle().print("Preload completed.")
    except Exception as e:
        PrintStyle().error(f"Error in preload: {e}")


# preload transcription model
if __name__ == "__main__":
    defaults_only = "--defaults-only" in sys.argv
    mode = "defaults-only" if defaults_only else "runtime-settings"
    PrintStyle().print(f"Running preload ({mode})...")
    runtime.initialize()
    asyncio.run(preload(defaults_only=defaults_only))
