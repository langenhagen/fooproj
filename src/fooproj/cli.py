"""Command-line entrypoint for fooproj."""

def build_greeting(name: str = "world") -> str:
    """Build a hello string for a given name."""
    return f"Hello from fooproj, {name}!"


def main() -> None:
    """Run the CLI entrypoint."""
    print(build_greeting())


if __name__ == "__main__":
    main()
