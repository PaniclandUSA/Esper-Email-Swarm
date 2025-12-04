"""
Tests for the 5-agent semantic swarm.
"""

import pytest
from esper_email_swarm.agents import (
    analyze_email_agents,
    analyze_urgency,
    analyze_importance,
    analyze_topic,
    analyze_tone,
    analyze_action,
)


class TestUrgencyAgent:
    """Test urgency detection"""
    
    def test_high_urgency_keywords(self):
        """Should detect high urgency from keywords"""
        text = "URGENT: This is CRITICAL and needs immediate action ASAP!"
        urgency, tension, gloss = analyze_urgency(text, {})
        
        assert urgency > 0.7
        assert "critical" in gloss.lower() or "urgent" in gloss.lower()
    
    def test_low_urgency(self):
        """Should detect low urgency in casual email"""
        text = "Just wanted to share this article I found interesting."
        urgency, tension, gloss = analyze_urgency(text, {})
        
        assert urgency < 0.3
        assert "low" in gloss.lower() or "flexible" in gloss.lower()
    
    def test_deadline_detection(self):
        """Should boost urgency when deadline present"""
        text = "Please send the report by Friday 3:00 PM."
        urgency, tension, gloss = analyze_urgency(text, {})
        
        # Deadline keywords + temporal pattern should boost urgency
        assert urgency > 0.4


class TestImportanceAgent:
    """Test importance domain detection"""
    
    def test_financial_domain(self):
        """Should detect financial importance"""
        text = "Invoice #123 for $5000 is due. Payment required for tax filing."
        importance, domain, gloss = analyze_importance(text, {})
        
        assert importance > 0.5
        assert domain == "financial"
        assert "financial" in gloss.lower()
    
    def test_health_domain(self):
        """Should detect health importance"""
        text = "Your medical test results are ready. Please call the doctor."
        importance, domain, gloss = analyze_importance(text, {})
        
        assert importance > 0.5
        assert domain == "health"
    
    def test_legal_domain(self):
        """Should detect legal importance"""
        text = "Contract review required. Legal compliance deadline approaching."
        importance, domain, gloss = analyze_importance(text, {})
        
        assert importance > 0.5
        assert domain == "legal"
    
    def test_career_domain(self):
        """Should detect career importance"""
        text = "Performance review scheduled. Promotion decision pending."
        importance, domain, gloss = analyze_importance(text, {})
        
        assert importance > 0.5
        assert domain == "career"
    
    def test_academic_domain(self):
        """Should detect academic importance"""
        text = "Research grant funding approved. Publication deadline next month."
        importance, domain, gloss = analyze_importance(text, {})
        
        assert importance > 0.5
        assert domain == "academic"
    
    def test_low_importance(self):
        """Should detect low importance in casual email"""
        text = "Hey, how are you doing? Just checking in."
        importance, domain, gloss = analyze_importance(text, {})
        
        assert importance < 0.3


class TestTopicAgent:
    """Test topic extraction"""
    
    def test_topic_from_domain(self):
        """Should extract topic from importance domain"""
        text = "Invoice payment due for tax filing."
        metadata = {'subject': 'Invoice Due'}
        
        topic, gloss = analyze_topic(text, metadata)
        
        assert topic == "financial"
        assert "financial" in gloss.lower()
    
    def test_topic_from_subject(self):
        """Should extract topic from subject line"""
        text = "Meeting details attached."
        metadata = {'subject': 'Q4 Planning Meeting Tomorrow'}
        
        topic, gloss = analyze_topic(text, metadata)
        
        # Should extract meaningful word from subject
        assert len(topic) >= 4  # At least 4 characters
        assert topic in gloss.lower()
    
    def test_fallback_to_general(self):
        """Should fallback to general for unclear emails"""
        text = "Hi."
        metadata = {'subject': 'Hi'}
        
        topic, gloss = analyze_topic(text, metadata)
        
        assert topic == "general"


class TestToneAgent:
    """Test tone and warmth detection"""
    
    def test_warm_friendly_tone(self):
        """Should detect warm, friendly communication"""
        text = "Thanks so much! I really appreciate your help. Hope you're doing well!"
        metadata = {'sender': 'friend@example.com'}
        
        warmth, tension, formality, gloss = analyze_tone(text, metadata)
        
        assert warmth > 0.5
        assert "warm" in gloss.lower()
    
    def test_tense_tone(self):
        """Should detect tension and conflict"""
        text = "I'm very disappointed and frustrated with this mistake. This is unacceptable."
        metadata = {'sender': 'boss@company.com'}
        
        warmth, tension, formality, gloss = analyze_tone(text, metadata)
        
        assert tension > 0.5
        assert "tense" in gloss.lower() or "tension" in gloss.lower()
    
    def test_formal_tone(self):
        """Should detect formal communication"""
        text = "Dear Sir or Madam, Please be advised that the contract has been executed. Respectfully yours,"
        metadata = {'sender': 'lawyer@law.com'}
        
        warmth, tension, formality, gloss = analyze_tone(text, metadata)
        
        assert formality > 0.6
        assert "formal" in gloss.lower()
    
    def test_personal_sender_boost(self):
        """Should boost warmth for family/friend senders"""
        text = "Hey, what's up?"
        metadata = {'sender': 'mom@family.com'}
        
        warmth, tension, formality, gloss = analyze_tone(text, metadata)
        
        # Should boost warmth for "mom" in sender
        assert warmth > 0.3


