"""Tests for input validation functions."""

import pytest
from pathlib import Path
from Helpers.validators import (
    validate_username,
    validate_file_path,
    validate_delay,
    validate_file_extension,
    validate_driver_type
)


class TestValidateUsername:
    """Test username validation."""

    def test_valid_username_alphanumeric(self):
        """Test valid alphanumeric username."""
        assert validate_username("user123") == "user123"

    def test_valid_username_with_dash(self):
        """Test valid username with dashes."""
        assert validate_username("test-user") == "test-user"

    def test_valid_username_with_underscore(self):
        """Test valid username with underscores."""
        assert validate_username("test_user") == "test_user"

    def test_valid_username_strips_whitespace(self):
        """Test that whitespace is stripped."""
        assert validate_username("  username  ") == "username"

    def test_empty_username_raises_error(self):
        """Test that empty username raises ValueError."""
        with pytest.raises(ValueError, match="Username cannot be empty"):
            validate_username("")

    def test_whitespace_only_username_raises_error(self):
        """Test that whitespace-only username raises ValueError."""
        with pytest.raises(ValueError, match="Username cannot be empty"):
            validate_username("   ")

    def test_username_with_special_chars_raises_error(self):
        """Test that special characters raise ValueError."""
        with pytest.raises(ValueError, match="Invalid username format"):
            validate_username("user@name")

    def test_username_with_spaces_raises_error(self):
        """Test that spaces raise ValueError."""
        with pytest.raises(ValueError, match="Invalid username format"):
            validate_username("user name")

    def test_username_with_sql_injection_raises_error(self):
        """Test that SQL injection attempts raise ValueError."""
        with pytest.raises(ValueError, match="Invalid username format"):
            validate_username("admin'; DROP TABLE users--")

    def test_username_with_unicode_raises_error(self):
        """Test that unicode characters raise ValueError."""
        with pytest.raises(ValueError, match="Invalid username format"):
            validate_username("пользователь")


class TestValidateFilePath:
    """Test file path validation."""

    def test_valid_relative_path(self, tmp_path):
        """Test valid relative path within current directory."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            test_file = tmp_path / "test.txt"
            test_file.touch()
            result = validate_file_path("test.txt", must_exist=True)
            assert Path(result).name == "test.txt"
        finally:
            os.chdir(original_cwd)

    def test_valid_path_does_not_exist(self, tmp_path):
        """Test valid path that doesn't exist when must_exist=False."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            result = validate_file_path("nonexistent.txt", must_exist=False)
            assert "nonexistent.txt" in result
        finally:
            os.chdir(original_cwd)

    def test_path_must_exist_raises_error(self, tmp_path):
        """Test that nonexistent path raises error when must_exist=True."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            with pytest.raises(FileNotFoundError, match="File not found"):
                validate_file_path("nonexistent.txt", must_exist=True)
        finally:
            os.chdir(original_cwd)

    def test_path_traversal_raises_error(self):
        """Test that path traversal attempts raise ValueError."""
        with pytest.raises(ValueError, match="File path must be within current directory"):
            validate_file_path("../../../etc/passwd")

    def test_absolute_path_outside_cwd_raises_error(self):
        """Test that absolute path outside current directory raises ValueError."""
        with pytest.raises(ValueError, match="File path must be within current directory"):
            validate_file_path("/etc/passwd")

    def test_symlink_traversal_raises_error(self, tmp_path):
        """Test that symlinks outside current directory raise ValueError."""
        import os
        original_cwd = os.getcwd()
        try:
            os.chdir(tmp_path)
            # Create symlink to parent directory
            symlink = tmp_path / "link"
            try:
                symlink.symlink_to(tmp_path.parent)
                with pytest.raises(ValueError, match="File path must be within current directory"):
                    validate_file_path("link/../../etc/passwd")
            except OSError:
                # Skip test if symlinks are not supported
                pytest.skip("Symlinks not supported on this system")
        finally:
            os.chdir(original_cwd)


class TestValidateDelay:
    """Test delay validation."""

    def test_valid_delay_range(self):
        """Test valid delay range."""
        min_delay, max_delay = validate_delay(5, 15)
        assert min_delay == 5
        assert max_delay == 15

    def test_equal_min_max_delay(self):
        """Test equal min and max delays."""
        min_delay, max_delay = validate_delay(10, 10)
        assert min_delay == 10
        assert max_delay == 10

    def test_zero_delays(self):
        """Test zero delays are valid."""
        min_delay, max_delay = validate_delay(0, 0)
        assert min_delay == 0
        assert max_delay == 0

    def test_negative_min_delay_raises_error(self):
        """Test that negative min_delay raises ValueError."""
        with pytest.raises(ValueError, match="Delays must be non-negative"):
            validate_delay(-1, 10)

    def test_negative_max_delay_raises_error(self):
        """Test that negative max_delay raises ValueError."""
        with pytest.raises(ValueError, match="Delays must be non-negative"):
            validate_delay(5, -1)

    def test_min_greater_than_max_raises_error(self):
        """Test that min > max raises ValueError."""
        with pytest.raises(ValueError, match="min_delay .* cannot exceed max_delay"):
            validate_delay(20, 10)

    def test_large_delay_values(self):
        """Test large delay values are accepted."""
        min_delay, max_delay = validate_delay(100, 500)
        assert min_delay == 100
        assert max_delay == 500


class TestValidateFileExtension:
    """Test file extension validation."""

    def test_valid_csv_extension(self):
        """Test valid CSV extension."""
        result = validate_file_extension("file.csv", ["csv", "xlsx"])
        assert result == "csv"

    def test_valid_xlsx_extension(self):
        """Test valid XLSX extension."""
        result = validate_file_extension("file.xlsx", ["csv", "xlsx"])
        assert result == "xlsx"

    def test_case_sensitive_extension(self):
        """Test that extension matching is case-sensitive."""
        with pytest.raises(ValueError, match="Unsupported file extension"):
            validate_file_extension("file.CSV", ["csv", "xlsx"])

    def test_invalid_extension_raises_error(self):
        """Test that invalid extension raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported file extension: txt"):
            validate_file_extension("file.txt", ["csv", "xlsx"])

    def test_no_extension_raises_error(self):
        """Test that file with no extension raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported file extension"):
            validate_file_extension("file", ["csv", "xlsx"])

    def test_multiple_dots_in_filename(self):
        """Test filename with multiple dots."""
        result = validate_file_extension("my.file.name.csv", ["csv", "xlsx"])
        assert result == "csv"


class TestValidateDriverType:
    """Test driver type validation."""

    def test_valid_requests_driver(self):
        """Test valid requests driver."""
        result = validate_driver_type("requests", ["requests", "selenium"])
        assert result == "requests"

    def test_valid_selenium_driver(self):
        """Test valid selenium driver."""
        result = validate_driver_type("selenium", ["requests", "selenium"])
        assert result == "selenium"

    def test_invalid_driver_raises_error(self):
        """Test that invalid driver raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported driver: chrome"):
            validate_driver_type("chrome", ["requests", "selenium"])

    def test_case_sensitive_driver(self):
        """Test that driver matching is case-sensitive."""
        with pytest.raises(ValueError, match="Unsupported driver: REQUESTS"):
            validate_driver_type("REQUESTS", ["requests", "selenium"])

    def test_empty_driver_raises_error(self):
        """Test that empty driver raises ValueError."""
        with pytest.raises(ValueError, match="Unsupported driver"):
            validate_driver_type("", ["requests", "selenium"])
