"""AgentStan HTTP API server. Requires: pip install agentstan[server]"""


def create_app(**kwargs):
    from .app import create_app as _create_app
    return _create_app(**kwargs)


def main():
    from .app import main as _main
    _main()
