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
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout,
                             QTextEdit, QLabel, QPushButton)
from PyQt6.QtCore import Qt, QTimer, QEvent
from PyQt6.QtGui import QKeyEvent, QFont


class KeyboardChecker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.escape_press_times = []
        self.escape_press_timer = None
        self.escape_hold_timer = None
        self.escape_hold_start = None
        self.init_ui()

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


def main():
    app = QApplication(sys.argv)
    window = KeyboardChecker()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
