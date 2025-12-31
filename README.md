# Keyboard Checker

A graphical keyboard testing utility for Ubuntu that captures and displays detailed information about keyboard key presses. Also includes a typing test mode to measure and improve typing speed.

## Features

### Keyboard Checker Mode
- Captures all keyboard events including letters, numbers, special keys, function keys, and media keys
- Displays key name, Qt key code, native virtual key code, and text representation
- Shows modifier keys (SHIFT, CTRL, ALT, META)
- Fully traps keyboard events (doesn't pass to OS when window is focused)
- Real-time event log
- Safe exit mechanism: Press ESC 3 times rapidly OR hold ESC for 3 seconds

### Typing Test Mode
- Time-constrained typing tests (30 seconds, 1 minute, or 2 minutes)
- 25 curated prose and literature samples (2-3 samples combined per test for sufficient length)
- Real-time error detection with color-coded feedback (green=correct, red=error)
- Comprehensive statistics:
  - Words per minute (WPM)
  - Adjusted WPM (accounting for errors)
  - Accuracy percentage
  - Peak WPM
  - Consistency score
  - Total characters and words typed
  - Error count
- Persistent history tracking stored in `~/.local/share/keyboard-checker/typing_history.json`
- Historical performance view with recent test results

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

## Keyboard Checker Mode

Once the application is running in keyboard checker mode:
- Press any key to see detailed information
- Try F keys (F1-F12), M key, SHIFT, ENTER, BACKSPACE, ESC, etc.
- Try Fn+F key combinations to see what keycodes they produce
- Check the event log for a history of all key presses
- Click "Switch to Typing Test" to enter typing test mode

## Typing Test Mode

To use the typing test:

1. Click "Switch to Typing Test" from the main keyboard checker window
2. Select your desired test duration (30 seconds, 1 minute, or 2 minutes)
3. Click "Start Test"
4. Type the displayed text samples as accurately as possible
5. Characters will turn green when correct and red when incorrect
6. When time expires, view your statistics (automatically saved)
7. Click "Try Again" to take another test
8. Click "Switch to Keyboard Checker" to return to keyboard testing mode

**Note:** Test results are automatically saved to your history when the test completes.

### Understanding Statistics

- **WPM**: Raw words per minute (characters typed ÷ 5 ÷ minutes)
- **Adjusted WPM**: WPM minus error penalty
- **Accuracy**: Percentage of correctly typed characters
- **Peak WPM**: Highest WPM achieved during any sampling window
- **Consistency**: How steady your typing speed was (lower is better)
  - Excellent: < 5
  - Good: 5-10
  - Fair: 10-15
  - Variable: > 15

### History Tracking

All saved test results are stored in `~/.local/share/keyboard-checker/typing_history.json` and persist across sessions. The history table shows your 10 most recent tests with:
- Date and time
- Test duration
- WPM and adjusted WPM
- Accuracy percentage

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

2. Run all test suites:
```bash
python3 -m pytest test_keyboard_checker.py test_typing_test.py -v
```

Or run individual test suites:
```bash
# Keyboard checker tests (42 tests)
python3 -m pytest test_keyboard_checker.py -v

# Typing test tests (29 tests)
python3 -m pytest test_typing_test.py -v
```

### Test Coverage

**Keyboard Checker Tests (test_keyboard_checker.py):**
- Key name conversion for all special keys, function keys, and modifiers
- Left vs right modifier key detection
- Escape key exit detection (triple-press and hold)
- UI component initialization
- Event handling and logging

**Typing Test Tests (test_typing_test.py):**
- Text sample loading and validation
- History file operations (save, load, query)
- WPM and accuracy calculations
- Statistics generation (peak WPM, consistency, adjusted WPM)
- UI state management
- Full typing test workflow integration

## License

This program is free software licensed under the GNU General Public License v3.0.

You can redistribute it and/or modify it under the terms of the GNU General Public License as published by the Free Software Foundation, either version 3 of the License, or (at your option) any later version.

This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU General Public License for more details.

See the [LICENSE](LICENSE) file for the full license text, or visit <https://www.gnu.org/licenses/>.
