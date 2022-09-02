
from __future__ import absolute_import, division, print_function
from operator import truediv

import os
import sys

import code
import click
import requests
import getpass
import os
from flask.cli import with_appcontext

token = ""

class GrantedConsole(code.InteractiveConsole):
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
        base_url = os.environ['GRANTED_WEBHOOK_URL']
        url = base_url + "/events-recorder"
        x = requests.post(
            url=url,
            json={"data": {"command": line}},
            headers={
                "X-Granted-Request": token,
                "Content-Type": "application/json",
            },
        )

        print("response from webhook: ", x.text)
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
    if 'GRANTED_WEBHOOK_URL' not in os.environ:
        print('GRANTED_WEBHOOK_URL (Granted deployment URL) is not set, if you are seeing this contact your administrator.')
        
        return


    print(
        "As part of our promise to protect customer data, we use Common Fate Granted (https://granted.dev) to audit shell access.\n"
    )
    print(
        "Please enter an access token.\n"
    )

    retry = True

    while retry:
        token = getpass.getpass("Access token: ")
        console = GrantedConsole(local)
        if readfunc is not None:
            console.raw_input = readfunc  
        else:
            try:
                import readline
            except ImportError:
                pass
            
        
        base_url = os.environ['GRANTED_WEBHOOK_URL']
        url = base_url + "/access-token"
        x = requests.post(
            url=url,
            
            headers={
                "X-Granted-Request": token,
                "Content-Type": "application/json",
            },
        )
    
        if x.status_code != 200:
            print("That token doesn't exist for your account or has expired: ", x.status_code)
            continue
        else:
            retry = False
        
    print('Correct token, entering Flask shell...\n')
    console.interact(banner, exitmsg)



@click.command('shell', short_help='Runs a shell in the app context.')
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
    startup = os.environ.get('PYTHONSTARTUP')
    if startup and os.path.isfile(startup):
        with open(startup, 'r') as f:
            eval(compile(f.read(), startup, 'exec'), ctx)

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