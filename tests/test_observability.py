"""
Tests for nagatha_core.observability package.

Tests correlation ID tracking and tracing utilities.
"""

import pytest
from nagatha_core.observability.tracing import (
    generate_correlation_id,
    get_correlation_id,
    set_correlation_id,
    clear_correlation_id,
    correlation_context,
    extract_correlation_id_from_headers,
    inject_correlation_id_into_headers,
)


class TestCorrelationId:
    """Test correlation ID utilities."""
    
    def test_generate_correlation_id(self):
        """Test generating correlation IDs."""
        corr_id1 = generate_correlation_id()
        corr_id2 = generate_correlation_id()
        
        assert corr_id1 != corr_id2
        assert len(corr_id1) > 0
        assert len(corr_id2) > 0
    
    def test_set_get_correlation_id(self):
        """Test setting and getting correlation ID."""
        test_id = "test-correlation-123"
        
        set_correlation_id(test_id)
        assert get_correlation_id() == test_id
        
        clear_correlation_id()
        assert get_correlation_id() is None
    
    def test_clear_correlation_id(self):
        """Test clearing correlation ID."""
        set_correlation_id("test-id")
        assert get_correlation_id() is not None
        
        clear_correlation_id()
        assert get_correlation_id() is None
    
    def test_correlation_context(self):
        """Test correlation context manager."""
        # Initially None
        assert get_correlation_id() is None
        
        # Inside context, ID is set
        with correlation_context("test-123") as corr_id:
            assert corr_id == "test-123"
            assert get_correlation_id() == "test-123"
        
        # After context, ID is cleared
        assert get_correlation_id() is None
    
    def test_correlation_context_auto_generate(self):
        """Test correlation context with auto-generated ID."""
        with correlation_context() as corr_id:
            assert corr_id is not None
            assert get_correlation_id() == corr_id
        
        assert get_correlation_id() is None
    
    def test_correlation_context_nested(self):
        """Test nested correlation contexts."""
        with correlation_context("outer") as outer_id:
            assert get_correlation_id() == "outer"
            
            with correlation_context("inner") as inner_id:
                assert get_correlation_id() == "inner"
            
            # Should restore outer
            assert get_correlation_id() == "outer"
        
        # Should be cleared
        assert get_correlation_id() is None


class TestHeaderHelpers:
    """Test header extraction/injection utilities."""
    
    def test_extract_correlation_id_from_headers(self):
        """Test extracting correlation ID from headers."""
        headers = {"X-Correlation-ID": "test-123"}
        corr_id = extract_correlation_id_from_headers(headers)
        assert corr_id == "test-123"
    
    def test_extract_from_request_id_header(self):
        """Test extracting from X-Request-ID header."""
        headers = {"X-Request-ID": "req-456"}
        corr_id = extract_correlation_id_from_headers(headers)
        assert corr_id == "req-456"
    
    def test_extract_from_trace_id_header(self):
        """Test extracting from X-Trace-ID header."""
        headers = {"X-Trace-ID": "trace-789"}
        corr_id = extract_correlation_id_from_headers(headers)
        assert corr_id == "trace-789"
    
    def test_extract_case_insensitive(self):
        """Test case-insensitive header extraction."""
        headers = {"x-correlation-id": "lower-case"}
        corr_id = extract_correlation_id_from_headers(headers)
        assert corr_id == "lower-case"
    
    def test_extract_not_found(self):
        """Test when correlation ID not in headers."""
        headers = {"Content-Type": "application/json"}
        corr_id = extract_correlation_id_from_headers(headers)
        assert corr_id is None
    
    def test_inject_correlation_id_into_headers(self):
        """Test injecting correlation ID into headers."""
        set_correlation_id("inject-test")
        
        headers = inject_correlation_id_into_headers({})
        assert headers["X-Correlation-ID"] == "inject-test"
        
        clear_correlation_id()
    
    def test_inject_with_existing_headers(self):
        """Test injecting without overwriting existing headers."""
        set_correlation_id("test-id")
        
        original = {"Content-Type": "application/json"}
        headers = inject_correlation_id_into_headers(original)
        
        assert headers["X-Correlation-ID"] == "test-id"
        assert headers["Content-Type"] == "application/json"
        assert "Content-Type" in original  # Original not modified
        
        clear_correlation_id()
    
    def test_inject_explicit_correlation_id(self):
        """Test injecting explicit correlation ID."""
        headers = inject_correlation_id_into_headers({}, correlation_id="explicit-123")
        assert headers["X-Correlation-ID"] == "explicit-123"
