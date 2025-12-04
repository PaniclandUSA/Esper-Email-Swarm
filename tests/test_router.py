"""
Tests for routing logic and benevolent fusion.
"""

import pytest
from esper_email_swarm.agents import analyze_email_agents
from esper_email_swarm.router import route_email, benevolence_clamp
from esper_email_swarm.model import EmailMetadata, VSEPacket, IntentSpine, AffectLattice


class TestBenevolentFusion:
    """Test benevolence clamp and packet fusion"""
    
    def test_empty_packets_raises_error(self):
        """Should raise error when no packets provided"""
        with pytest.raises(ValueError, match="empty packet"):
            benevolence_clamp({})
    
    def test_single_packet_fusion(self):
        """Should handle single packet correctly"""
        from esper_email_swarm.model import semantic_hash
        
        packet = VSEPacket(
            agent_role="test",
            intent_spine=IntentSpine(
                urgency=0.8,
                importance=0.6,
                warmth=0.5,
                tension=0.3,
                confidence=0.9,
            ),
            affect_lattice=AffectLattice(),
            semantic_motif=semantic_hash("test"),
            gloss="Test packet",
            confidence=0.9,
        )
        
        urgency, importance, warmth, tension = benevolence_clamp({"test": packet})
        
        assert urgency == 0.8
        assert importance == 0.6
        assert warmth == 0.5
        assert tension == 0.3
    
    def test_benevolence_clamp_activates(self):
        """Should soften tension when warmth is high"""
        from esper_email_swarm.model import semantic_hash
        
        packet = VSEPacket(
            agent_role="test",
            intent_spine=IntentSpine(
                urgency=0.5,
                importance=0.5,
                warmth=0.8,  # High warmth
                tension=0.9,  # High tension
                confidence=0.9,
            ),
            affect_lattice=AffectLattice(),
            semantic_motif=semantic_hash("test"),
            gloss="Test packet",
            confidence=0.9,
        )
        
        urgency, importance, warmth, tension = benevolence_clamp({"test": packet})
        
        # Tension should be softened by warmth
        assert tension < 0.9
        assert tension == (0.9 + 0.8) / 2.0


class TestUrgentRouting:
    """Test routing of urgent emails"""
    
    def test_urgent_personal_email(self):
        """Should route urgent family email correctly"""
        text = """
        Hi John,
        
        URGENT - The tax documents are due by Friday! Please send them ASAP.
        This is critical - we'll face penalties if we miss the deadline.
        
        Love,
        Mom
        """
        
        metadata = EmailMetadata(
            sender="mom@example.com",
            subject="URGENT - Tax documents due Friday",
            date="2024-12-03",
        )
        
        packets = analyze_email_agents(text, {
            'sender': metadata.sender,
            'subject': metadata.subject,
        })
        analysis = route_email(packets, metadata)
        
        # Should route to URGENT-NOW
        assert analysis.routing_folder == "1-URGENT-NOW"
        assert analysis.routing_priority == "critical"
        
        # Should detect high urgency
        assert analysis.urgency > 0.7
        
        # Should detect warmth (family)
        assert analysis.warmth > 0.5
        
        # Topic should relate to taxes
        assert "tax" in analysis.topic.lower()
    
    def test_moderate_urgency_business(self):
        """Should route moderately urgent business email"""
        text = """
        Dear John,
        
        Following up on our meeting last week. Could you please send
        the quarterly report by end of day Thursday?
        
        Best regards,
        Jane Smith
        """
        
        metadata = EmailMetadata(
            sender="jane.smith@company.com",
            subject="Quarterly Report Request",
            date="2024-12-03",
        )
        
        packets = analyze_email_agents(text, {
            'sender': metadata.sender,
            'subject': metadata.subject,
        })
        analysis = route_email(packets, metadata)
        
        # Should route to Action-Required (not URGENT)
        assert analysis.routing_folder in ["3-Action-Required", "2-Important"]
        
        # Moderate urgency
        assert 0.3 < analysis.urgency < 0.8


class TestNewsletterRouting:
    """Test newsletter detection and routing"""
    
    def test_newsletter_detection(self):
        """Should detect and route newsletters correctly"""
        text = """
        Welcome to this week's AI Research Digest!
        
        Top stories:
        - New GPT release
        - Latest DeepMind paper
        
        Unsubscribe at any time.
        """
        
        metadata = EmailMetadata(
            sender="newsletter@airesearch.com",
            subject="AI Research Digest - Weekly Update",
            date="2024-12-03",
        )
        
        packets = analyze_email_agents(text, {
            'sender': metadata.sender,
            'subject': metadata.subject,
        })
        analysis = route_email(packets, metadata)
        
        # Should route to Read-Later
        assert analysis.routing_folder == "4-Read-Later"
        
        # Should have low urgency
        assert analysis.urgency < 0.3


