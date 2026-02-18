#!/usr/bin/env python3
import sys
import os

# Set environment variables
os.environ['WEB_UI_HOST'] = '0.0.0.0'
os.environ['WEB_UI_PORT'] = '8000'

try:
    from python.helpers import runtime, dotenv
    runtime.initialize()
    dotenv.load_dotenv()
    
    print(f"Host: {runtime.get_arg('host') or os.getenv('WEB_UI_HOST', 'localhost')}")
    print(f"Port: {runtime.get_web_ui_port()}")
    
    print("Starting server...")
    import run_ui
    run_ui.run()
except Exception as e:
    import traceback
    print("ERROR:", str(e))
    traceback.print_exc()
    sys.exit(1)

