"""Command-line entrypoint for fooproj."""

from fooproj.game import run_game


def main() -> None:
    """Run the CLI entrypoint."""
    run_game()


if __name__ == "__main__":
    main()
