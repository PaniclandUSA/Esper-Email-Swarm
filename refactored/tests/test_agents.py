"""
ESPER Email Swarm - Agent Tests

Tests for individual semantic agents.
"""

import pytest
from esper_email_swarm.agents import (
    analyze_email_agents,
    _analyze_urgency,
    _analyze_importance,
    _analyze_topic,
    _analyze_tone,
    _analyze_action,
)


class TestUrgencyAgent:
    """Tests for urgency detection agent."""
    
    def test_urgent_keyword_detection(self):
        """Should detect 'urgent' keyword."""
        score, gloss = _analyze_urgency("This is urgent!")
        assert score > 0.2
        assert "urgent" in gloss.lower() or "pressure" in gloss.lower()
    
    def test_asap_detection(self):
        """Should detect 'ASAP' keyword."""
        score, gloss = _analyze_urgency("Please respond ASAP")
        assert score > 0.2
    
    def test_deadline_detection(self):
        """Should detect deadline mentions."""
        score, gloss = _analyze_urgency("The deadline is tomorrow")
        assert score > 0.2
    
    def test_multiple_urgency_signals(self):
        """Multiple urgency signals should compound."""
        score, gloss = _analyze_urgency("URGENT!! Please respond ASAP. Deadline today!")
        assert score > 0.7
        assert "critical" in gloss.lower() or "immediate" in gloss.lower()
    
    def test_no_urgency(self):
        """Low urgency email should score near zero."""
        score, gloss = _analyze_urgency("Just wanted to say hello and see how you're doing")
        assert score < 0.3
        assert "low" in gloss.lower() or "flexible" in gloss.lower()


class TestImportanceAgent:
    """Tests for importance detection agent."""
    
    def test_financial_importance(self):
        """Should detect financial terms."""
        score, gloss = _analyze_importance("The invoice is $5,000. Payment due.")
        assert score > 0.3
        assert "financial" in gloss.lower()
    
    def test_health_importance(self):
        """Should detect health-related content."""
        score, gloss = _analyze_importance("Your medical appointment is scheduled. Insurance approved.")
        assert score > 0.3
        assert "health" in gloss.lower()
    
    def test_legal_importance(self):
        """Should detect legal terms."""
        score, gloss = _analyze_importance("Please review and sign the contract. Legal compliance required.")
        assert score > 0.3
        assert "legal" in gloss.lower()
    
    def test_career_importance(self):
        """Should detect career-related content."""
        score, gloss = _analyze_importance("We'd like to offer you a promotion. Salary increase included.")
        assert score > 0.3
        assert "career" in gloss.lower()
    
    def test_low_importance(self):
        """Generic content should score low."""
        score, gloss = _analyze_importance("Just checking in to say hello!")
        assert score < 0.3


class TestTopicAgent:
    """Tests for topic extraction agent."""
    
    def test_tax_topic(self):
        """Should identify tax-related topics."""
        topic, gloss = _analyze_topic("Remember to file your taxes", "Tax Reminder")
        assert topic == "taxes"
        assert "taxes" in gloss
    
    def test_billing_topic(self):
        """Should identify billing topics."""
        topic, gloss = _analyze_topic("Your invoice is attached. Payment due.", "Invoice #1234")
        assert topic == "billing"
    
    def test_meeting_topic(self):
        """Should identify meeting topics."""
        topic, gloss = _analyze_topic("Let's schedule a meeting next week", "Meeting Request")
        assert topic == "meetings"
    
    def test_newsletter_topic(self):
        """Should identify newsletters."""
        topic, gloss = _analyze_topic("Welcome to our monthly newsletter!", "Newsletter")
        assert topic == "newsletter"
    
    def test_subject_priority(self):
        """Should prioritize subject line for topic extraction."""
        topic, gloss = _analyze_topic(
            "Some generic body text here",
            "Important Research Findings"
        )
        assert topic in ["research", "important", "findings"]


class TestToneAgent:
    """Tests for tone and warmth detection agent."""
    
    def test_warm_tone_detection(self):
        """Should detect warm, friendly tone."""
        warmth, tension, gloss = _analyze_tone("Thank you so much! I really appreciate your help. Love it!")
        assert warmth > 0.5
        assert "warm" in gloss.lower() or "friend" in gloss.lower()
    
    def test_tension_detection(self):
        """Should detect tense, problematic tone."""
        warmth, tension, gloss = _analyze_tone("I'm sorry but there's a problem. This is concerning. Disappointed.")
        assert tension > 0.3
        assert "tense" in gloss.lower() or "neutral" in gloss.lower()
    
    def test_family_sender_increases_warmth(self):
        """Family senders should boost warmth."""
        warmth1, _, _ = _analyze_tone("Can you help?", "random@example.com")
        warmth2, _, _ = _analyze_tone("Can you help?", "mom@example.com")
        assert warmth2 > warmth1
    
    def test_neutral_tone(self):
        """Neutral email should score middle range."""
        warmth, tension, gloss = _analyze_tone("Please find the attached document.")
        assert warmth < 0.5
        assert tension < 0.5
        assert "neutral" in gloss.lower() or "formal" in gloss.lower()


