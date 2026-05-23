import pytest

from newsagent.security.input_sanitizer import InputSanitizer


class TestSanitize:
    def test_clean_text_unchanged(self) -> None:
        assert InputSanitizer.sanitize("Ini adalah teks bersih.") == "Ini adalah teks bersih."

    def test_removes_script_tags(self) -> None:
        result = InputSanitizer.sanitize("Teks <script>alert('xss')</script>bersih")
        assert "<script>" not in result
        assert result == "Teks bersih"

    def test_removes_case_variant_xss(self) -> None:
        result = InputSanitizer.sanitize("<ScRiPt>alert(1)</ScRiPt>")
        assert "ScRiPt" not in result

    def test_removes_nested_script(self) -> None:
        result = InputSanitizer.sanitize("<<script>alert(1)</script>")
        assert "<" not in result or "script" not in result.lower()

    def test_removes_javascript_protocol(self) -> None:
        result = InputSanitizer.sanitize("Link: javascript:alert(1)")
        assert "javascript:" not in result.lower()

    def test_removes_javascript_case_variant(self) -> None:
        result = InputSanitizer.sanitize("Link: JAVASCRIPT:alert(1)")
        assert "JAVASCRIPT:" not in result and "javascript:" not in result.lower()

    def test_removes_event_handlers(self) -> None:
        result = InputSanitizer.sanitize('<div onclick="evil()">Klik</div>')
        assert "onclick" not in result.lower()

    def test_removes_multiple_event_handlers(self) -> None:
        result = InputSanitizer.sanitize('<div onmouseover="x()" onload="y()">Teks</div>')
        assert "onmouseover" not in result.lower()
        assert "onload" not in result.lower()

    def test_strips_whitespace(self) -> None:
        assert InputSanitizer.sanitize("  hello  ") == "hello"

    def test_empty_string(self) -> None:
        assert InputSanitizer.sanitize("") == ""

    def test_only_whitespace(self) -> None:
        assert InputSanitizer.sanitize("   ") == ""

    def test_multiple_script_tags(self) -> None:
        result = InputSanitizer.sanitize("awal <script>a</script> tengah <script>b</script> akhir")
        assert "<script>" not in result
        assert result == "awal  tengah  akhir"


class TestValidateInputType:
    def test_valid_topic(self) -> None:
        result = InputSanitizer.validate_input_type({"input_type": "topic", "raw_input": "berita politik"})
        assert result["input_type"] == "topic"
        assert result["raw_input"] == "berita politik"

    def test_valid_draft(self) -> None:
        result = InputSanitizer.validate_input_type({"input_type": "draft", "raw_input": "draf artikel"})
        assert result["input_type"] == "draft"

    def test_valid_url(self) -> None:
        result = InputSanitizer.validate_input_type({"input_type": "url", "raw_input": "https://example.com"})
        assert result["input_type"] == "url"

    def test_invalid_type_defaults_to_topic(self) -> None:
        result = InputSanitizer.validate_input_type({"input_type": "pdf", "raw_input": "file"})
        assert result["input_type"] == "topic"

    def test_none_type_defaults_to_topic(self) -> None:
        result = InputSanitizer.validate_input_type({"input_type": None, "raw_input": "file"})
        assert result["input_type"] == "topic"

    def test_empty_raw_input_raises(self) -> None:
        with pytest.raises(ValueError, match="raw_input must be a non-empty string"):
            InputSanitizer.validate_input_type({"input_type": "topic", "raw_input": ""})

    def test_non_string_raw_input_raises(self) -> None:
        with pytest.raises(ValueError, match="raw_input must be a non-empty string"):
            InputSanitizer.validate_input_type({"input_type": "topic", "raw_input": 123})

    def test_sanitizes_raw_input(self) -> None:
        result = InputSanitizer.validate_input_type(
            {"input_type": "topic", "raw_input": "<script>alert('x')</script>teks"}
        )
        assert "<script>" not in result["raw_input"]
        assert result["raw_input"] == "teks"
