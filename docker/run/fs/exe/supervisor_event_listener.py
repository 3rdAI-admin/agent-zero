#!/usr/bin/python
import sys
import os
import logging
import subprocess
import time

from supervisor.childutils import listener # type: ignore

# Reason: These processes are non-essential (VNC/X11 desktop stack).
# If they enter FATAL state, we log a warning but do NOT kill supervisord,
# because the main Web UI and agent services work perfectly without them.
NON_ESSENTIAL_PROCESSES = frozenset({
    "xvfb",
    "fluxbox",
    "x11vnc",
    "autocutsel",
    "wallpaper",
    "setup_vnc_password",
    "setup_clipboard_shortcuts",
    "install_security_tools",
})


def main(args):
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG, format='%(asctime)s %(levelname)s %(filename)s: %(message)s')
    logger = logging.getLogger("supervisord-watchdog")
    debug_mode = True if 'DEBUG' in os.environ else False

    while True:
        logger.info("Listening for events...")
        headers, body = listener.wait(sys.stdin, sys.stdout)
        body = dict([pair.split(":") for pair in body.split(" ")])

        logger.debug("Headers: %r", repr(headers))
        logger.debug("Body: %r", repr(body))
        logger.debug("Args: %r", repr(args))

        if debug_mode:
            listener.ok(sys.stdout)
            continue

        try:
            if headers["eventname"] == "PROCESS_STATE_FATAL":
                process_name = body.get("processname", "unknown")
                logger.info("Process '%s' entered FATAL state.", process_name)

                # Skip non-essential processes — do not kill the container
                if process_name in NON_ESSENTIAL_PROCESSES:
                    logger.warning(
                        "Ignoring FATAL for non-essential process '%s'. "
                        "The Web UI and agent services are unaffected.",
                        process_name,
                    )
                    listener.ok(sys.stdout)
                    continue

                if not args or process_name in args:
                    logger.error("Killing off supervisord instance ...")
                    _ = subprocess.call(["/bin/kill", "-15", "1"], stdout=sys.stderr)
                    logger.info("Sent TERM signal to init process")
                    time.sleep(5)
                    logger.critical("Why am I still alive? Send KILL to all processes...")
                    _ = subprocess.call(["/bin/kill", "-9", "-1"], stdout=sys.stderr)
        except Exception as e:
            logger.critical("Unexpected Exception: %s", str(e))
            listener.fail(sys.stdout)
            exit(1)
        else:
            listener.ok(sys.stdout)


if __name__ == '__main__':
    main(sys.argv[1:])
