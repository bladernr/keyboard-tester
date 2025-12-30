# Keyboard Checker

A graphical keyboard testing utility for Ubuntu that captures and displays detailed information about keyboard key presses.

## Features

- Captures all keyboard events including letters, numbers, special keys, function keys, and media keys
- Displays key name, Qt key code, native virtual key code, and text representation
- Shows modifier keys (SHIFT, CTRL, ALT, META)
- Fully traps keyboard events (doesn't pass to OS when window is focused)
- Real-time event log
- Safe exit mechanism: Press ESC 3 times rapidly OR hold ESC for 3 seconds

## Requirements

- Python 3.8 or higher
- PyQt6

## Installation

Install PyQt6 from Ubuntu repositories:
```bash
sudo apt install python3-pyqt6
```

## Usage

Run the application:
```bash
./keyboard_checker.py
```

Or:
```bash
python3 keyboard_checker.py
```

Note: You may see a harmless GTK module warning which can be safely ignored.

## Testing Keys

Once the application is running:
- Press any key to see detailed information
- Try F keys (F1-F12), M key, SHIFT, ENTER, BACKSPACE, ESC, etc.
- Try Fn+F key combinations to see what keycodes they produce
- Check the event log for a history of all key presses

## Exiting

To exit the application:
- Press ESC 3 times rapidly (within 1 second), OR
- Hold ESC for 3 seconds

## Testing

The project includes comprehensive unit tests. To run the tests:

1. Install pytest (if not already installed):
```bash
sudo apt install python3-pytest
```

2. Run the test suite:
```bash
python3 -m pytest test_keyboard_checker.py -v
```

The test suite covers:
- Key name conversion for all special keys, function keys, and modifiers
- Left vs right modifier key detection
- Escape key exit detection (triple-press and hold)
- UI component initialization
- Event handling and logging

## License

This program is free software licensed under the GNU General Public License v3.0.

You can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

See the [LICENSE](LICENSE) file for the full license text, or visit <https://www.gnu.org/licenses/>.
