#!/usr/bin/env python3
"""
Unit tests for Keyboard Checker

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
import pytest
from datetime import datetime, timedelta
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt, QEvent
from PyQt6.QtGui import QKeyEvent
from PyQt6.QtTest import QTest

from keyboard_checker import KeyboardChecker


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def window(qapp):
    """Create a KeyboardChecker window for testing"""
    win = KeyboardChecker()
    yield win
    win.close()


class TestKeyNameConversion:
    """Test key name conversion functionality"""

    def test_escape_key(self, window):
        """Test ESC key name"""
        result = window.get_key_name(Qt.Key.Key_Escape, "", 0)
        assert result == "ESC"

    def test_tab_key(self, window):
        """Test TAB key name"""
        result = window.get_key_name(Qt.Key.Key_Tab, "", 0)
        assert result == "TAB"

    def test_space_key(self, window):
        """Test SPACE key name"""
        result = window.get_key_name(Qt.Key.Key_Space, " ", 0)
        assert result == "SPACE"

    def test_backspace_key(self, window):
        """Test BACKSPACE key name"""
        result = window.get_key_name(Qt.Key.Key_Backspace, "", 0)
        assert result == "BACKSPACE"

    def test_return_key(self, window):
        """Test RETURN key name"""
        result = window.get_key_name(Qt.Key.Key_Return, "", 0)
        assert result == "RETURN"

    def test_arrow_keys(self, window):
        """Test arrow key names"""
        assert window.get_key_name(Qt.Key.Key_Left, "", 0) == "LEFT ARROW"
        assert window.get_key_name(Qt.Key.Key_Right, "", 0) == "RIGHT ARROW"
        assert window.get_key_name(Qt.Key.Key_Up, "", 0) == "UP ARROW"
        assert window.get_key_name(Qt.Key.Key_Down, "", 0) == "DOWN ARROW"

    def test_navigation_keys(self, window):
        """Test navigation key names"""
        assert window.get_key_name(Qt.Key.Key_Home, "", 0) == "HOME"
        assert window.get_key_name(Qt.Key.Key_End, "", 0) == "END"
        assert window.get_key_name(Qt.Key.Key_PageUp, "", 0) == "PAGE UP"
        assert window.get_key_name(Qt.Key.Key_PageDown, "", 0) == "PAGE DOWN"

    def test_function_keys(self, window):
        """Test function key names"""
        for i in range(1, 13):
            key = getattr(Qt.Key, f'Key_F{i}')
            result = window.get_key_name(key, "", 0)
            assert result == f"F{i}"

    def test_letter_keys(self, window):
        """Test letter key names"""
        result = window.get_key_name(Qt.Key.Key_M, "m", 0)
        assert result == "M"

        result = window.get_key_name(Qt.Key.Key_A, "a", 0)
        assert result == "A"

    def test_number_keys(self, window):
        """Test number key names"""
        result = window.get_key_name(Qt.Key.Key_1, "1", 0)
        assert result == "1"

    def test_media_keys(self, window):
        """Test media key names"""
        assert window.get_key_name(Qt.Key.Key_VolumeUp, "", 0) == "VOLUME UP"
        assert window.get_key_name(Qt.Key.Key_VolumeDown, "", 0) == "VOLUME DOWN"
        assert window.get_key_name(Qt.Key.Key_VolumeMute, "", 0) == "VOLUME MUTE"

    def test_unknown_key(self, window):
        """Test unknown key fallback"""
        result = window.get_key_name(0x9999, "", 0)
        assert result.startswith("KEY_0x")


class TestModifierKeys:
    """Test modifier key detection"""

    def test_left_shift(self, window):
        """Test left SHIFT key detection"""
        result = window.get_key_name(Qt.Key.Key_Shift, "", 0x32)
        assert result == "SHIFT (LEFT)"

    def test_right_shift(self, window):
        """Test right SHIFT key detection"""
        result = window.get_key_name(Qt.Key.Key_Shift, "", 0x3e)
        assert result == "SHIFT (RIGHT)"

    def test_left_ctrl(self, window):
        """Test left CTRL key detection"""
        result = window.get_key_name(Qt.Key.Key_Control, "", 0x25)
        assert result == "CTRL (LEFT)"

    def test_right_ctrl(self, window):
        """Test right CTRL key detection"""
        result = window.get_key_name(Qt.Key.Key_Control, "", 0x69)
        assert result == "CTRL (RIGHT)"

    def test_left_alt(self, window):
        """Test left ALT/OPTION key detection"""
        result = window.get_key_name(Qt.Key.Key_Alt, "", 0x40)
        assert result == "ALT/OPTION (LEFT)"

    def test_right_alt(self, window):
        """Test right ALT/OPTION key detection"""
        result = window.get_key_name(Qt.Key.Key_Alt, "", 0x6c)
        assert result == "ALT/OPTION (RIGHT)"

    def test_left_meta(self, window):
        """Test left META/SUPER key detection"""
        result = window.get_key_name(Qt.Key.Key_Meta, "", 0x85)
        assert result == "META/SUPER (LEFT)"

    def test_right_meta(self, window):
        """Test right META/SUPER key detection"""
        result = window.get_key_name(Qt.Key.Key_Meta, "", 0x86)
        assert result == "META/SUPER (RIGHT)"


class TestModifierNames:
    """Test modifier name conversion"""

    def test_no_modifiers(self, window):
        """Test no modifiers"""
        result = window.get_modifier_names(Qt.KeyboardModifier.NoModifier)
        assert result == ""

    def test_shift_modifier(self, window):
        """Test SHIFT modifier"""
        result = window.get_modifier_names(Qt.KeyboardModifier.ShiftModifier)
        assert result == "SHIFT"

    def test_ctrl_modifier(self, window):
        """Test CTRL modifier"""
        result = window.get_modifier_names(Qt.KeyboardModifier.ControlModifier)
        assert result == "CTRL"

    def test_alt_modifier(self, window):
        """Test ALT modifier"""
        result = window.get_modifier_names(Qt.KeyboardModifier.AltModifier)
        assert result == "ALT"

    def test_meta_modifier(self, window):
        """Test META modifier"""
        result = window.get_modifier_names(Qt.KeyboardModifier.MetaModifier)
        assert result == "META"

    def test_combined_modifiers(self, window):
        """Test combined modifiers"""
        modifiers = (Qt.KeyboardModifier.ControlModifier |
                    Qt.KeyboardModifier.ShiftModifier)
        result = window.get_modifier_names(modifiers)
        assert "SHIFT" in result
        assert "CTRL" in result


class TestEscapeDetection:
    """Test escape key detection for exit"""

    def test_single_escape_press(self, window):
        """Test single escape press doesn't exit"""
        window.handle_escape_press()
        assert len(window.escape_press_times) == 1

    def test_triple_escape_rapid(self, window):
        """Test triple rapid escape presses triggers exit"""
        with patch.object(window, 'exit_application') as mock_exit:
            # Simulate 3 rapid presses
            now = datetime.now()
            window.escape_press_times = [
                now,
                now + timedelta(milliseconds=100),
                now + timedelta(milliseconds=200)
            ]
            window.handle_escape_press()
            mock_exit.assert_called_once()

    def test_triple_escape_slow(self, window):
        """Test triple slow escape presses doesn't exit"""
        with patch.object(window, 'exit_application') as mock_exit:
            # Simulate 3 slow presses (more than 1 second apart)
            now = datetime.now()
            window.escape_press_times = [
                now - timedelta(seconds=2),
                now - timedelta(seconds=1.5),
                now
            ]
            window.handle_escape_press()
            mock_exit.assert_not_called()

    def test_escape_press_list_limit(self, window):
        """Test escape press times list is limited to 3"""
        for _ in range(5):
            window.handle_escape_press()
        assert len(window.escape_press_times) <= 3

    def test_escape_hold_timer_starts(self, window):
        """Test escape hold timer starts on press"""
        window.handle_escape_press()
        assert window.escape_hold_timer is not None
        assert window.escape_hold_start is not None

    def test_escape_release_stops_timer(self, window):
        """Test escape release stops hold timer"""
        window.handle_escape_press()
        window.handle_escape_release()
        assert window.escape_hold_timer is None
        assert window.escape_hold_start is None


