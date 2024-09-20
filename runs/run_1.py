from mcp import Run


def run_1(run: Run):
    """Run 1"""
    run.drive_attachment(1, 100, duration=1)
    run.drive_attachment(2, 100, duration=1)
    run.drive_attachment(3, 100, duration=1)
    run.drive_attachment(4, 100, duration=1)


def register(mcp):
    mcp.run(color="red")(run_1)
