from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class TeamMember(db.Model):
    __tablename__ = 'team_members'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    region = db.Column(db.String(50), nullable=False)
    aligned_rep = db.Column(db.String(100))
    aligned_rep_2 = db.Column(db.String(100))
    role = db.Column(db.String(50), default='SE')
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    one_on_ones = db.relationship('OneOnOne', backref='team_member', lazy=True, cascade='all, delete-orphan')
    opportunities = db.relationship('Opportunity', backref='team_member', lazy=True, cascade='all, delete-orphan')
    support_cases = db.relationship('SupportCase', backref='team_member', lazy=True, cascade='all, delete-orphan')
    follow_ups = db.relationship('FollowUp', backref='team_member', lazy=True, cascade='all, delete-orphan')
    notes = db.relationship('Note', backref='team_member', lazy=True, cascade='all, delete-orphan')
    skill_ratings = db.relationship('SkillRating', backref='team_member', lazy=True, cascade='all, delete-orphan')


class OneOnOne(db.Model):
    __tablename__ = 'one_on_ones'

    id = db.Column(db.Integer, primary_key=True)
    team_member_id = db.Column(db.Integer, db.ForeignKey('team_members.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    notes = db.Column(db.Text)
    action_items = db.Column(db.Text)
    mood = db.Column(db.String(20))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class Opportunity(db.Model):
    __tablename__ = 'opportunities'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(200), nullable=False)
    account = db.Column(db.String(200), nullable=False)
    stage = db.Column(db.String(50), nullable=False, default='1')
    value = db.Column(db.Float, default=0)
    team_member_id = db.Column(db.Integer, db.ForeignKey('team_members.id'), nullable=False)
    close_date = db.Column(db.Date)
    salesforce_link = db.Column(db.String(500))
    confidence = db.Column(db.Integer)
    sales_rep = db.Column(db.String(100))
    products = db.Column(db.String(500))
    rfp = db.Column(db.String(1))
    demo = db.Column(db.String(1))
    pov_status = db.Column(db.String(20))
    latest_update_date = db.Column(db.Date)
    latest_update_notes = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    updates = db.relationship('OpportunityUpdate', backref='opportunity', lazy=True, cascade='all, delete-orphan')


class OpportunityUpdate(db.Model):
    __tablename__ = 'opportunity_updates'

    id = db.Column(db.Integer, primary_key=True)
    opportunity_id = db.Column(db.Integer, db.ForeignKey('opportunities.id'), nullable=False)
    stage_from = db.Column(db.String(50))
    stage_to = db.Column(db.String(50))
    comment = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SupportCase(db.Model):
    __tablename__ = 'support_cases'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(50), nullable=False, default='Open')
    priority = db.Column(db.String(20), nullable=False, default='Medium')
    team_member_id = db.Column(db.Integer, db.ForeignKey('team_members.id'), nullable=False)
    customer = db.Column(db.String(200))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    resolved_at = db.Column(db.DateTime)

    comments = db.relationship('SupportCaseComment', backref='support_case', lazy=True, cascade='all, delete-orphan')


class SupportCaseComment(db.Model):
    __tablename__ = 'support_case_comments'

    id = db.Column(db.Integer, primary_key=True)
    case_id = db.Column(db.Integer, db.ForeignKey('support_cases.id'), nullable=False)
    comment = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class FollowUp(db.Model):
    __tablename__ = 'follow_ups'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    due_date = db.Column(db.Date, nullable=False)
    status = db.Column(db.String(50), nullable=False, default='Pending')
    priority = db.Column(db.String(20), nullable=False, default='Medium')
    related_type = db.Column(db.String(50))
    related_id = db.Column(db.Integer)
    team_member_id = db.Column(db.Integer, db.ForeignKey('team_members.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class SkillRating(db.Model):
    __tablename__ = 'skill_ratings'

    id = db.Column(db.Integer, primary_key=True)
    team_member_id = db.Column(db.Integer, db.ForeignKey('team_members.id'), nullable=False)
    skill = db.Column(db.String(50), nullable=False)
    proficiency = db.Column(db.String(50), nullable=False, default="Haven't Started")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    __table_args__ = (
        db.UniqueConstraint('team_member_id', 'skill', name='uq_member_skill'),
    )


class Note(db.Model):
    __tablename__ = 'notes'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    content = db.Column(db.Text)
    tags = db.Column(db.String(500))
    team_member_id = db.Column(db.Integer, db.ForeignKey('team_members.id'))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
