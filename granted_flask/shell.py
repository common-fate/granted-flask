from __future__ import absolute_import, division, print_function

import os
import sys

import code
import click
import requests
import getpass
import os
import urllib.parse
from flask.cli import with_appcontext


class GrantedConsole(code.InteractiveConsole):
    def __init__(self, locals=None, filename="<console>", token=None):
        """
        Sets up the console with a token to use for sending audited
        events back to the Granted webhook URL.
        """
        self.token = token
        super().__init__(locals=locals, filename=filename)

    def push(self, line):
        """Push a line to the interpreter.

        The line should not have a trailing newline; it may have
        internal newlines.  The line is appended to a buffer and the
        interpreter's runsource() method is called with the
        concatenated contents of the buffer as source.  If this
        indicates that the command was executed or invalid, the buffer
        is reset; otherwise, the command is incomplete, and the buffer
        is left as it was after the line was appended.  The return
        value is 1 if more input is required, 0 if the line was dealt
        with in some way (this is the same as runsource()).

        """
        base_url = os.environ["GRANTED_WEBHOOK_URL"]
        url = urllib.parse.urljoin(base_url, "events-recorder")
        x = requests.post(
            url=url,
            json={"data": {"command": line}},
            headers={
                "X-Granted-Request": self.token,
                "Content-Type": "application/json",
            },
        )

        print(f"[Granted] recorded entry: {line}")
        self.buffer.append(line)
        source = "\n".join(self.buffer)
        more = self.runsource(source, self.filename)
        if not more:
            self.resetbuffer()
        return more


def interact(banner=None, readfunc=None, local=None, exitmsg=None):
    """Closely emulate the interactive Python interpreter.

    This is a backwards compatible interface to the InteractiveConsole
    class.  When readfunc is not specified, it attempts to import the
    readline module to enable GNU readline if it is available.

    Arguments (all optional, all default to None):

    banner -- passed to InteractiveConsole.interact()
    readfunc -- if not None, replaces InteractiveConsole.raw_input()
    local -- passed to InteractiveInterpreter.__init__()
    exitmsg -- passed to InteractiveConsole.interact()

    """

    # Check if base url environment variable has been set before setting up the shell
    if "GRANTED_WEBHOOK_URL" not in os.environ:
        print(
            "GRANTED_WEBHOOK_URL (Granted deployment URL) is not set, if you are seeing this contact your administrator."
        )
        return

    print(
        "As part of our promise to protect customer data, we use Common Fate Granted (https://granted.dev) to audit shell access.\n"
    )
    print("Please enter an access token.\n")

    retry = True

    while retry:
        token = getpass.getpass("Access token: ")

        base_url = os.environ["GRANTED_WEBHOOK_URL"]
        url = urllib.parse.urljoin(base_url, "access-token/verify")

        x = requests.post(
            url=url,
            headers={
                "X-CommonFate-Access-Token": token,
                "Content-Type": "application/json",
            },
        )

        if x.status_code != 200:
            print(
                "That token doesn't exist for your account or has expired: ",
                x.status_code,
            )
            continue
        else:
            retry = False

    print("[✔] Entering Python shell...")

    # Setup the GrantedConsole interactive interpreter
    # and perform the same readfunc logic as the built-in code.interact() method does.
    console = GrantedConsole(locals=local, token=token)
    if readfunc is not None:
        console.raw_input = readfunc
    else:
        try:
            import readline
        except ImportError:
            pass

    url = urllib.parse.urljoin(base_url, "events-recorder")
    res = requests.post(
        url=url,
        json={"data": {"action": "Entered Shell"}},
        headers={
            "X-CommonFate-Access-Token": token,
            "Content-Type": "application/json",
        },
    )

    console.interact(banner, exitmsg)


@click.command("shell", short_help="Runs a shell in the app context.")
@with_appcontext
def shell_command():
    """Runs an interactive Python shell in the context of a given
    Flask application.  The application will populate the default
    namespace of this shell according to its configuration.
    This is useful for executing small snippets of management code
    without having to manually configuring the application.
    """
    from flask.globals import _app_ctx_stack

    app = _app_ctx_stack.top.app
    banner = (
        f"Python {sys.version} on {sys.platform}\n"
        f"App: {app.import_name}\n"
        f"Instance: {app.instance_path}"
    )

    ctx = {}

    # Support the regular Python interpreter startup script if someone
    # is using it.
    startup = os.environ.get("PYTHONSTARTUP")
    if startup and os.path.isfile(startup):
        with open(startup, "r") as f:
            eval(compile(f.read(), startup, "exec"), ctx)

    ctx.update(app.make_shell_context())

    # Site, customize, or startup script can set a hook to call when
    # entering interactive mode. The default one sets up readline with
    # tab and history completion.
    interactive_hook = getattr(sys, "__interactivehook__", None)

    if interactive_hook is not None:
        try:
            import readline
            from rlcompleter import Completer
        except ImportError:
            pass
        else:
            # rlcompleter uses __main__.__dict__ by default, which is
            # flask.__main__. Use the shell context instead.
            readline.set_completer(Completer(ctx).complete)

        interactive_hook()

    interact(banner=banner, local=ctx)
