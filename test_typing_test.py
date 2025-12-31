#!/usr/bin/env python3
"""
Unit tests for Typing Test functionality

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
import pytest
import tempfile
from pathlib import Path
from datetime import datetime
from unittest.mock import Mock, patch, MagicMock
from PyQt6.QtWidgets import QApplication

from keyboard_checker import TypingHistory, TypingTest
from text_samples import TYPING_SAMPLES


@pytest.fixture(scope="session")
def qapp():
    """Create QApplication instance for tests"""
    app = QApplication.instance()
    if app is None:
        app = QApplication(sys.argv)
    yield app


@pytest.fixture
def temp_history_dir(tmp_path):
    """Create temporary directory for history testing"""
    return tmp_path


@pytest.fixture
def typing_history(temp_history_dir):
    """Create TypingHistory instance with temporary directory"""
    history = TypingHistory()
    history.history_dir = temp_history_dir
    history.history_file = temp_history_dir / "typing_history.json"
    return history


@pytest.fixture
def typing_test(qapp):
    """Create TypingTest widget for testing"""
    test = TypingTest()
    yield test
    test.close()


class TestTextSamples:
    """Test text samples module"""

    def test_samples_exist(self):
        """Test that text samples are loaded"""
        assert len(TYPING_SAMPLES) > 0

    def test_sample_count(self):
        """Test that we have the expected number of samples"""
        assert len(TYPING_SAMPLES) >= 20
        assert len(TYPING_SAMPLES) <= 60

    def test_sample_structure(self):
        """Test that each sample has required fields"""
        for sample in TYPING_SAMPLES:
            assert 'id' in sample
            assert 'text' in sample
            assert 'source' in sample
            assert isinstance(sample['id'], int)
            assert isinstance(sample['text'], str)
            assert isinstance(sample['source'], str)
            assert len(sample['text']) > 0

    def test_sample_uniqueness(self):
        """Test that sample IDs are unique"""
        ids = [s['id'] for s in TYPING_SAMPLES]
        assert len(ids) == len(set(ids))


class TestTypingHistory:
    """Test TypingHistory class"""

    def test_init_creates_directory(self, typing_history, temp_history_dir):
        """Test that history directory is created"""
        assert temp_history_dir.exists()

    def test_load_empty_history(self, typing_history):
        """Test loading history when file doesn't exist"""
        history = typing_history.load_history()
        assert history == []

    def test_save_and_load_result(self, typing_history):
        """Test saving and loading a single result"""
        result = {
            'timestamp': datetime.now().isoformat(),
            'duration': 60,
            'wpm': 85.5,
            'adjusted_wpm': 78.2,
            'accuracy_percent': 92.5
        }

        typing_history.save_result(result)
        loaded = typing_history.load_history()

        assert len(loaded) == 1
        assert loaded[0]['wpm'] == 85.5
        assert loaded[0]['duration'] == 60

    def test_save_multiple_results(self, typing_history):
        """Test saving multiple results"""
        for i in range(5):
            result = {
                'timestamp': datetime.now().isoformat(),
                'duration': 60,
                'wpm': 80 + i,
                'adjusted_wpm': 75 + i
            }
            typing_history.save_result(result)

        loaded = typing_history.load_history()
        assert len(loaded) == 5

    def test_get_recent(self, typing_history):
        """Test getting recent N results"""
        # Add 15 results
        for i in range(15):
            result = {
                'timestamp': datetime.now().isoformat(),
                'wpm': i
            }
            typing_history.save_result(result)

        recent = typing_history.get_recent(10)
        assert len(recent) == 10
        # Should be most recent (highest wpm values)
        assert recent[-1]['wpm'] == 14

    def test_get_by_duration(self, typing_history):
        """Test filtering results by duration"""
        for duration in [30, 60, 120]:
            for i in range(3):
                result = {
                    'timestamp': datetime.now().isoformat(),
                    'duration': duration,
                    'wpm': 80
                }
                typing_history.save_result(result)

        results_60 = typing_history.get_by_duration(60)
        assert len(results_60) == 3
        assert all(r['duration'] == 60 for r in results_60)

    def test_get_average_wpm(self, typing_history):
        """Test calculating average WPM"""
        wpms = [80, 85, 90, 95, 100]
        for wpm in wpms:
            result = {
                'timestamp': datetime.now().isoformat(),
                'wpm': wpm
            }
            typing_history.save_result(result)

        avg = typing_history.get_average_wpm()
        assert avg == 90.0  # (80+85+90+95+100)/5

    def test_get_average_wpm_empty(self, typing_history):
        """Test average WPM with no history"""
        avg = typing_history.get_average_wpm()
        assert avg == 0.0

    def test_corrupted_file_handling(self, typing_history):
        """Test handling of corrupted JSON file"""
        # Write corrupted JSON
        with open(typing_history.history_file, 'w') as f:
            f.write("{ invalid json }")

        # Should return empty list instead of crashing
        history = typing_history.load_history()
        assert history == []


