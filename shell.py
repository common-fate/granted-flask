import code
import sys
import requests


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
        url = "https://x6mwweu4s2.execute-api.ap-southeast-2.amazonaws.com/prod/api/v1/events-recorder"
        requests.post(
            url=url,
            json={"data": {"command": line}},
            headers={
                "X-Granted-Request": "TOKEN-123",
                "Content-Type": "application/json",
            },
        )
        #print(f"[Granted] recorded entry: {line}")
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
    print(
        "As part of our promise to protect customer data, we use Common Fate Granted (https://granted.dev) to audit shell access."
    )
    print(
        "Please enter an access token. If you don't have one, visit https://demo.granted.com/access/request/rul_2BtW97o6jTacUuzxNJZorACn5v0 to request one."
    )
    input("Access token: ")
    console = GrantedConsole(local)
    if readfunc is not None:
        console.raw_input = readfunc
    else:
        try:
            import readline
        except ImportError:
            pass
    console.interact(banner, exitmsg)


def main():
    banner = (
        f"Python {sys.version} on {sys.platform}\n"
        "This session is being audited with Common Fate Granted."
    )
    interact(banner=banner)


if __name__ == "__main__":
    main()
