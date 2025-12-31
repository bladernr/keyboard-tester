#!/usr/bin/env python3
"""
Keyboard Checker - A tool to test and display keyboard key presses

Copyright (C) 2025

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import sys
import json
import random
import statistics
from pathlib import Path
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QTextEdit, QLabel, QPushButton, QHBoxLayout,
                             QRadioButton, QButtonGroup, QTableWidget,
                             QTableWidgetItem, QHeaderView, QStackedWidget)
from PyQt6.QtCore import Qt, QTimer, QEvent
from PyQt6.QtGui import QKeyEvent, QFont, QTextCharFormat, QColor, QTextCursor

from text_samples import TYPING_SAMPLES


class KeyboardChecker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.escape_press_times = []
        self.escape_press_timer = None
        self.escape_hold_timer = None
        self.escape_hold_start = None
        self.init_ui()
        self.init_mode_switching()

    def init_ui(self):
        self.setWindowTitle("Keyboard Checker")
        self.setGeometry(100, 100, 800, 600)

        # Set focus policy to capture all keyboard events
        self.setFocusPolicy(Qt.FocusPolicy.StrongFocus)

        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        central_widget.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout = QVBoxLayout(central_widget)

        # Title label
        title = QLabel("Keyboard Checker")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(title)

        # Instructions
        instructions = QLabel(
            "Press any key to see its information below.\n"
            "Note: Fn key is hardware-level and shows what Fn+Key combinations produce.\n"
            "To exit: Press ESC 3 times rapidly OR hold ESC for 3 seconds"
        )
        instructions.setAlignment(Qt.AlignmentFlag.AlignCenter)
        instructions.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(instructions)

        # Current key display (large)
        self.current_key_label = QLabel("Press a key... (Click here if keys not working)")
        self.current_key_label.setFont(QFont("Arial", 24, QFont.Weight.Bold))
        self.current_key_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.current_key_label.setStyleSheet(
            "background-color: #e0e0e0; padding: 20px; border-radius: 5px;"
        )
        self.current_key_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.current_key_label.mousePressEvent = lambda e: self.setFocus()
        layout.addWidget(self.current_key_label)

        # Key details display
        self.details_label = QLabel("")
        self.details_label.setFont(QFont("Monospace", 10))
        self.details_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        self.details_label.setWordWrap(True)
        self.details_label.setStyleSheet(
            "background-color: #f5f5f5; padding: 10px; border-radius: 5px;"
        )
        self.details_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self.details_label)

        # Event log
        log_label = QLabel("Event Log:")
        log_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        log_label.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(log_label)

        self.event_log = QTextEdit()
        self.event_log.setReadOnly(True)
        self.event_log.setFont(QFont("Monospace", 9))
        self.event_log.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self.event_log)

        # Clear button
        clear_btn = QPushButton("Clear Log")
        clear_btn.clicked.connect(self.clear_log)
        clear_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(clear_btn)

        # Mode switch button
        self.mode_switch_btn = QPushButton("Switch to Typing Test")
        self.mode_switch_btn.clicked.connect(self.switch_to_typing_test)
        self.mode_switch_btn.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        layout.addWidget(self.mode_switch_btn)

    def showEvent(self, event):
        """Ensure the window has focus when shown"""
        super().showEvent(event)
        self.setFocus()
        self.activateWindow()

    def keyPressEvent(self, event: QKeyEvent):
        """Override to capture all key press events"""
        self.handle_key_press(event)
        # Don't call super() to prevent default handling

    def keyReleaseEvent(self, event: QKeyEvent):
        """Override to capture all key release events"""
        self.handle_key_release(event)
        # Don't call super() to prevent default handling

    def handle_key_press(self, event: QKeyEvent):
        """Handle key press events"""
        key = event.key()
        key_text = event.text()
        modifiers = event.modifiers()
        native_key = event.nativeVirtualKey()

        # Get key name
        key_name = self.get_key_name(key, key_text, native_key)

        # Get modifier names
        modifier_names = self.get_modifier_names(modifiers)

        # Build display strings
        display_name = key_name
        if modifier_names:
            display_name = f"{modifier_names} + {key_name}"

        # Update current key display
        self.current_key_label.setText(display_name)

        # Build detailed information
        details = []
        details.append(f"Key Name: {key_name}")
        details.append(f"Qt Key Code: {key} (0x{key:04X})")
        details.append(f"Native Virtual Key: {native_key} (0x{native_key:04X})")
        details.append(f"Text: '{key_text}' (empty if special key)" if key_text else "Text: (none - special key)")
        details.append(f"Modifiers: {modifier_names if modifier_names else 'None'}")

        self.details_label.setText("\n".join(details))

        # Log the event
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        log_entry = f"[{timestamp}] PRESS: {display_name} | Qt:{key} Native:0x{native_key:04X}"
        self.event_log.append(log_entry)

        # Scroll to bottom
        self.event_log.verticalScrollBar().setValue(
            self.event_log.verticalScrollBar().maximum()
        )

        # Check for escape key
        if key == Qt.Key.Key_Escape:
            self.handle_escape_press()

    def handle_key_release(self, event: QKeyEvent):
        """Handle key release events"""
        key = event.key()

        if key == Qt.Key.Key_Escape:
            self.handle_escape_release()

    def get_key_name(self, key, text, native_key=0):
        """Convert Qt key code to readable name"""
        # Special keys mapping
        special_keys = {
            Qt.Key.Key_Escape: "ESC",
            Qt.Key.Key_Tab: "TAB",
            Qt.Key.Key_Backtab: "BACKTAB",
            Qt.Key.Key_Backspace: "BACKSPACE",
            Qt.Key.Key_Return: "RETURN",
            Qt.Key.Key_Enter: "ENTER",
            Qt.Key.Key_Insert: "INSERT",
            Qt.Key.Key_Delete: "DELETE",
            Qt.Key.Key_Pause: "PAUSE",
            Qt.Key.Key_Print: "PRINT",
            Qt.Key.Key_Home: "HOME",
            Qt.Key.Key_End: "END",
            Qt.Key.Key_Left: "LEFT ARROW",
            Qt.Key.Key_Up: "UP ARROW",
            Qt.Key.Key_Right: "RIGHT ARROW",
            Qt.Key.Key_Down: "DOWN ARROW",
            Qt.Key.Key_PageUp: "PAGE UP",
            Qt.Key.Key_PageDown: "PAGE DOWN",
            Qt.Key.Key_CapsLock: "CAPS LOCK",
            Qt.Key.Key_NumLock: "NUM LOCK",
            Qt.Key.Key_ScrollLock: "SCROLL LOCK",
            Qt.Key.Key_Space: "SPACE",
        }

        # Handle modifier keys with left/right detection
        # On Linux X11, native virtual key codes help distinguish left vs right
        if key == Qt.Key.Key_Shift:
            # Left Shift is typically 0x32 (50), Right Shift is 0x3e (62)
            if native_key == 0x3e or native_key == 62:
                return "SHIFT (RIGHT)"
            return "SHIFT (LEFT)"
        elif key == Qt.Key.Key_Control:
            # Left Ctrl is typically 0x25 (37), Right Ctrl is 0x69 (105)
            if native_key == 0x69 or native_key == 105:
                return "CTRL (RIGHT)"
            return "CTRL (LEFT)"
        elif key == Qt.Key.Key_Alt:
            # Left Alt is typically 0x40 (64), Right Alt is 0x6c (108)
            if native_key == 0x6c or native_key == 108:
                return "ALT/OPTION (RIGHT)"
            return "ALT/OPTION (LEFT)"
        elif key == Qt.Key.Key_AltGr:
            return "ALT GR (RIGHT)"
        elif key == Qt.Key.Key_Meta:
            # Left Super/Meta is typically 0x85 (133), Right is 0x86 (134)
            if native_key == 0x86 or native_key == 134:
                return "META/SUPER (RIGHT)"
            return "META/SUPER (LEFT)"

        # F keys
        for i in range(1, 36):
            special_keys[getattr(Qt.Key, f'Key_F{i}')] = f"F{i}"

        # Media and function keys
        media_keys = {
            Qt.Key.Key_VolumeDown: "VOLUME DOWN",
            Qt.Key.Key_VolumeUp: "VOLUME UP",
            Qt.Key.Key_VolumeMute: "VOLUME MUTE",
            Qt.Key.Key_MediaPlay: "MEDIA PLAY",
            Qt.Key.Key_MediaStop: "MEDIA STOP",
            Qt.Key.Key_MediaPrevious: "MEDIA PREVIOUS",
            Qt.Key.Key_MediaNext: "MEDIA NEXT",
            Qt.Key.Key_MonBrightnessUp: "BRIGHTNESS UP",
            Qt.Key.Key_MonBrightnessDown: "BRIGHTNESS DOWN",
        }
        special_keys.update(media_keys)

        if key in special_keys:
            return special_keys[key]

        # For regular characters
        if text and text.isprintable():
            return text.upper() if len(text) == 1 else text

        # Fallback for unknown keys - just show the key code
        return f"KEY_0x{key:04X}"

    def get_modifier_names(self, modifiers):
        """Convert Qt modifiers to readable names"""
        mod_list = []

        if modifiers & Qt.KeyboardModifier.ShiftModifier:
            mod_list.append("SHIFT")
        if modifiers & Qt.KeyboardModifier.ControlModifier:
            mod_list.append("CTRL")
        if modifiers & Qt.KeyboardModifier.AltModifier:
            mod_list.append("ALT")
        if modifiers & Qt.KeyboardModifier.MetaModifier:
            mod_list.append("META")

        return " + ".join(mod_list)

    def handle_escape_press(self):
        """Handle escape key press for exit detection"""
        current_time = datetime.now()

        # Track escape press times for triple-press detection
        self.escape_press_times.append(current_time)

        # Keep only last 3 presses
        if len(self.escape_press_times) > 3:
            self.escape_press_times.pop(0)

        # Check for 3 rapid presses (within 1 second)
        if len(self.escape_press_times) == 3:
            time_diff = (self.escape_press_times[-1] - self.escape_press_times[0]).total_seconds()
            if time_diff < 1.0:
                self.exit_application()
                return

        # Start hold timer for 3-second hold detection
        if self.escape_hold_timer is None:
            self.escape_hold_start = current_time
            self.escape_hold_timer = QTimer()
            self.escape_hold_timer.timeout.connect(self.check_escape_hold)
            self.escape_hold_timer.start(100)  # Check every 100ms

    def handle_escape_release(self):
        """Handle escape key release"""
        if self.escape_hold_timer is not None:
            self.escape_hold_timer.stop()
            self.escape_hold_timer = None
            self.escape_hold_start = None

    def check_escape_hold(self):
        """Check if escape has been held for 3 seconds"""
        if self.escape_hold_start is not None:
            hold_duration = (datetime.now() - self.escape_hold_start).total_seconds()
            if hold_duration >= 3.0:
                self.exit_application()

    def exit_application(self):
        """Exit the application"""
        self.event_log.append("\n=== Exit condition detected. Closing... ===")
        QTimer.singleShot(500, self.close)

    def clear_log(self):
        """Clear the event log"""
        self.event_log.clear()

    def init_mode_switching(self):
        """Initialize mode switching between keyboard checker and typing test"""
        # Create stacked widget to hold both modes
        self.stacked_widget = QStackedWidget()

        # Get the current central widget (keyboard checker)
        self.keyboard_checker_widget = self.centralWidget()

        # Create typing test widget
        self.typing_test_widget = QWidget()
        typing_test_layout = QVBoxLayout(self.typing_test_widget)

        # Add typing test
        self.typing_test = TypingTest()
        typing_test_layout.addWidget(self.typing_test)

        # Add back button
        back_btn = QPushButton("Switch to Keyboard Checker")
        back_btn.clicked.connect(self.switch_to_keyboard_checker)
        typing_test_layout.addWidget(back_btn)

        # Add both widgets to stacked widget
        self.stacked_widget.addWidget(self.keyboard_checker_widget)
        self.stacked_widget.addWidget(self.typing_test_widget)

        # Set stacked widget as central widget
        self.setCentralWidget(self.stacked_widget)

    def switch_to_typing_test(self):
        """Switch to typing test mode"""
        self.setWindowTitle("Keyboard Checker - Typing Test")
        self.stacked_widget.setCurrentWidget(self.typing_test_widget)

    def switch_to_keyboard_checker(self):
        """Switch back to keyboard checker mode"""
        self.setWindowTitle("Keyboard Checker")
        self.stacked_widget.setCurrentWidget(self.keyboard_checker_widget)
        self.setFocus()
        self.activateWindow()


class TypingHistory:
    """Manages typing test history storage and retrieval"""

    def __init__(self):
        self.history_dir = Path.home() / ".local" / "share" / "keyboard-checker"
        self.history_file = self.history_dir / "typing_history.json"
        self._ensure_history_dir()

    def _ensure_history_dir(self):
        """Create history directory if it doesn't exist"""
        self.history_dir.mkdir(parents=True, exist_ok=True)

    def load_history(self):
        """Load typing test history from file"""
        if not self.history_file.exists():
            return []

        try:
            with open(self.history_file, 'r') as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            # Corrupted or unreadable file
            return []

    def save_result(self, result):
        """Append a new result to history"""
        history = self.load_history()
        history.append(result)

        try:
            with open(self.history_file, 'w') as f:
                json.dump(history, f, indent=2)
        except IOError:
            pass  # Fail silently if can't write

    def get_all_results(self):
        """Get all test results"""
        return self.load_history()

    def get_recent(self, n=10):
        """Get the N most recent results"""
        history = self.load_history()
        return history[-n:] if len(history) > n else history

    def get_by_duration(self, duration_seconds):
        """Get results filtered by test duration"""
        history = self.load_history()
        return [r for r in history if r.get('duration') == duration_seconds]

    def get_average_wpm(self):
        """Calculate overall average WPM"""
        history = self.load_history()
        if not history:
            return 0.0
        wpms = [r.get('wpm', 0) for r in history if 'wpm' in r]
        return statistics.mean(wpms) if wpms else 0.0

    def get_trend_data(self):
        """Get WPM trend data for graphing"""
        history = self.load_history()
        return [(r.get('timestamp', ''), r.get('wpm', 0)) for r in history]


