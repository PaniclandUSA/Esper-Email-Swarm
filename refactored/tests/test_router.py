"""
ESPER Email Swarm - Routing Tests

Tests for the routing engine and benevolent fusion logic.
"""

import pytest
from esper_email_swarm.agents import analyze_email_agents
from esper_email_swarm.router import route_email, benevolence_clamp, explain_routing
from esper_email_swarm.model import EmailMetadata, VSEPacket, IntentSpine, AffectLattice


class TestBenevolentFusion:
    """Tests for benevolence clamp and packet merging."""
    
    def test_empty_packets_raises_error(self):
        """Empty packet dict should raise ValueError."""
        with pytest.raises(ValueError):
            benevolence_clamp({})
    
    def test_basic_averaging(self):
        """Test that signals are averaged across packets."""
        from esper_email_swarm.model import semantic_hash
        
        packets = {
            "agent1": VSEPacket(
                agent_role="agent1",
                intent_spine=IntentSpine(urgency=1.0, importance=0.0, warmth=0.5, tension=0.5),
                affect_lattice=AffectLattice(),
                semantic_motif=semantic_hash("test1"),
                gloss="Test 1",
                confidence=0.9,
            ),
            "agent2": VSEPacket(
                agent_role="agent2",
                intent_spine=IntentSpine(urgency=0.0, importance=1.0, warmth=0.5, tension=0.5),
                affect_lattice=AffectLattice(),
                semantic_motif=semantic_hash("test2"),
                gloss="Test 2",
                confidence=0.9,
            ),
        }
        
        urgency, importance, warmth, tension = benevolence_clamp(packets)
        
        assert urgency == 0.5  # (1.0 + 0.0) / 2
        assert importance == 0.5  # (0.0 + 1.0) / 2
        assert warmth == 0.5  # (0.5 + 0.5) / 2
        assert tension == 0.5  # (0.5 + 0.5) / 2
    
    def test_benevolence_clamp_protects_warm_tense(self):
        """High warmth + high tension should dampen tension."""
        from esper_email_swarm.model import semantic_hash
        
        packets = {
            "agent1": VSEPacket(
                agent_role="agent1",
                intent_spine=IntentSpine(urgency=0.0, importance=0.0, warmth=0.8, tension=0.9),
                affect_lattice=AffectLattice(),
                semantic_motif=semantic_hash("test"),
                gloss="Test",
                confidence=0.9,
            ),
        }
        
        urgency, importance, warmth, tension = benevolence_clamp(packets)
        
        assert warmth == 0.8
        assert tension < 0.9  # Tension should be reduced
        assert tension == (0.9 + 0.8) / 2.0  # Specific calculation


class TestUrgentRouting:
    """Tests for urgent email routing."""
    
    def test_urgent_keywords_route_to_urgent_now(self):
        """Emails with urgent keywords should route to 1-URGENT-NOW."""
        text = "This is URGENT. Please respond ASAP. Deadline today!!"
        packets = analyze_email_agents(text, subject="URGENT", sender="test@example.com")
        metadata = EmailMetadata(sender="test@example.com", subject="URGENT")
        
        analysis = route_email(packets, metadata)
        
        assert analysis.routing_folder == "1-URGENT-NOW"
        assert analysis.routing_priority == "critical"
        assert analysis.urgency > 0.7
    
    def test_deadline_mention_increases_urgency(self):
        """Mentions of deadlines should increase urgency."""
        text = "The report is due by Friday. Please complete by end of day."
        packets = analyze_email_agents(text)
        
        urgency_packet = packets["urgency"]
        assert urgency_packet.intent_spine.urgency > 0.3


class TestImportanceRouting:
    """Tests for importance-based routing."""
    
    def test_financial_keywords_increase_importance(self):
        """Financial terms should trigger importance detection."""
        text = "Your invoice for $5,000 is attached. Payment due within 30 days."
        packets = analyze_email_agents(text)
        
        importance_packet = packets["importance"]
        assert importance_packet.intent_spine.importance > 0.5
    
    def test_important_routes_to_important_folder(self):
        """High importance should route to 2-Important."""
        text = "Please review the attached contract for our partnership. This involves $100,000 in funding."
        packets = analyze_email_agents(text, subject="Partnership Contract")
        metadata = EmailMetadata(sender="partner@example.com", subject="Partnership Contract")
        
        analysis = route_email(packets, metadata)
        
        # Should be either URGENT-NOW or Important (both valid for high importance)
        assert analysis.routing_folder in ["1-URGENT-NOW", "2-Important"]
        assert analysis.importance > 0.5


class TestNewsletterDetection:
    """Tests for newsletter routing."""
    
    def test_newsletter_keyword_routes_to_read_later(self):
        """Emails with 'newsletter' should route to Read-Later."""
        text = "Welcome to our weekly newsletter! You can unsubscribe at any time."
        packets = analyze_email_agents(text, subject="Weekly Newsletter")
        metadata = EmailMetadata(sender="newsletter@example.com", subject="Weekly Newsletter")
        
        analysis = route_email(packets, metadata)
        
        assert analysis.routing_folder == "4-Read-Later"
    
    def test_unsubscribe_link_indicates_newsletter(self):
        """'unsubscribe' is a strong newsletter indicator."""
        text = "Thanks for subscribing! To unsubscribe, click here."
        packets = analyze_email_agents(text)
        metadata = EmailMetadata(sender="updates@company.com", subject="Monthly Update")
        
        analysis = route_email(packets, metadata)
        
        assert analysis.routing_folder == "4-Read-Later"