class TestActionAgent:
    """Test action recommendation"""
    
    def test_reply_action(self):
        """Should recommend reply when questions present"""
        text = "Can you let me know your availability for next week?"
        metadata = {}
        
        action, gloss = analyze_action(text, metadata, urgency=0.5, importance=0.5)
        
        assert "reply" in gloss.lower()
    
    def test_schedule_action(self):
        """Should recommend scheduling when meeting mentioned"""
        text = "Let's schedule a call to discuss. What time works for you?"
        metadata = {}
        
        action, gloss = analyze_action(text, metadata, urgency=0.5, importance=0.5)
        
        assert "schedule" in gloss.lower() or "meeting" in gloss.lower()
    
    def test_review_action(self):
        """Should recommend review when attachments mentioned"""
        text = "Please review the attached document and provide feedback."
        metadata = {}
        
        action, gloss = analyze_action(text, metadata, urgency=0.5, importance=0.5)
        
        assert "review" in gloss.lower()
    
    def test_fyi_action(self):
        """Should detect FYI/informational emails"""
        text = "FYI - Just wanted to let you know about this update."
        metadata = {}
        
        action, gloss = analyze_action(text, metadata, urgency=0.2, importance=0.2)
        
        assert "reference" in gloss.lower() or "read" in gloss.lower()


class TestAgentOrchestration:
    """Test the full 5-agent orchestration"""
    
    def test_all_agents_run(self):
        """All 5 agents should produce packets"""
        text = "Test email content"
        metadata = {
            'sender': 'test@example.com',
            'subject': 'Test Subject',
        }
        
        packets = analyze_email_agents(text, metadata)
        
        # Should have exactly 5 packets
        assert len(packets) == 5
        
        # Should have all expected agent roles
        expected_roles = {'urgency', 'importance', 'topic', 'tone', 'action'}
        assert set(packets.keys()) == expected_roles
    
    def test_packet_structure(self):
        """Each packet should have correct structure"""
        text = "Test email content"
        metadata = {'sender': 'test@example.com', 'subject': 'Test'}
        
        packets = analyze_email_agents(text, metadata)
        
        for role, packet in packets.items():
            # Check VSEPacket attributes
            assert packet.agent_role == role
            assert hasattr(packet, 'intent_spine')
            assert hasattr(packet, 'affect_lattice')
            assert hasattr(packet, 'semantic_motif')
            assert hasattr(packet, 'gloss')
            assert hasattr(packet, 'confidence')
            
            # Check that gloss is meaningful
            assert len(packet.gloss) > 0
            assert isinstance(packet.gloss, str)
            
            # Check confidence is in valid range
            assert 0.0 <= packet.confidence <= 1.0
    
    def test_deterministic_output(self):
        """Same input should produce same packets"""
        text = "Determinism test email"
        metadata = {'sender': 'test@example.com', 'subject': 'Test'}
        
        # Run twice
        packets1 = analyze_email_agents(text, metadata)
        packets2 = analyze_email_agents(text, metadata)
        
        # Should have identical agent roles
        assert set(packets1.keys()) == set(packets2.keys())
        
        # Glosses should be identical
        for role in packets1.keys():
            assert packets1[role].gloss == packets2[role].gloss
            assert packets1[role].confidence == packets2[role].confidence


class TestEdgeCases:
    """Test edge cases and error handling"""
    
    def test_empty_text(self):
        """Should handle empty email text"""
        text = ""
        metadata = {}
        
        # Should not crash
        packets = analyze_email_agents(text, metadata)
        assert len(packets) == 5
    
    def test_very_long_text(self):
        """Should handle very long emails"""
        text = "word " * 10000  # 10,000 words
        metadata = {}
        
        # Should not crash or timeout
        packets = analyze_email_agents(text, metadata)
        assert len(packets) == 5
    
    def test_unicode_text(self):
        """Should handle Unicode characters"""
        text = "Hello 你好 Привет مرحبا 🎉"
        metadata = {'subject': '测试 Test テスト'}
        
        # Should not crash
        packets = analyze_email_agents(text, metadata)
        assert len(packets) == 5
    
    def test_special_characters(self):
        """Should handle special characters"""
        text = "Test with $pecial ch@r@cter$ & symbols!"
        metadata = {}
        
        # Should not crash
        packets = analyze_email_agents(text, metadata)
        assert len(packets) == 5


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