class TestUIComponents:
    """Test UI component initialization"""

    def test_window_created(self, window):
        """Test window is created properly"""
        assert window is not None
        assert window.windowTitle() == "Keyboard Checker"

    def test_ui_elements_exist(self, window):
        """Test UI elements are created"""
        assert window.current_key_label is not None
        assert window.details_label is not None
        assert window.event_log is not None

    def test_focus_policy(self, window):
        """Test window has correct focus policy"""
        assert window.focusPolicy() == Qt.FocusPolicy.StrongFocus

    def test_event_log_readonly(self, window):
        """Test event log is read-only"""
        assert window.event_log.isReadOnly() is True

    def test_clear_log(self, window):
        """Test clear log functionality"""
        window.event_log.append("test entry")
        window.clear_log()
        assert window.event_log.toPlainText() == ""


class TestEventHandling:
    """Test keyboard event handling"""

    def test_handle_key_press_updates_display(self, window):
        """Test key press updates display"""
        # Create a mock key event
        event = Mock(spec=QKeyEvent)
        event.key.return_value = Qt.Key.Key_A
        event.text.return_value = "a"
        event.modifiers.return_value = Qt.KeyboardModifier.NoModifier
        event.nativeVirtualKey.return_value = 0x26

        window.handle_key_press(event)

        # Check that the label was updated
        assert window.current_key_label.text() == "A"

    def test_handle_key_press_with_modifier(self, window):
        """Test key press with modifier updates display"""
        event = Mock(spec=QKeyEvent)
        event.key.return_value = Qt.Key.Key_A
        event.text.return_value = "A"
        event.modifiers.return_value = Qt.KeyboardModifier.ShiftModifier
        event.nativeVirtualKey.return_value = 0x26

        window.handle_key_press(event)

        # Check that both modifier and key are shown
        display_text = window.current_key_label.text()
        assert "SHIFT" in display_text
        assert "A" in display_text

    def test_handle_key_press_logs_event(self, window):
        """Test key press is logged"""
        window.event_log.clear()

        event = Mock(spec=QKeyEvent)
        event.key.return_value = Qt.Key.Key_Space
        event.text.return_value = " "
        event.modifiers.return_value = Qt.KeyboardModifier.NoModifier
        event.nativeVirtualKey.return_value = 0x41

        window.handle_key_press(event)

        log_text = window.event_log.toPlainText()
        assert "PRESS" in log_text
        assert "SPACE" in log_text

    def test_escape_key_triggers_detection(self, window):
        """Test escape key triggers escape detection"""
        with patch.object(window, 'handle_escape_press') as mock_escape:
            event = Mock(spec=QKeyEvent)
            event.key.return_value = Qt.Key.Key_Escape
            event.text.return_value = ""
            event.modifiers.return_value = Qt.KeyboardModifier.NoModifier
            event.nativeVirtualKey.return_value = 0x9

            window.handle_key_press(event)
            mock_escape.assert_called_once()


class TestExitApplication:
    """Test exit application functionality"""

    def test_exit_application_logs_message(self, window):
        """Test exit application logs exit message"""
        window.event_log.clear()

        with patch.object(window, 'close'):
            window.exit_application()
            log_text = window.event_log.toPlainText()
            assert "Exit condition detected" in log_text


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