class TestBenevolenceProtection:
    """Test benevolence clamp protecting personal emails"""
    
    def test_personal_not_archived(self):
        """High-warmth personal email should never go to Reference"""
        text = """
        Hey John,
        
        Just wanted to check in and see how you're doing.
        Hope all is well with your projects!
        
        Love,
        Sarah
        """
        
        metadata = EmailMetadata(
            sender="sarah@friend.com",
            subject="Checking in",
            date="2024-12-03",
        )
        
        packets = analyze_email_agents(text, {
            'sender': metadata.sender,
            'subject': metadata.subject,
        })
        analysis = route_email(packets, metadata)
        
        # Should NOT go to Reference (5-Reference)
        assert analysis.routing_folder != "5-Reference"
        
        # Should detect high warmth
        assert analysis.warmth > 0.5


class TestImportanceDetection:
    """Test importance domain detection"""
    
    def test_financial_importance(self):
        """Should detect financial importance"""
        text = """
        Dear Customer,
        
        Your invoice #12345 for $5,000 is due on December 15th.
        Please remit payment by the due date to avoid late fees.
        
        Accounting Department
        """
        
        metadata = EmailMetadata(
            sender="billing@company.com",
            subject="Invoice Due - $5,000",
            date="2024-12-03",
        )
        
        packets = analyze_email_agents(text, {
            'sender': metadata.sender,
            'subject': metadata.subject,
        })
        analysis = route_email(packets, metadata)
        
        # Should detect high importance (financial)
        assert analysis.importance > 0.6
        
        # Should route to Important
        assert analysis.routing_folder in ["1-URGENT-NOW", "2-Important"]
    
    def test_health_importance(self):
        """Should detect health-related importance"""
        text = """
        Dear Patient,
        
        Your medical test results are ready. Please call our office
        at your earliest convenience to discuss your treatment options.
        
        Dr. Smith's Office
        """
        
        metadata = EmailMetadata(
            sender="office@doctor.com",
            subject="Test Results Available",
            date="2024-12-03",
        )
        
        packets = analyze_email_agents(text, {
            'sender': metadata.sender,
            'subject': metadata.subject,
        })
        analysis = route_email(packets, metadata)
        
        # Should detect high importance (health)
        assert analysis.importance > 0.7


class TestTopicExtraction:
    """Test topic identification"""
    
    def test_subject_line_topic(self):
        """Should extract topic from subject line"""
        text = "Meeting agenda attached."
        
        metadata = EmailMetadata(
            sender="colleague@work.com",
            subject="Q4 Planning Meeting",
            date="2024-12-03",
        )
        
        packets = analyze_email_agents(text, {
            'sender': metadata.sender,
            'subject': metadata.subject,
        })
        analysis = route_email(packets, metadata)
        
        # Topic should include meeting or planning
        assert any(word in analysis.topic.lower() 
                  for word in ['meeting', 'planning', 'meetings'])


class TestGlyphGeneration:
    """Test PICTOGRAM-256 glyph generation"""
    
    def test_consistent_glyph_generation(self):
        """Same email should always generate same glyph"""
        text = "Test email content"
        
        metadata = EmailMetadata(
            sender="test@example.com",
            subject="Test",
            date="2024-12-03",
        )
        
        # Process same email twice
        packets1 = analyze_email_agents(text, {'sender': metadata.sender, 'subject': metadata.subject})
        analysis1 = route_email(packets1, metadata)
        
        packets2 = analyze_email_agents(text, {'sender': metadata.sender, 'subject': metadata.subject})
        analysis2 = route_email(packets2, metadata)
        
        # Glyphs should be identical
        assert analysis1.icon == analysis2.icon
    
    def test_glyph_is_three_characters(self):
        """Glyph should always be 3 characters"""
        text = "Any email content"
        
        metadata = EmailMetadata(
            sender="any@example.com",
            subject="Any subject",
            date="2024-12-03",
        )
        
        packets = analyze_email_agents(text, {'sender': metadata.sender, 'subject': metadata.subject})
        analysis = route_email(packets, metadata)
        
        # Should be exactly 3 glyphs
        assert len(analysis.icon) == 3


class TestAuditability:
    """Test that all agent packets are preserved"""
    
    def test_all_packets_preserved(self):
        """All 5 agent packets should be in final analysis"""
        text = "Test email for auditability"
        
        metadata = EmailMetadata(
            sender="test@example.com",
            subject="Test",
            date="2024-12-03",
        )
        
        packets = analyze_email_agents(text, {'sender': metadata.sender, 'subject': metadata.subject})
        analysis = route_email(packets, metadata)
        
        # Should have all 5 agents
        assert len(analysis.packets) == 5
        
        # Should have expected agent roles
        expected_roles = {'urgency', 'importance', 'topic', 'tone', 'action'}
        actual_roles = set(analysis.packets.keys())
        assert actual_roles == expected_roles
    
    def test_packets_have_glosses(self):
        """Each packet should have human-readable gloss"""
        text = "Test email content"
        
        metadata = EmailMetadata(
            sender="test@example.com",
            subject="Test",
            date="2024-12-03",
        )
        
        packets = analyze_email_agents(text, {'sender': metadata.sender, 'subject': metadata.subject})
        analysis = route_email(packets, metadata)
        
        # Every packet should have non-empty gloss
        for role, packet in analysis.packets.items():
            assert packet.gloss
            assert len(packet.gloss) > 0
            assert isinstance(packet.gloss, str)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
