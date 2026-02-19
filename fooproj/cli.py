"""Command-line entrypoint for fooproj."""


def main() -> None:
    """Run the CLI entrypoint."""
    from fooproj.game import run_game

    run_game()


if __name__ == "__main__":
    main()
