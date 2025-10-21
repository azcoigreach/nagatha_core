"""
Tests for the AI module.
"""

from nagatha_core.ai import summarize_text, analyze_sentiment, heartbeat


def test_summarize_short_text():
    """Test summarizing short text."""
    text = "Hello world"
    result = summarize_text(text, max_length=50)
    
    assert result == text


def test_summarize_long_text():
    """Test summarizing long text."""
    text = "A" * 200
    result = summarize_text(text, max_length=100)
    
    assert len(result) <= 103  # 100 + "..."
    assert result.endswith("...")


def test_summarize_custom_length():
    """Test summarize with custom length."""
    text = "This is a test text for summarization"
    result = summarize_text(text, max_length=10)
    
    assert len(result) <= 13  # 10 + "..."


def test_analyze_sentiment():
    """Test sentiment analysis."""
    result = analyze_sentiment("I love this!")
    
    assert isinstance(result, dict)
    assert "sentiment" in result
    assert "confidence" in result
    assert result["text"] == "I love this!"


def test_analyze_sentiment_structure():
    """Test sentiment analysis response structure."""
    result = analyze_sentiment("Test")
    
    assert result["sentiment"] in ["positive", "negative", "neutral"]
    assert 0 <= result["confidence"] <= 1


def test_ai_heartbeat():
    """Test AI module heartbeat."""
    status = heartbeat()
    
    assert isinstance(status, dict)
    assert status["status"] == "healthy"
    assert status["module"] == "ai"
    assert "version" in status