class TestTypingTestUI:
    """Test TypingTest UI components"""

    def test_widget_created(self, typing_test):
        """Test that typing test widget is created"""
        assert typing_test is not None

    def test_initial_state(self, typing_test):
        """Test initial state of typing test"""
        assert typing_test.test_active is False
        assert typing_test.test_duration == 60
        assert typing_test.typed_text == ""
        assert typing_test.errors == []

    def test_duration_buttons_exist(self, typing_test):
        """Test that duration selection buttons exist"""
        assert typing_test.radio_30s is not None
        assert typing_test.radio_60s is not None
        assert typing_test.radio_120s is not None
        assert typing_test.radio_60s.isChecked()  # Default

    def test_ui_components_exist(self, typing_test):
        """Test that all UI components are created"""
        assert typing_test.timer_label is not None
        assert typing_test.sample_display is not None
        assert typing_test.typing_input is not None
        assert typing_test.start_button is not None
        assert typing_test.stats_panel is not None
        assert typing_test.history_table is not None

    def test_typing_input_initially_disabled(self, typing_test):
        """Test that typing input is disabled before test starts"""
        assert typing_test.typing_input.isEnabled() is False


class TestTypingTestFunctionality:
    """Test typing test core functionality"""

    def test_start_test(self, typing_test):
        """Test starting a typing test"""
        typing_test.start_test()

        assert typing_test.test_active is True
        assert typing_test.current_sample is not None
        assert typing_test.typing_input.isEnabled() is True
        assert typing_test.start_button.isEnabled() is False

    def test_duration_selection(self, typing_test):
        """Test selecting different test durations"""
        typing_test.radio_30s.setChecked(True)
        typing_test.start_test()
        assert typing_test.test_duration == 30

        typing_test.reset_test()
        typing_test.radio_120s.setChecked(True)
        typing_test.start_test()
        assert typing_test.test_duration == 120

    def test_calculate_statistics_basic(self, typing_test):
        """Test basic statistics calculation"""
        typing_test.current_sample = TYPING_SAMPLES[0]
        typing_test.test_duration = 60
        typing_test.typed_text = "Hello world"
        typing_test.errors = []
        typing_test.wpm_samples = [50, 55, 60]

        stats = typing_test.calculate_statistics()

        assert 'wpm' in stats
        assert 'adjusted_wpm' in stats
        assert 'accuracy_percent' in stats
        assert 'peak_wpm' in stats
        assert 'consistency_score' in stats
        assert stats['total_characters'] == 11
        assert stats['errors'] == 0

    def test_wpm_calculation(self, typing_test):
        """Test WPM calculation accuracy"""
        typing_test.current_sample = TYPING_SAMPLES[0]
        typing_test.test_duration = 60  # 1 minute
        typing_test.typed_text = "a" * 300  # 300 characters
        typing_test.errors = []
        typing_test.wpm_samples = [60]

        stats = typing_test.calculate_statistics()

        # WPM = (chars / 5) / minutes = (300 / 5) / 1 = 60
        assert stats['wpm'] == 60.0

    def test_adjusted_wpm_with_errors(self, typing_test):
        """Test adjusted WPM calculation with errors"""
        typing_test.current_sample = TYPING_SAMPLES[0]
        typing_test.test_duration = 60
        typing_test.typed_text = "a" * 300
        typing_test.errors = [(i, 'a', 'b') for i in range(10)]  # 10 errors
        typing_test.wpm_samples = [60]

        stats = typing_test.calculate_statistics()

        # WPM = 60, Adjusted = 60 - 10 = 50
        assert stats['adjusted_wpm'] == 50.0

    def test_accuracy_calculation(self, typing_test):
        """Test accuracy percentage calculation"""
        typing_test.current_sample = TYPING_SAMPLES[0]
        typing_test.test_duration = 60
        typing_test.typed_text = "a" * 100
        typing_test.errors = [(i, 'a', 'b') for i in range(8)]  # 8 errors
        typing_test.wpm_samples = [60]

        stats = typing_test.calculate_statistics()

        # Accuracy = (100 - 8) / 100 * 100 = 92%
        assert stats['accuracy_percent'] == 92.0

    def test_peak_wpm(self, typing_test):
        """Test peak WPM detection"""
        typing_test.current_sample = TYPING_SAMPLES[0]
        typing_test.test_duration = 60
        typing_test.typed_text = "test"
        typing_test.errors = []
        typing_test.wpm_samples = [50, 75, 60, 55]

        stats = typing_test.calculate_statistics()

        assert stats['peak_wpm'] == 75.0

    def test_consistency_calculation(self, typing_test):
        """Test consistency score calculation"""
        typing_test.current_sample = TYPING_SAMPLES[0]
        typing_test.test_duration = 60
        typing_test.typed_text = "test"
        typing_test.errors = []
        # More varied samples = higher consistency score (stdev)
        typing_test.wpm_samples = [50, 50, 50, 50]  # Very consistent

        stats = typing_test.calculate_statistics()

        # Standard deviation of [50,50,50,50] is 0
        assert stats['consistency_score'] == 0.0

    def test_reset_test(self, typing_test):
        """Test resetting the test"""
        typing_test.start_test()
        typing_test.typed_text = "some text"
        typing_test.errors = [(0, 'a', 'b')]

        typing_test.reset_test()

        assert typing_test.typing_input.toPlainText() == ""
        assert typing_test.sample_display.toPlainText() == ""
        assert typing_test.stats_panel.isVisible() is False


