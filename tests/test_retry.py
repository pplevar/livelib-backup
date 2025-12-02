"""Tests for retry decorator with exponential backoff."""

import pytest
import time
from unittest.mock import Mock, patch
from Helpers.retry import retry


class TestRetryDecorator:
    """Test retry decorator functionality."""

    def test_successful_execution_no_retry(self):
        """Test that successful function executes without retry."""
        mock_func = Mock(return_value="success")
        decorated = retry(max_attempts=3)(mock_func)

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 1

    def test_retry_after_single_failure(self):
        """Test retry after single failure."""
        mock_func = Mock(side_effect=[Exception("fail"), "success"], __name__="test_func")
        decorated = retry(max_attempts=3, delay=0.1)(mock_func)

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 2

    def test_retry_after_multiple_failures(self):
        """Test retry after multiple failures."""
        mock_func = Mock(
            side_effect=[
                Exception("fail1"),
                Exception("fail2"),
                "success"
            ],
            __name__="test_func"
        )
        decorated = retry(max_attempts=3, delay=0.1)(mock_func)

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 3

    def test_exhausts_max_attempts(self):
        """Test that max attempts is exhausted and exception is raised."""
        mock_func = Mock(side_effect=Exception("always fails"), __name__="test_func")
        decorated = retry(max_attempts=3, delay=0.1)(mock_func)

        with pytest.raises(Exception, match="always fails"):
            decorated()

        assert mock_func.call_count == 3

    def test_exponential_backoff_timing(self):
        """Test that exponential backoff works correctly."""
        call_times = []

        def failing_func():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise Exception("fail")
            return "success"

        decorated = retry(max_attempts=3, delay=0.1, backoff=2.0)(failing_func)
        start_time = time.time()
        result = decorated()

        assert result == "success"
        assert len(call_times) == 3

        # Check delays: first retry ~0.1s, second retry ~0.2s
        if len(call_times) >= 2:
            first_delay = call_times[1] - call_times[0]
            assert 0.08 <= first_delay <= 0.15  # Allow some timing variance

        if len(call_times) >= 3:
            second_delay = call_times[2] - call_times[1]
            assert 0.15 <= second_delay <= 0.30  # ~0.2s with variance

    def test_specific_exception_handling(self):
        """Test that only specified exceptions trigger retry."""
        class CustomError(Exception):
            pass

        class OtherError(Exception):
            pass

        mock_func = Mock(side_effect=OtherError("wrong error"), __name__="test_func")
        decorated = retry(max_attempts=3, delay=0.1, exceptions=(CustomError,))(mock_func)

        # Should raise immediately without retry
        with pytest.raises(OtherError, match="wrong error"):
            decorated()

        assert mock_func.call_count == 1

    def test_multiple_exception_types(self):
        """Test retry with multiple exception types."""
        class ErrorA(Exception):
            pass

        class ErrorB(Exception):
            pass

        mock_func = Mock(
            side_effect=[
                ErrorA("error a"),
                ErrorB("error b"),
                "success"
            ],
            __name__="test_func"
        )
        decorated = retry(max_attempts=3, delay=0.1, exceptions=(ErrorA, ErrorB))(mock_func)

        result = decorated()

        assert result == "success"
        assert mock_func.call_count == 3

    def test_preserves_function_name(self):
        """Test that decorator preserves original function name."""
        def original_func():
            return "test"

        decorated = retry(max_attempts=3)(original_func)

        assert decorated.__name__ == "original_func"

    def test_preserves_function_docstring(self):
        """Test that decorator preserves original function docstring."""
        def original_func():
            """Original docstring."""
            return "test"

        decorated = retry(max_attempts=3)(original_func)

        assert decorated.__doc__ == "Original docstring."

    def test_passes_arguments_to_function(self):
        """Test that arguments are passed correctly to decorated function."""
        mock_func = Mock(return_value="success")
        decorated = retry(max_attempts=3)(mock_func)

        result = decorated("arg1", "arg2", key="value")

        assert result == "success"
        mock_func.assert_called_once_with("arg1", "arg2", key="value")

    def test_zero_delay(self):
        """Test retry with zero delay."""
        mock_func = Mock(side_effect=[Exception("fail"), "success"], __name__="test_func")
        decorated = retry(max_attempts=3, delay=0.0)(mock_func)

        start_time = time.time()
        result = decorated()
        elapsed = time.time() - start_time

        assert result == "success"
        assert elapsed < 0.1  # Should be nearly instant

    def test_large_backoff_factor(self):
        """Test retry with large backoff factor."""
        call_times = []

        def failing_func():
            call_times.append(time.time())
            if len(call_times) < 3:
                raise Exception("fail")
            return "success"

        decorated = retry(max_attempts=3, delay=0.05, backoff=4.0)(failing_func)
        result = decorated()

        assert result == "success"
        assert len(call_times) == 3

        if len(call_times) >= 3:
            second_delay = call_times[2] - call_times[1]
            # Second delay should be ~0.2s (0.05 * 4.0)
            assert 0.15 <= second_delay <= 0.30

    @patch('Helpers.retry.logger')
    def test_logs_retry_attempts(self, mock_logger):
        """Test that retry attempts are logged."""
        mock_func = Mock(side_effect=[Exception("fail"), "success"], __name__="test_func")
        decorated = retry(max_attempts=3, delay=0.01)(mock_func)

        result = decorated()

        assert result == "success"
        # Should log warning for failed attempt
        assert mock_logger.warning.called

    @patch('Helpers.retry.logger')
    def test_logs_final_failure(self, mock_logger):
        """Test that final failure is logged as error."""
        mock_func = Mock(side_effect=Exception("always fails"), __name__="test_func")
        decorated = retry(max_attempts=2, delay=0.01)(mock_func)

        with pytest.raises(Exception):
            decorated()

        # Should log error for exhausted attempts
        assert mock_logger.error.called

    def test_single_attempt_no_backoff(self):
        """Test that single attempt doesn't involve backoff logic."""
        mock_func = Mock(side_effect=Exception("fail"), __name__="test_func")
        decorated = retry(max_attempts=1, delay=1.0)(mock_func)

        start_time = time.time()
        with pytest.raises(Exception, match="fail"):
            decorated()
        elapsed = time.time() - start_time

        assert elapsed < 0.5  # Should fail immediately without delay
        assert mock_func.call_count == 1

    def test_return_value_types(self):
        """Test that different return value types work correctly."""
        # Test None return
        mock_func = Mock(return_value=None)
        decorated = retry(max_attempts=3)(mock_func)
        assert decorated() is None

        # Test list return
        mock_func = Mock(return_value=[1, 2, 3])
        decorated = retry(max_attempts=3)(mock_func)
        assert decorated() == [1, 2, 3]

        # Test dict return
        mock_func = Mock(return_value={"key": "value"})
        decorated = retry(max_attempts=3)(mock_func)
        assert decorated() == {"key": "value"}

    def test_with_class_method(self):
        """Test retry decorator works with class methods."""
        class TestClass:
            def __init__(self):
                self.attempt_count = 0

            @retry(max_attempts=3, delay=0.01)
            def failing_method(self):
                self.attempt_count += 1
                if self.attempt_count < 2:
                    raise Exception("fail")
                return "success"

        obj = TestClass()
        result = obj.failing_method()

        assert result == "success"
        assert obj.attempt_count == 2