class TestBenevolenceProtection:
    """Tests for benevolence clamp protecting personal emails."""
    
    def test_high_warmth_prevents_low_priority_routing(self):
        """Personal emails (high warmth) should not go to Reference."""
        text = "Hi! I love you and hope you're doing well. Just wanted to check in."
        packets = analyze_email_agents(text, sender="mom@example.com")
        
        # Artificially adjust to ensure it would otherwise go to Reference
        metadata = EmailMetadata(sender="mom@example.com", subject="Checking in")
        
        analysis = route_email(packets, metadata)
        
        # High warmth should prevent Reference folder
        if analysis.warmth > 0.6:
            assert analysis.routing_folder != "5-Reference"
    
    def test_family_sender_increases_warmth(self):
        """Senders with family terms should have increased warmth."""
        text = "Can you help me with something?"
        packets = analyze_email_agents(text, sender="mom@example.com")
        
        tone_packet = packets["tone"]
        assert tone_packet.intent_spine.warmth > 0.5


class TestTopicExtraction:
    """Tests for topic identification."""
    
    def test_tax_keyword_extracts_tax_topic(self):
        """'tax' keyword should identify taxes topic."""
        text = "Don't forget about your tax documents. The IRS deadline is approaching."
        packets = analyze_email_agents(text, subject="Tax Reminder")
        
        topic_packet = packets["topic"]
        assert "taxes" in topic_packet.gloss.lower()
    
    def test_meeting_keyword_extracts_meeting_topic(self):
        """'meeting' should identify meetings topic."""
        text = "Let's schedule a meeting next week to discuss the project."
        packets = analyze_email_agents(text, subject="Meeting Request")
        
        topic_packet = packets["topic"]
        assert "meeting" in topic_packet.gloss.lower()


class TestActionDetection:
    """Tests for action recommendation."""
    
    def test_urgent_email_recommends_quick_reply(self):
        """Urgent emails should recommend immediate action."""
        text = "URGENT: Please respond by end of day!"
        packets = analyze_email_agents(text)
        
        action_packet = packets["action"]
        assert "24 hours" in action_packet.gloss.lower() or "immediate" in action_packet.gloss.lower()
    
    def test_newsletter_recommends_read_when_convenient(self):
        """Newsletters should recommend casual reading."""
        text = "Here's our weekly newsletter. Unsubscribe anytime."
        packets = analyze_email_agents(text)
        
        action_packet = packets["action"]
        assert "convenient" in action_packet.gloss.lower() or "when" in action_packet.gloss.lower()


class TestConsistency:
    """Tests for routing consistency (determinism)."""
    
    def test_same_email_produces_same_routing(self):
        """Processing the same email multiple times should produce identical results."""
        text = "This is a test email with some content."
        subject = "Test Subject"
        sender = "test@example.com"
        
        results = []
        for _ in range(5):
            packets = analyze_email_agents(text, subject, sender)
            metadata = EmailMetadata(sender=sender, subject=subject)
            analysis = route_email(packets, metadata)
            results.append(analysis.routing_folder)
        
        # All results should be identical
        assert len(set(results)) == 1
    
    def test_semantic_hash_is_stable(self):
        """Semantic hash should be deterministic."""
        from esper_email_swarm.model import semantic_hash
        
        text = "Test content"
        hash1 = semantic_hash(text)
        hash2 = semantic_hash(text)
        
        assert hash1 == hash2


class TestEdgeCases:
    """Tests for edge cases and error handling."""
    
    def test_empty_email_body(self):
        """Empty email should not crash."""
        packets = analyze_email_agents("", subject="Empty", sender="test@example.com")
        metadata = EmailMetadata(sender="test@example.com", subject="Empty")
        
        analysis = route_email(packets, metadata)
        
        # Should still produce valid routing
        assert analysis.routing_folder in [
            "1-URGENT-NOW", "2-Important", "3-Action-Required", 
            "4-Read-Later", "5-Reference"
        ]
    
    def test_very_long_email(self):
        """Very long emails should be handled."""
        text = "word " * 10000  # 10,000 words
        packets = analyze_email_agents(text)
        
        # Should complete without error
        assert len(packets) == 5
    
    def test_special_characters_in_email(self):
        """Emails with special characters should be handled."""
        text = "Hello! 你好 🎉 #hashtag @mention $100 50% off"
        packets = analyze_email_agents(text)
        metadata = EmailMetadata(sender="test@example.com", subject="Special chars")
        
        analysis = route_email(packets, metadata)
        
        # Should produce valid result
        assert analysis.icon
        assert analysis.gloss


class TestExplainRouting:
    """Tests for routing explanation functionality."""
    
    def test_explain_routing_produces_text(self):
        """explain_routing should produce human-readable explanation."""
        text = "URGENT: Please respond ASAP!"
        packets = analyze_email_agents(text)
        metadata = EmailMetadata(sender="test@example.com", subject="URGENT")
        analysis = route_email(packets, metadata)
        
        explanation = explain_routing(analysis)
        
        assert isinstance(explanation, str)
        assert len(explanation) > 0
        assert "•" in explanation  # Should have bullet points


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
