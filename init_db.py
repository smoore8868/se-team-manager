#!/usr/bin/env python3
"""Initialize the database with sample data."""

from datetime import datetime, date, timedelta
from app import app, db
from models import TeamMember, OneOnOne, Opportunity, OpportunityUpdate, SupportCase, SupportCaseComment, FollowUp, Note, SkillRating


def init_database():
    """Create all tables and optionally add sample data."""
    with app.app_context():
        # Create all tables
        db.create_all()
        print("Database tables created successfully!")

        # Check if data already exists
        if TeamMember.query.first():
            print("Database already has data. Skipping sample data creation.")
            return

        # Add sample team members
        members = [
            TeamMember(name="Alice Johnson", email="alice@example.com", region="Americas", aligned_rep="Bob Smith", aligned_rep_2="Sarah Miller", role="Senior SE"),
            TeamMember(name="Charlie Brown", email="charlie@example.com", region="EMEA", aligned_rep="Diana Ross", aligned_rep_2="", role="SE"),
            TeamMember(name="Eve Williams", email="eve@example.com", region="APAC", aligned_rep="Frank Chen", aligned_rep_2="Lisa Wang", role="SE Manager"),
        ]
        for m in members:
            db.session.add(m)
        db.session.commit()
        print(f"Added {len(members)} team members")

        # Add sample 1-1 meetings
        one_on_ones = [
            OneOnOne(team_member_id=1, date=date.today() - timedelta(days=7), notes="Discussed Q4 goals and career development.", action_items="- Complete training\n- Review pipeline", mood="Good"),
            OneOnOne(team_member_id=2, date=date.today() - timedelta(days=3), notes="Weekly sync on active deals.", action_items="- Follow up with Acme Corp\n- Prepare demo", mood="Excellent"),
            OneOnOne(team_member_id=3, date=date.today() - timedelta(days=1), notes="Team planning session.", action_items="- Finalize Q1 roadmap", mood="Neutral"),
        ]
        for o in one_on_ones:
            db.session.add(o)
        db.session.commit()
        print(f"Added {len(one_on_ones)} 1-1 meetings")

        # Add sample opportunities
        opportunities = [
            Opportunity(name="Acme Corp Enterprise Deal", account="Acme Corporation", stage="POC", value=150000, team_member_id=1, close_date=date.today() + timedelta(days=30)),
            Opportunity(name="TechStart Expansion", account="TechStart Inc", stage="Demo", value=75000, team_member_id=1, close_date=date.today() + timedelta(days=45)),
            Opportunity(name="Global Bank Platform", account="Global Bank", stage="Negotiation", value=500000, team_member_id=2, close_date=date.today() + timedelta(days=15)),
            Opportunity(name="Retail Plus Integration", account="Retail Plus", stage="Prospecting", value=50000, team_member_id=3, close_date=date.today() + timedelta(days=60)),
        ]
        for opp in opportunities:
            db.session.add(opp)
        db.session.commit()

        # Add opportunity updates
        for opp in opportunities:
            update = OpportunityUpdate(opportunity_id=opp.id, stage_to=opp.stage, comment="Opportunity created")
            db.session.add(update)
        db.session.commit()
        print(f"Added {len(opportunities)} opportunities")

        # Add sample support cases
        cases = [
            SupportCase(title="Login Issues", description="Customer unable to log in after password reset", status="In Progress", priority="High", team_member_id=1, customer="Acme Corporation"),
            SupportCase(title="API Integration Help", description="Need assistance with REST API setup", status="Open", priority="Medium", team_member_id=2, customer="TechStart Inc"),
            SupportCase(title="Performance Optimization", description="Dashboard loading slowly", status="Pending", priority="Low", team_member_id=3, customer="Retail Plus"),
        ]
        for case in cases:
            db.session.add(case)
        db.session.commit()

        # Add case comments
        comment = SupportCaseComment(case_id=1, comment="Investigating authentication service logs")
        db.session.add(comment)
        db.session.commit()
        print(f"Added {len(cases)} support cases")

        # Add sample follow-ups
        follow_ups = [
            FollowUp(title="Send POC documentation", description="Prepare and send POC requirements document", due_date=date.today() + timedelta(days=2), status="Pending", priority="High", team_member_id=1, related_type="opportunity", related_id=1),
            FollowUp(title="Schedule demo call", description="Set up demo with technical team", due_date=date.today() + timedelta(days=5), status="Pending", priority="Medium", team_member_id=2),
            FollowUp(title="Review contract terms", description="Legal review of contract", due_date=date.today() - timedelta(days=1), status="In Progress", priority="High", team_member_id=2, related_type="opportunity", related_id=3),
            FollowUp(title="Training completion", description="Complete advanced product training", due_date=date.today() + timedelta(days=14), status="Pending", priority="Low", team_member_id=1),
        ]
        for fu in follow_ups:
            db.session.add(fu)
        db.session.commit()
        print(f"Added {len(follow_ups)} follow-ups")

        # Add sample notes
        notes = [
            Note(title="Acme Corp Requirements", content="Key requirements from discovery call:\n- SSO integration required\n- 99.9% uptime SLA\n- Data residency in US\n- Support for 5000 users", tags="acme, requirements, discovery", team_member_id=1),
            Note(title="Competitive Analysis", content="Main competitors in this deal:\n- Competitor A: Strong in enterprise\n- Competitor B: Better pricing\n\nOur advantages: Integration capabilities, support quality", tags="competitive, strategy", team_member_id=2),
            Note(title="Q4 Planning Notes", content="Team priorities for Q4:\n1. Close Acme deal\n2. Expand EMEA coverage\n3. Launch new demo environment\n4. Complete certifications", tags="planning, q4, team"),
        ]
        for note in notes:
            db.session.add(note)
        db.session.commit()
        print(f"Added {len(notes)} notes")

        # Add sample skill ratings
        skill_ratings = [
            # Alice Johnson (id=1) - Advanced/Senior SE
            SkillRating(team_member_id=1, skill='Password Safe', proficiency='Expert'),
            SkillRating(team_member_id=1, skill='EPM Win-Mac', proficiency='Expert'),
            SkillRating(team_member_id=1, skill='EPM-L', proficiency='POV Ready'),
            SkillRating(team_member_id=1, skill='Remote Support', proficiency='Demo Ready'),
            SkillRating(team_member_id=1, skill='PRA', proficiency='POV Ready'),
            SkillRating(team_member_id=1, skill='AD Bridge', proficiency='Expert'),
            SkillRating(team_member_id=1, skill='Insights', proficiency='Demo Ready'),
            SkillRating(team_member_id=1, skill='Entitle', proficiency='Training'),
            # Charlie Brown (id=2) - Mid-level SE
            SkillRating(team_member_id=2, skill='Password Safe', proficiency='POV Ready'),
            SkillRating(team_member_id=2, skill='EPM Win-Mac', proficiency='Demo Ready'),
            SkillRating(team_member_id=2, skill='EPM-L', proficiency='Training'),
            SkillRating(team_member_id=2, skill='Remote Support', proficiency='POV Ready'),
            SkillRating(team_member_id=2, skill='PRA', proficiency='Demo Ready'),
            SkillRating(team_member_id=2, skill='AD Bridge', proficiency='Training'),
            SkillRating(team_member_id=2, skill='Insights', proficiency="Haven't Started"),
            SkillRating(team_member_id=2, skill='Entitle', proficiency="Haven't Started"),
            # Eve Williams (id=3) - Broad coverage / Manager
            SkillRating(team_member_id=3, skill='Password Safe', proficiency='Demo Ready'),
            SkillRating(team_member_id=3, skill='EPM Win-Mac', proficiency='Demo Ready'),
            SkillRating(team_member_id=3, skill='EPM-L', proficiency='Demo Ready'),
            SkillRating(team_member_id=3, skill='Remote Support', proficiency='Demo Ready'),
            SkillRating(team_member_id=3, skill='PRA', proficiency='Training'),
            SkillRating(team_member_id=3, skill='AD Bridge', proficiency='Demo Ready'),
            SkillRating(team_member_id=3, skill='Insights', proficiency='POV Ready'),
            SkillRating(team_member_id=3, skill='Entitle', proficiency='Training'),
        ]
        for sr in skill_ratings:
            db.session.add(sr)
        db.session.commit()
        print(f"Added {len(skill_ratings)} skill ratings")

        print("\nDatabase initialization complete!")
        print("You can now run 'python app.py' to start the server.")


if __name__ == '__main__':
    init_database()