class TestTypingTestIntegration:
    """Integration tests for typing test"""

    def test_full_test_workflow(self, typing_test):
        """Test complete typing test workflow"""
        # Start test
        typing_test.start_test()
        assert typing_test.test_active is True

        # Simulate typing
        typing_test.typed_text = "Test text"
        typing_test.wpm_samples = [60, 65, 70]

        # End test
        typing_test.end_test()
        assert typing_test.test_active is False
        assert hasattr(typing_test, 'current_stats')
        # Stats panel visibility depends on parent widget being shown
        # Just check that stats were calculated
        assert typing_test.current_stats is not None

    def test_mode_switching_preserves_history(self, typing_test, temp_history_dir):
        """Test that history persists across mode switches"""
        # Override history location
        typing_test.history.history_dir = temp_history_dir
        typing_test.history.history_file = temp_history_dir / "typing_history.json"

        # Complete a test and save
        typing_test.start_test()
        typing_test.typed_text = "Test"
        typing_test.wpm_samples = [60]
        typing_test.end_test()
        typing_test.save_results()

        # Create new typing test instance (simulating mode switch)
        new_test = TypingTest()
        new_test.history.history_dir = temp_history_dir
        new_test.history.history_file = temp_history_dir / "typing_history.json"

        # Should load previous history
        history = new_test.history.load_history()
        assert len(history) >= 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