class TypingTest(QWidget):
    """Typing test widget with timer, statistics, and history"""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.history = TypingHistory()
        self.test_active = False
        self.test_start_time = None
        self.test_duration = 60  # default 1 minute
        self.current_sample = None
        self.typed_text = ""
        self.errors = []
        self.wpm_samples = []  # Track WPM every second for peak/consistency
        self.init_ui()

    def init_ui(self):
        """Initialize typing test UI"""
        layout = QVBoxLayout(self)

        # Title
        title = QLabel("Typing Test")
        title.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)

        # Duration selection
        duration_layout = QHBoxLayout()
        duration_label = QLabel("Test Duration:")
        duration_layout.addWidget(duration_label)

        self.duration_group = QButtonGroup(self)
        self.radio_30s = QRadioButton("30 seconds")
        self.radio_60s = QRadioButton("1 minute")
        self.radio_120s = QRadioButton("2 minutes")
        self.radio_60s.setChecked(True)

        self.duration_group.addButton(self.radio_30s, 30)
        self.duration_group.addButton(self.radio_60s, 60)
        self.duration_group.addButton(self.radio_120s, 120)

        duration_layout.addWidget(self.radio_30s)
        duration_layout.addWidget(self.radio_60s)
        duration_layout.addWidget(self.radio_120s)
        duration_layout.addStretch()
        layout.addLayout(duration_layout)

        # Timer display
        self.timer_label = QLabel("Time: 0:00")
        self.timer_label.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        self.timer_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.timer_label)

        # Sample text display
        sample_label = QLabel("Text to type:")
        sample_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(sample_label)

        self.sample_display = QTextEdit()
        self.sample_display.setReadOnly(True)
        self.sample_display.setFont(QFont("Monospace", 11))
        # Auto-expand to show all text - adjust height based on content
        self.sample_display.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        layout.addWidget(self.sample_display)

        # Typing input area
        input_label = QLabel("Your typing:")
        input_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(input_label)

        self.typing_input = QTextEdit()
        self.typing_input.setFont(QFont("Monospace", 11))
        self.typing_input.setMaximumHeight(150)
        self.typing_input.setEnabled(False)
        self.typing_input.textChanged.connect(self.handle_typing_input)
        layout.addWidget(self.typing_input)

        # Start button
        self.start_button = QPushButton("Start Test")
        self.start_button.clicked.connect(self.start_test)
        layout.addWidget(self.start_button)

        # Statistics panel (hidden initially)
        self.stats_panel = QLabel("")
        self.stats_panel.setFont(QFont("Monospace", 10))
        self.stats_panel.setStyleSheet(
            "background-color: #f0f0f0; color: #000000; padding: 15px; border-radius: 5px;"
        )
        self.stats_panel.setVisible(False)
        self.stats_panel.setWordWrap(True)
        layout.addWidget(self.stats_panel)

        # Action buttons (hidden initially)
        self.action_buttons = QWidget()
        action_layout = QHBoxLayout(self.action_buttons)

        self.save_button = QPushButton("Results Saved")
        self.save_button.setEnabled(False)
        action_layout.addWidget(self.save_button)

        self.retry_button = QPushButton("Try Again")
        self.retry_button.clicked.connect(self.reset_test)
        action_layout.addWidget(self.retry_button)

        self.action_buttons.setVisible(False)
        layout.addWidget(self.action_buttons)

        # History display
        history_label = QLabel("Recent Results:")
        history_label.setFont(QFont("Arial", 11, QFont.Weight.Bold))
        layout.addWidget(history_label)

        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels(
            ["Date/Time", "Duration", "WPM", "Adj WPM", "Accuracy"]
        )
        self.history_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.history_table.setMaximumHeight(150)
        layout.addWidget(self.history_table)

        # Timer for countdown
        self.test_timer = QTimer()
        self.test_timer.timeout.connect(self.timer_tick)

        # Timer for WPM sampling
        self.wpm_sample_timer = QTimer()
        self.wpm_sample_timer.timeout.connect(self.sample_wpm)

        # Load and display history
        self.load_and_display_history()

    def start_test(self):
        """Start a new typing test"""
        # Get selected duration
        self.test_duration = self.duration_group.checkedId()

        # Disable duration selection
        self.radio_30s.setEnabled(False)
        self.radio_60s.setEnabled(False)
        self.radio_120s.setEnabled(False)

        # Load multiple random samples to ensure enough text
        # Concatenate 2-3 samples depending on duration
        num_samples = 2 if self.test_duration <= 60 else 3
        samples = random.sample(TYPING_SAMPLES, num_samples)

        # Combine samples with separator
        combined_text = " ".join([s['text'] for s in samples])
        combined_sources = " | ".join([s['source'] for s in samples])

        self.current_sample = {
            'id': samples[0]['id'],  # Use first sample's ID
            'text': combined_text,
            'source': combined_sources
        }
        self.sample_display.setPlainText(self.current_sample['text'])

        # Auto-resize sample display to fit all content without scrolling
        doc = self.sample_display.document()
        doc_height = doc.size().height()
        self.sample_display.setFixedHeight(int(doc_height) + 10)  # Add padding

        # Reset state
        self.test_active = True
        self.test_start_time = datetime.now()
        self.typed_text = ""
        self.errors = []
        self.wpm_samples = []
        self.typing_input.clear()
        self.typing_input.setEnabled(True)
        self.typing_input.setFocus()

        # Hide stats
        self.stats_panel.setVisible(False)
        self.action_buttons.setVisible(False)

        # Update UI
        self.start_button.setText("Test in Progress...")
        self.start_button.setEnabled(False)

        # Start timers
        self.test_timer.start(100)  # Update every 100ms
        self.wpm_sample_timer.start(1000)  # Sample WPM every second

    def timer_tick(self):
        """Update timer display"""
        if not self.test_active:
            return

        elapsed = (datetime.now() - self.test_start_time).total_seconds()
        remaining = max(0, self.test_duration - elapsed)

        minutes = int(remaining // 60)
        seconds = int(remaining % 60)
        self.timer_label.setText(f"Time: {minutes}:{seconds:02d}")

        if remaining <= 0:
            self.end_test()

    def sample_wpm(self):
        """Sample current WPM for peak/consistency calculation"""
        if not self.test_active:
            return

        elapsed = (datetime.now() - self.test_start_time).total_seconds()
        if elapsed > 0:
            chars_typed = len(self.typed_text)
            current_wpm = (chars_typed / 5) / (elapsed / 60)
            self.wpm_samples.append(current_wpm)

    def handle_typing_input(self):
        """Handle user typing input with word-based error detection"""
        if not self.test_active:
            return

        self.typed_text = self.typing_input.toPlainText()
        source_text = self.current_sample['text']

        # Clear and rebuild with color formatting
        cursor = self.typing_input.textCursor()
        current_pos = cursor.position()

        self.typing_input.blockSignals(True)  # Prevent recursion
        self.typing_input.clear()

        # Reset errors for this iteration
        self.errors = []

        # Tokenize source and typed text into words and whitespace
        # This allows word-by-word comparison without error propagation
        import re

        # Split into tokens (words/punctuation + spaces)
        source_tokens = []
        for match in re.finditer(r'\S+|\s+', source_text):
            source_tokens.append(match.group())

        typed_tokens = []
        for match in re.finditer(r'\S+|\s+', self.typed_text):
            typed_tokens.append((match.group(), match.start(), match.end()))

        # Match typed tokens to source tokens and colorize
        cursor = self.typing_input.textCursor()
        typed_char_idx = 0

        for token_idx, (typed_token, typed_start, typed_end) in enumerate(typed_tokens):
            # Get corresponding source token (if exists)
            if token_idx >= len(source_tokens):
                # Typed beyond source - mark as red (error) for tokens close to end,
                # gray for tokens far beyond
                # This catches things like typing a space instead of punctuation
                is_near_end = token_idx < len(source_tokens) + 2
                for char in typed_token:
                    fmt = QTextCharFormat()
                    if is_near_end:
                        fmt.setForeground(QColor(200, 0, 0))
                        self.errors.append((typed_char_idx, char, ''))
                    else:
                        fmt.setForeground(QColor(128, 128, 128))
                    cursor.movePosition(QTextCursor.MoveOperation.End)
                    cursor.insertText(char, fmt)
                    typed_char_idx += 1
                continue

            source_token = source_tokens[token_idx]

            # Compare character by character within this token
            for i, char in enumerate(typed_token):
                if i < len(source_token):
                    if char == source_token[i]:
                        # Correct character - green
                        fmt = QTextCharFormat()
                        fmt.setForeground(QColor(0, 150, 0))
                        cursor.movePosition(QTextCursor.MoveOperation.End)
                        cursor.insertText(char, fmt)
                    else:
                        # Incorrect character - red
                        fmt = QTextCharFormat()
                        fmt.setForeground(QColor(200, 0, 0))
                        cursor.movePosition(QTextCursor.MoveOperation.End)
                        cursor.insertText(char, fmt)
                        self.errors.append((typed_char_idx, char, source_token[i]))
                else:
                    # Extra character in this token - red
                    fmt = QTextCharFormat()
                    fmt.setForeground(QColor(200, 0, 0))
                    cursor.movePosition(QTextCursor.MoveOperation.End)
                    cursor.insertText(char, fmt)
                    self.errors.append((typed_char_idx, char, ''))

                typed_char_idx += 1

        # Restore cursor position
        cursor = self.typing_input.textCursor()
        cursor.setPosition(min(current_pos, len(self.typed_text)))
        self.typing_input.setTextCursor(cursor)
        self.typing_input.blockSignals(False)

    def end_test(self):
        """End the test and show statistics"""
        self.test_active = False
        self.test_timer.stop()
        self.wpm_sample_timer.stop()

        self.typing_input.setEnabled(False)
        self.start_button.setText("Start Test")
        self.start_button.setEnabled(True)

        # Re-enable duration selection
        self.radio_30s.setEnabled(True)
        self.radio_60s.setEnabled(True)
        self.radio_120s.setEnabled(True)

        # Calculate statistics
        stats = self.calculate_statistics()

        # Display statistics
        self.display_statistics(stats)

        # Store stats
        self.current_stats = stats

        # Auto-save results
        self.save_results()

    def calculate_statistics(self):
        """Calculate all typing test statistics"""
        elapsed = self.test_duration
        source_text = self.current_sample['text']

        # Basic counts
        total_chars = len(self.typed_text)
        total_words = len(self.typed_text.split())

        # Error count
        error_count = len(self.errors)

        # WPM calculation (standard: chars/5 / minutes)
        wpm = (total_chars / 5) / (elapsed / 60) if elapsed > 0 else 0

        # Adjusted WPM (standard net WPM formula: subtract error penalty from words before dividing by time)
        # Each error subtracts 1 word (5 characters worth)
        adjusted_wpm = max(0, ((total_chars / 5) - error_count) / (elapsed / 60)) if elapsed > 0 else 0

        # Accuracy
        accuracy = ((total_chars - error_count) / total_chars * 100) if total_chars > 0 else 0

        # Peak WPM
        peak_wpm = max(self.wpm_samples) if self.wpm_samples else wpm

        # Consistency (standard deviation of WPM samples)
        if len(self.wpm_samples) > 1:
            consistency = statistics.stdev(self.wpm_samples)
        else:
            consistency = 0

        return {
            'timestamp': datetime.now().isoformat(),
            'duration': elapsed,
            'text_sample_id': self.current_sample['id'],
            'wpm': round(wpm, 1),
            'adjusted_wpm': round(adjusted_wpm, 1),
            'accuracy_percent': round(accuracy, 1),
            'peak_wpm': round(peak_wpm, 1),
            'consistency_score': round(consistency, 1),
            'total_characters': total_chars,
            'total_words': total_words,
            'errors': error_count,
            'error_details': self.errors
        }

    def display_statistics(self, stats):
        """Display statistics in the stats panel"""
        consistency_label = "Excellent" if stats['consistency_score'] < 5 else \
                          "Good" if stats['consistency_score'] < 10 else \
                          "Fair" if stats['consistency_score'] < 15 else "Variable"

        stats_text = f"""TYPING TEST RESULTS
{'='*50}
Duration:         {stats['duration']} seconds
WPM:              {stats['wpm']}
Adjusted WPM:     {stats['adjusted_wpm']}
Accuracy:         {stats['accuracy_percent']}%
Peak WPM:         {stats['peak_wpm']}
Consistency:      {consistency_label} (σ={stats['consistency_score']})
Characters:       {stats['total_characters']}
Words:            {stats['total_words']}
Errors:           {stats['errors']}
{'='*50}
Results automatically saved to history."""

        self.stats_panel.setText(stats_text)
        self.stats_panel.setVisible(True)
        self.action_buttons.setVisible(True)

    def save_results(self):
        """Save test results to history"""
        if hasattr(self, 'current_stats'):
            self.history.save_result(self.current_stats)

            # Refresh history display
            self.load_and_display_history()

            # Disable save button since results are auto-saved
            self.save_button.setText("Results Saved")
            self.save_button.setEnabled(False)

    def reset_test(self):
        """Reset for a new test"""
        self.typing_input.clear()
        self.sample_display.clear()
        self.stats_panel.setVisible(False)
        self.action_buttons.setVisible(False)
        self.timer_label.setText("Time: 0:00")

    def load_and_display_history(self):
        """Load and display recent test history"""
        recent = self.history.get_recent(10)
        recent.reverse()  # Show newest first

        self.history_table.setRowCount(len(recent))

        for i, result in enumerate(recent):
            # Parse timestamp
            try:
                dt = datetime.fromisoformat(result['timestamp'])
                timestamp_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                timestamp_str = result.get('timestamp', 'Unknown')

            self.history_table.setItem(i, 0, QTableWidgetItem(timestamp_str))
            self.history_table.setItem(i, 1, QTableWidgetItem(f"{result.get('duration', 0)}s"))
            self.history_table.setItem(i, 2, QTableWidgetItem(str(result.get('wpm', 0))))
            self.history_table.setItem(i, 3, QTableWidgetItem(str(result.get('adjusted_wpm', 0))))
            self.history_table.setItem(i, 4, QTableWidgetItem(f"{result.get('accuracy_percent', 0)}%"))


def main():
    app = QApplication(sys.argv)
    window = KeyboardChecker()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