class TestActionAgent:
    """Tests for action recommendation agent."""
    
    def test_urgent_action(self):
        """Urgent emails should recommend immediate action."""
        action = _analyze_action(urgency=0.9, importance=0.5, warmth=0.3, text="urgent asap")
        assert "24 hours" in action.lower() or "immediate" in action.lower()
    
    def test_important_action(self):
        """Important emails should recommend timely action."""
        action = _analyze_action(urgency=0.2, importance=0.8, warmth=0.3, text="contract review")
        assert "week" in action.lower() or "days" in action.lower()
    
    def test_newsletter_action(self):
        """Newsletters should recommend casual reading."""
        action = _analyze_action(urgency=0.1, importance=0.1, warmth=0.0, text="newsletter unsubscribe")
        assert "convenient" in action.lower() or "time" in action.lower()
    
    def test_warm_personal_action(self):
        """Personal emails should recommend convenient response."""
        action = _analyze_action(urgency=0.2, importance=0.2, warmth=0.8, text="just checking in")
        assert "convenient" in action.lower()


class TestAgentIntegration:
    """Tests for full agent swarm integration."""
    
    def test_all_agents_produce_packets(self):
        """All 5 agents should produce packets."""
        packets = analyze_email_agents("Test email content")
        
        assert len(packets) == 5
        assert "urgency" in packets
        assert "importance" in packets
        assert "topic" in packets
        assert "tone" in packets
        assert "action" in packets
    
    def test_packets_have_required_fields(self):
        """All packets should have required VSE fields."""
        packets = analyze_email_agents("Test email content")
        
        for role, packet in packets.items():
            assert packet.agent_role == role
            assert packet.intent_spine is not None
            assert packet.affect_lattice is not None
            assert packet.semantic_motif is not None
            assert packet.gloss is not None
            assert 0.0 <= packet.confidence <= 1.0
    
    def test_packets_are_deterministic(self):
        """Same input should produce identical packets."""
        text = "Test email with specific content"
        subject = "Test Subject"
        sender = "test@example.com"
        
        packets1 = analyze_email_agents(text, subject, sender)
        packets2 = analyze_email_agents(text, subject, sender)
        
        # Check that urgency scores are identical
        assert packets1["urgency"].intent_spine.urgency == packets2["urgency"].intent_spine.urgency
        
        # Check that semantic motifs are identical
        assert packets1["urgency"].semantic_motif == packets2["urgency"].semantic_motif
    
    def test_subject_and_sender_used(self):
        """Subject and sender should influence analysis."""
        # Without subject/sender
        packets1 = analyze_email_agents("Generic text")
        
        # With urgent subject
        packets2 = analyze_email_agents("Generic text", subject="URGENT: Read Now!")
        
        # Urgency should be different
        assert packets2["urgency"].intent_spine.urgency > packets1["urgency"].intent_spine.urgency
    
    def test_real_world_urgent_email(self):
        """Real-world urgent email example."""
        text = """
        Hi,
        
        The tax documents are due by Friday. I need you to review and sign 
        the forms ASAP. This is urgent - penalties apply if we miss the deadline.
        
        Thanks,
        Mom
        """
        
        packets = analyze_email_agents(text, subject="URGENT - Taxes", sender="mom@example.com")
        
        assert packets["urgency"].intent_spine.urgency > 0.5
        assert packets["tone"].intent_spine.warmth > 0.3  # Family sender
        assert "tax" in packets["topic"].gloss.lower()
    
    def test_real_world_newsletter(self):
        """Real-world newsletter example."""
        text = """
        Welcome to our weekly AI research digest!
        
        This week's highlights:
        - New GPT model released
        - Breakthrough in computer vision
        
        Unsubscribe | Update preferences
        """
        
        packets = analyze_email_agents(
            text,
            subject="AI Research Digest - Week 49",
            sender="newsletter@research.com"
        )
        
        assert packets["urgency"].intent_spine.urgency < 0.3
        assert "newsletter" in packets["topic"].gloss.lower()
        assert "convenient" in packets["action"].gloss.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
