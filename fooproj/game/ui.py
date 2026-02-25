"""Runtime UI entities for the Ursina sandbox."""

from ursina import Text


def create_controls_hint() -> Text:
    """Render controls help text and return its entity."""
    return Text(
        name="controls_hint_text",
        text=(
            "Move: arrow keys (forward/back + strafe)\n"
            "Turn: page up/down + mouse (captured)\n"
            "Zoom: mouse wheel\n"
            "Camera: c / gamepad dpad left (orbit/chase)\n"
            "UI: u toggle controls\n"
            "Zoom pad: gamepad dpad up/down\n"
            "Controller: R2/L2 gas-brake, L1/R1 strafe, LS steer, RS look"
        ),
        x=-0.86,
        y=0.47,
        scale=0.9,
        background=True,
    )
