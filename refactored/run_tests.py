#!/usr/bin/env python3
"""
Simple test runner for ESPER Email Swarm

Runs tests without requiring pytest installation.
For full test suite with coverage, install pytest: pip install pytest pytest-cov
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent))

from esper_email_swarm.agents import analyze_email_agents
from esper_email_swarm.router import route_email, benevolence_clamp
from esper_email_swarm.model import EmailMetadata, semantic_hash


def test_urgent_email_routing():
    """Test that urgent emails route correctly."""
    print("Testing urgent email routing...", end=" ")
    
    text = "URGENT: This is very important! Please respond ASAP. Deadline today!!"
    packets = analyze_email_agents(text, subject="URGENT", sender="test@example.com")
    metadata = EmailMetadata(sender="test@example.com", subject="URGENT")
    
    analysis = route_email(packets, metadata)
    
    assert analysis.urgency > 0.5, f"Expected urgency > 0.5, got {analysis.urgency}"
    assert analysis.routing_folder in ["1-URGENT-NOW", "3-Action-Required"], \
        f"Expected urgent routing, got {analysis.routing_folder}"
    
    print("✓ PASSED")


def test_newsletter_detection():
    """Test that newsletters are detected."""
    print("Testing newsletter detection...", end=" ")
    
    text = "Welcome to our newsletter! You can unsubscribe at any time."
    packets = analyze_email_agents(text, subject="Weekly Newsletter")
    metadata = EmailMetadata(sender="newsletter@example.com", subject="Weekly Newsletter")
    
    analysis = route_email(packets, metadata)
    
    assert analysis.routing_folder == "4-Read-Later", \
        f"Expected Read-Later folder, got {analysis.routing_folder}"
    
    print("✓ PASSED")


def test_warmth_protection():
    """Test benevolence clamp protects warm emails."""
    print("Testing benevolence clamp...", end=" ")
    
    text = "Hi! I love you and hope you're doing well. Just checking in."
    packets = analyze_email_agents(text, sender="mom@example.com")
    metadata = EmailMetadata(sender="mom@example.com", subject="Checking in")
    
    analysis = route_email(packets, metadata)
    
    # High warmth should prevent Reference folder
    if analysis.warmth > 0.6:
        assert analysis.routing_folder != "5-Reference", \
            f"Benevolence clamp failed: warm email in Reference folder"
    
    print("✓ PASSED")


def test_consistency():
    """Test that routing is deterministic."""
    print("Testing routing consistency...", end=" ")
    
    text = "Test email with specific content"
    subject = "Test Subject"
    sender = "test@example.com"
    
    results = []
    for _ in range(5):
        packets = analyze_email_agents(text, subject, sender)
        metadata = EmailMetadata(sender=sender, subject=subject)
        analysis = route_email(packets, metadata)
        results.append(analysis.routing_folder)
    
    # All results should be identical
    assert len(set(results)) == 1, f"Inconsistent routing: {results}"
    
    print("✓ PASSED")


def test_semantic_hash_stability():
    """Test that semantic hashes are stable."""
    print("Testing semantic hash stability...", end=" ")
    
    text = "Test content for hashing"
    hash1 = semantic_hash(text)
    hash2 = semantic_hash(text)
    
    assert hash1 == hash2, "Semantic hash is not stable!"
    
    print("✓ PASSED")


def test_all_agents_present():
    """Test that all 5 agents produce packets."""
    print("Testing agent swarm completeness...", end=" ")
    
    packets = analyze_email_agents("Test email content")
    
    assert len(packets) == 5, f"Expected 5 agents, got {len(packets)}"
    assert "urgency" in packets
    assert "importance" in packets
    assert "topic" in packets
    assert "tone" in packets
    assert "action" in packets
    
    print("✓ PASSED")


def test_real_world_urgent_email():
    """Test with a real-world urgent email example."""
    print("Testing real-world urgent email...", end=" ")
    
    text = """
    Hi,
    
    The tax documents are due by Friday. I need you to review and sign 
    the forms ASAP. This is urgent - penalties apply if we miss the deadline.
    
    Thanks,
    Mom
    """
    
    packets = analyze_email_agents(text, subject="URGENT - Taxes", sender="mom@example.com")
    metadata = EmailMetadata(sender="mom@example.com", subject="URGENT - Taxes")
    
    analysis = route_email(packets, metadata)
    
    # Should detect urgency and tax topic
    assert analysis.urgency > 0.2, f"Expected some urgency, got {analysis.urgency}"
    assert "tax" in analysis.topic.lower(), f"Expected tax topic, got {analysis.topic}"
    
    print("✓ PASSED")


def test_importance_detection():
    """Test that importance is detected."""
    print("Testing importance detection...", end=" ")
    
    text = "Please review the contract. This involves $100,000 in funding."
    packets = analyze_email_agents(text)
    
    importance_packet = packets["importance"]
    assert importance_packet.intent_spine.importance > 0.3, \
        f"Expected importance > 0.3, got {importance_packet.intent_spine.importance}"
    
    print("✓ PASSED")


def run_tests():
    """Run all tests."""
    print("=" * 70)
    print("ESPER Email Swarm - Test Suite")
    print("=" * 70)
    print()
    
    tests = [
        test_urgent_email_routing,
        test_newsletter_detection,
        test_warmth_protection,
        test_consistency,
        test_semantic_hash_stability,
        test_all_agents_present,
        test_real_world_urgent_email,
        test_importance_detection,
    ]
    
    passed = 0
    failed = 0
    
    for test in tests:
        try:
            test()
            passed += 1
        except AssertionError as e:
            print(f"✗ FAILED: {e}")
            failed += 1
        except Exception as e:
            print(f"✗ ERROR: {e}")
            failed += 1
    
    print()
    print("=" * 70)
    print(f"Results: {passed} passed, {failed} failed out of {len(tests)} total")
    print("=" * 70)
    
    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(run_tests())
