from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from models import db, TeamMember, OneOnOne, Opportunity, OpportunityUpdate, SupportCase, SupportCaseComment, FollowUp, Note, SkillRating
from datetime import datetime, date
from dateutil.parser import parse as parse_date
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = 'se-team-manager-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///se_team.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

REGIONS = ['East', 'Central', 'West', 'Global']
OPPORTUNITY_STAGES = ['1', '2', '3', '4', '5', '6']
CASE_STATUSES = ['Open', 'In Progress', 'Pending', 'Resolved', 'Closed']
PRIORITIES = ['High', 'Medium', 'Low']
FOLLOWUP_STATUSES = ['Pending', 'In Progress', 'Completed', 'Deferred']
MOODS = ['Excellent', 'Good', 'Neutral', 'Concerned', 'Needs Attention']
SKILLS = ['Password Safe', 'EPM Win-Mac', 'EPM-L', 'Remote Support', 'PRA', 'AD Bridge', 'Insights', 'Entitle']
PROFICIENCY_LEVELS = ["Haven't Started", 'Training', 'Demo Ready', 'POV Ready', 'Expert']
PRODUCTS = ['EPM', 'EPM-L', 'PWS', 'RS', 'PRA', 'ADB', 'Insights', 'Entitle']
POV_STATUSES = ['None', 'Active', 'Completed', 'Tech Win']


@app.context_processor
def inject_globals():
    return {
        'regions': REGIONS,
        'opportunity_stages': OPPORTUNITY_STAGES,
        'case_statuses': CASE_STATUSES,
        'priorities': PRIORITIES,
        'followup_statuses': FOLLOWUP_STATUSES,
        'moods': MOODS,
        'skills': SKILLS,
        'proficiency_levels': PROFICIENCY_LEVELS,
        'products_list': PRODUCTS,
        'pov_statuses': POV_STATUSES,
    }


# Dashboard
@app.route('/')
def dashboard():
    team_count = TeamMember.query.count()
    live_povs = Opportunity.query.filter(Opportunity.pov_status == 'Active').count()
    open_opps = Opportunity.query.filter(Opportunity.stage != '6').count()
    open_cases = SupportCase.query.filter(~SupportCase.status.in_(['Resolved', 'Closed'])).count()
    pending_followups = FollowUp.query.filter(FollowUp.status.in_(['Pending', 'In Progress'])).count()
    overdue_followups = FollowUp.query.filter(
        FollowUp.status.in_(['Pending', 'In Progress']),
        FollowUp.due_date < date.today()
    ).all()
    recent_one_on_ones = OneOnOne.query.order_by(OneOnOne.date.desc()).limit(5).all()
    upcoming_followups = FollowUp.query.filter(
        FollowUp.status.in_(['Pending', 'In Progress'])
    ).order_by(FollowUp.due_date).limit(5).all()

    return render_template('dashboard.html',
                           team_count=team_count,
                           live_povs=live_povs,
                           open_opps=open_opps,
                           open_cases=open_cases,
                           pending_followups=pending_followups,
                           overdue_followups=overdue_followups,
                           recent_one_on_ones=recent_one_on_ones,
                           upcoming_followups=upcoming_followups,
                           today=date.today())


# Team Members
@app.route('/team')
def team_members():
    members = TeamMember.query.order_by(TeamMember.name).all()
    return render_template('team_members.html', members=members)


@app.route('/team/add', methods=['POST'])
def add_team_member():
    member = TeamMember(
        name=request.form['name'],
        email=request.form['email'],
        region=request.form['region'],
        aligned_rep=request.form.get('aligned_rep', ''),
        aligned_rep_2=request.form.get('aligned_rep_2', ''),
        role=request.form.get('role', 'SE')
    )
    db.session.add(member)
    db.session.commit()
    flash('Team member added successfully', 'success')
    return redirect(url_for('team_members'))


@app.route('/team/edit/<int:id>', methods=['POST'])
def edit_team_member(id):
    member = TeamMember.query.get_or_404(id)
    member.name = request.form['name']
    member.email = request.form['email']
    member.region = request.form['region']
    member.aligned_rep = request.form.get('aligned_rep', '')
    member.aligned_rep_2 = request.form.get('aligned_rep_2', '')
    member.role = request.form.get('role', 'SE')
    db.session.commit()
    flash('Team member updated successfully', 'success')
    return redirect(url_for('team_members'))


@app.route('/team/delete/<int:id>', methods=['POST'])
def delete_team_member(id):
    member = TeamMember.query.get_or_404(id)
    db.session.delete(member)
    db.session.commit()
    flash('Team member deleted successfully', 'success')
    return redirect(url_for('team_members'))


# One-on-Ones
@app.route('/one-on-ones')
def one_on_ones():
    member_id = request.args.get('member_id', type=int)
    team_members_list = TeamMember.query.order_by(TeamMember.name).all()

    selected_member = None
    meetings = []
    active_opps = []
    open_cases = []
    live_povs = []
    skill_ratings = {}
    open_followups = []
    member_notes = []

    if member_id:
        selected_member = TeamMember.query.get(member_id)
        if selected_member:
            meetings = (OneOnOne.query
                        .filter(OneOnOne.team_member_id == member_id)
                        .order_by(OneOnOne.date.desc()).all())
            active_opps = (Opportunity.query
                           .filter(Opportunity.team_member_id == member_id,
                                   Opportunity.stage != '6')
                           .order_by(Opportunity.updated_at.desc()).all())
            open_cases = (SupportCase.query
                          .filter(SupportCase.team_member_id == member_id,
                                  ~SupportCase.status.in_(['Resolved', 'Closed']))
                          .order_by(SupportCase.created_at.desc()).all())
            live_povs = (Opportunity.query
                         .filter(Opportunity.team_member_id == member_id,
                                 Opportunity.pov_status == 'Active')
                         .order_by(Opportunity.updated_at.desc()).all())
            ratings = SkillRating.query.filter_by(team_member_id=member_id).all()
            skill_ratings = {r.skill: r.proficiency for r in ratings}
            open_followups = (FollowUp.query
                              .filter(FollowUp.team_member_id == member_id,
                                      ~FollowUp.status.in_(['Completed']))
                              .order_by(FollowUp.due_date).all())
            member_notes = (Note.query
                            .filter(Note.team_member_id == member_id)
                            .order_by(Note.created_at.desc()).all())

    return render_template('one_on_ones.html',
                           team_members=team_members_list,
                           selected_member=selected_member,
                           member_id=member_id,
                           meetings=meetings,
                           active_opps=active_opps,
                           open_cases=open_cases,
                           live_povs=live_povs,
                           skill_ratings=skill_ratings,
                           open_followups=open_followups,
                           member_notes=member_notes,
                           today=date.today())


@app.route('/one-on-ones/add', methods=['POST'])
def add_one_on_one():
    member_id = request.form['team_member_id']
    meeting = OneOnOne(
        team_member_id=member_id,
        date=parse_date(request.form['date']).date(),
        notes=request.form.get('notes', ''),
        action_items=request.form.get('action_items', ''),
        mood=request.form.get('mood', '')
    )
    db.session.add(meeting)
    db.session.commit()
    flash('1-1 meeting logged successfully', 'success')
    return redirect(url_for('one_on_ones', member_id=member_id))


@app.route('/one-on-ones/edit/<int:id>', methods=['POST'])
def edit_one_on_one(id):
    meeting = OneOnOne.query.get_or_404(id)
    meeting.team_member_id = request.form['team_member_id']
    meeting.date = parse_date(request.form['date']).date()
    meeting.notes = request.form.get('notes', '')
    meeting.action_items = request.form.get('action_items', '')
    meeting.mood = request.form.get('mood', '')
    db.session.commit()
    flash('1-1 meeting updated successfully', 'success')
    return redirect(url_for('one_on_ones', member_id=meeting.team_member_id))


@app.route('/one-on-ones/delete/<int:id>', methods=['POST'])
def delete_one_on_one(id):
    meeting = OneOnOne.query.get_or_404(id)
    member_id = meeting.team_member_id
    db.session.delete(meeting)
    db.session.commit()
    flash('1-1 meeting deleted successfully', 'success')
    return redirect(url_for('one_on_ones', member_id=member_id))


# Opportunities
@app.route('/opportunities')
def opportunities():
    stage = request.args.get('stage')
    member_id = request.args.get('member_id', type=int)

    query = Opportunity.query
    if stage:
        query = query.filter(Opportunity.stage == stage)
    if member_id:
        query = query.filter(Opportunity.team_member_id == member_id)

    opps = query.order_by(Opportunity.updated_at.desc()).all()
    team_members = TeamMember.query.order_by(TeamMember.name).all()
    return render_template('opportunities.html', opportunities=opps, team_members=team_members,
                           selected_stage=stage, selected_member=member_id)


@app.route('/opportunities/add', methods=['POST'])
def add_opportunity():
    opp = Opportunity(
        name=request.form['name'],
        account=request.form['account'],
        stage=request.form.get('stage', '1'),
        value=float(request.form.get('value', 0) or 0),
        team_member_id=request.form['team_member_id'],
        close_date=parse_date(request.form['close_date']).date() if request.form.get('close_date') else None,
        salesforce_link=request.form.get('salesforce_link', ''),
        confidence=int(request.form['confidence']) if request.form.get('confidence') else None,
        sales_rep=request.form.get('sales_rep', ''),
        products=','.join(request.form.getlist('products')),
        rfp=request.form.get('rfp', 'N'),
        demo=request.form.get('demo', 'N'),
        pov_status=request.form.get('pov_status', 'None'),
        latest_update_date=parse_date(request.form['latest_update_date']).date() if request.form.get('latest_update_date') else None,
        latest_update_notes=request.form.get('latest_update_notes', ''),
    )
    db.session.add(opp)
    db.session.commit()

    update = OpportunityUpdate(
        opportunity_id=opp.id,
        stage_to=opp.stage,
        comment='Opportunity created'
    )
    db.session.add(update)
    db.session.commit()

    flash('Opportunity added successfully', 'success')
    next_url = request.form.get('next')
    if next_url:
        return redirect(next_url)
    return redirect(url_for('opportunities'))


@app.route('/opportunities/edit/<int:id>', methods=['POST'])
def edit_opportunity(id):
    opp = Opportunity.query.get_or_404(id)
    old_stage = opp.stage

    opp.name = request.form['name']
    opp.account = request.form['account']
    opp.stage = request.form.get('stage', opp.stage)
    opp.value = float(request.form.get('value', 0) or 0)
    opp.team_member_id = request.form['team_member_id']
    opp.close_date = parse_date(request.form['close_date']).date() if request.form.get('close_date') else None
    opp.salesforce_link = request.form.get('salesforce_link', '')
    opp.confidence = int(request.form['confidence']) if request.form.get('confidence') else None
    opp.sales_rep = request.form.get('sales_rep', '')
    opp.products = ','.join(request.form.getlist('products'))
    opp.rfp = request.form.get('rfp', 'N')
    opp.demo = request.form.get('demo', 'N')
    opp.pov_status = request.form.get('pov_status', 'None')
    opp.latest_update_date = parse_date(request.form['latest_update_date']).date() if request.form.get('latest_update_date') else None
    opp.latest_update_notes = request.form.get('latest_update_notes', '')

    if old_stage != opp.stage:
        update = OpportunityUpdate(
            opportunity_id=opp.id,
            stage_from=old_stage,
            stage_to=opp.stage,
            comment=request.form.get('comment', f'Stage changed from {old_stage} to {opp.stage}')
        )
        db.session.add(update)

    db.session.commit()
    flash('Opportunity updated successfully', 'success')
    next_url = request.form.get('next')
    if next_url:
        return redirect(next_url)
    return redirect(url_for('opportunities'))


@app.route('/opportunities/comment/<int:id>', methods=['POST'])
def add_opportunity_comment(id):
    opp = Opportunity.query.get_or_404(id)
    update = OpportunityUpdate(
        opportunity_id=opp.id,
        comment=request.form['comment']
    )
    db.session.add(update)
    db.session.commit()
    flash('Comment added successfully', 'success')
    return redirect(url_for('opportunities'))


@app.route('/opportunities/delete/<int:id>', methods=['POST'])
def delete_opportunity(id):
    opp = Opportunity.query.get_or_404(id)
    db.session.delete(opp)
    db.session.commit()
    flash('Opportunity deleted successfully', 'success')
    return redirect(url_for('opportunities'))


# Support Cases
@app.route('/support-cases')
def support_cases():
    status = request.args.get('status')
    priority = request.args.get('priority')
    member_id = request.args.get('member_id', type=int)

    query = SupportCase.query
    if status:
        query = query.filter(SupportCase.status == status)
    if priority:
        query = query.filter(SupportCase.priority == priority)
    if member_id:
        query = query.filter(SupportCase.team_member_id == member_id)

    cases = query.order_by(SupportCase.created_at.desc()).all()
    team_members = TeamMember.query.order_by(TeamMember.name).all()
    return render_template('support_cases.html', cases=cases, team_members=team_members,
                           selected_status=status, selected_priority=priority, selected_member=member_id)


@app.route('/support-cases/add', methods=['POST'])
def add_support_case():
    case = SupportCase(
        title=request.form['title'],
        description=request.form.get('description', ''),
        status=request.form.get('status', 'Open'),
        priority=request.form.get('priority', 'Medium'),
        team_member_id=request.form['team_member_id'],
        customer=request.form.get('customer', '')
    )
    db.session.add(case)
    db.session.commit()
    flash('Support case created successfully', 'success')
    return redirect(url_for('support_cases'))


@app.route('/support-cases/edit/<int:id>', methods=['POST'])
def edit_support_case(id):
    case = SupportCase.query.get_or_404(id)
    old_status = case.status

    case.title = request.form['title']
    case.description = request.form.get('description', '')
    case.status = request.form.get('status', case.status)
    case.priority = request.form.get('priority', case.priority)
    case.team_member_id = request.form['team_member_id']
    case.customer = request.form.get('customer', '')

    if case.status in ['Resolved', 'Closed'] and old_status not in ['Resolved', 'Closed']:
        case.resolved_at = datetime.utcnow()
    elif case.status not in ['Resolved', 'Closed']:
        case.resolved_at = None

    db.session.commit()
    flash('Support case updated successfully', 'success')
    next_url = request.form.get('next')
    if next_url:
        return redirect(next_url)
    return redirect(url_for('support_cases'))


@app.route('/support-cases/comment/<int:id>', methods=['POST'])
def add_case_comment(id):
    case = SupportCase.query.get_or_404(id)
    comment = SupportCaseComment(
        case_id=case.id,
        comment=request.form['comment']
    )
    db.session.add(comment)
    db.session.commit()
    flash('Comment added successfully', 'success')
    return redirect(url_for('support_cases'))


@app.route('/support-cases/delete/<int:id>', methods=['POST'])
def delete_support_case(id):
    case = SupportCase.query.get_or_404(id)
    db.session.delete(case)
    db.session.commit()
    flash('Support case deleted successfully', 'success')
    return redirect(url_for('support_cases'))


# Follow-ups
@app.route('/follow-ups')
def follow_ups():
    status = request.args.get('status')
    priority = request.args.get('priority')
    member_id = request.args.get('member_id', type=int)

    query = FollowUp.query
    if status:
        query = query.filter(FollowUp.status == status)
    if priority:
        query = query.filter(FollowUp.priority == priority)
    if member_id:
        query = query.filter(FollowUp.team_member_id == member_id)

    items = query.order_by(FollowUp.due_date).all()
    team_members = TeamMember.query.order_by(TeamMember.name).all()
    return render_template('follow_ups.html', follow_ups=items, team_members=team_members,
                           selected_status=status, selected_priority=priority, selected_member=member_id,
                           today=date.today())


@app.route('/follow-ups/add', methods=['POST'])
def add_follow_up():
    follow_up = FollowUp(
        title=request.form['title'],
        description=request.form.get('description', ''),
        due_date=parse_date(request.form['due_date']).date(),
        status=request.form.get('status', 'Pending'),
        priority=request.form.get('priority', 'Medium'),
        related_type=request.form.get('related_type', ''),
        related_id=int(request.form['related_id']) if request.form.get('related_id') else None,
        team_member_id=int(request.form['team_member_id']) if request.form.get('team_member_id') else None
    )
    db.session.add(follow_up)
    db.session.commit()
    flash('Follow-up created successfully', 'success')
    next_url = request.form.get('next')
    if next_url:
        return redirect(next_url)
    return redirect(url_for('follow_ups'))


@app.route('/follow-ups/edit/<int:id>', methods=['POST'])
def edit_follow_up(id):
    follow_up = FollowUp.query.get_or_404(id)
    follow_up.title = request.form['title']
    follow_up.description = request.form.get('description', '')
    follow_up.due_date = parse_date(request.form['due_date']).date()
    follow_up.status = request.form.get('status', follow_up.status)
    follow_up.priority = request.form.get('priority', follow_up.priority)
    follow_up.related_type = request.form.get('related_type', '')
    follow_up.related_id = int(request.form['related_id']) if request.form.get('related_id') else None
    follow_up.team_member_id = int(request.form['team_member_id']) if request.form.get('team_member_id') else None
    db.session.commit()
    flash('Follow-up updated successfully', 'success')
    next_url = request.form.get('next')
    if next_url:
        return redirect(next_url)
    return redirect(url_for('follow_ups'))


@app.route('/follow-ups/complete/<int:id>', methods=['POST'])
def complete_follow_up(id):
    follow_up = FollowUp.query.get_or_404(id)
    follow_up.status = 'Completed'
    db.session.commit()
    flash('Follow-up marked as completed', 'success')
    next_url = request.form.get('next')
    if next_url:
        return redirect(next_url)
    return redirect(request.referrer or url_for('follow_ups'))


@app.route('/follow-ups/delete/<int:id>', methods=['POST'])
def delete_follow_up(id):
    follow_up = FollowUp.query.get_or_404(id)
    db.session.delete(follow_up)
    db.session.commit()
    flash('Follow-up deleted successfully', 'success')
    next_url = request.form.get('next')
    if next_url:
        return redirect(next_url)
    return redirect(url_for('follow_ups'))


# Notes
@app.route('/notes')
def notes():
    search = request.args.get('search', '')
    member_id = request.args.get('member_id', type=int)
    tag = request.args.get('tag', '')

    query = Note.query
    if search:
        query = query.filter(
            db.or_(
                Note.title.ilike(f'%{search}%'),
                Note.content.ilike(f'%{search}%')
            )
        )
    if member_id:
        query = query.filter(Note.team_member_id == member_id)
    if tag:
        query = query.filter(Note.tags.ilike(f'%{tag}%'))

    all_notes = query.order_by(Note.created_at.desc()).all()
    team_members = TeamMember.query.order_by(TeamMember.name).all()

    all_tags = set()
    for note in Note.query.all():
        if note.tags:
            all_tags.update([t.strip() for t in note.tags.split(',') if t.strip()])

    return render_template('notes.html', notes=all_notes, team_members=team_members,
                           search=search, selected_member=member_id, selected_tag=tag, all_tags=sorted(all_tags))


@app.route('/notes/add', methods=['POST'])
def add_note():
    note = Note(
        title=request.form['title'],
        content=request.form.get('content', ''),
        tags=request.form.get('tags', ''),
        team_member_id=int(request.form['team_member_id']) if request.form.get('team_member_id') else None
    )
    db.session.add(note)
    db.session.commit()
    flash('Note created successfully', 'success')
    return redirect(url_for('notes'))


@app.route('/notes/edit/<int:id>', methods=['POST'])
def edit_note(id):
    note = Note.query.get_or_404(id)
    note.title = request.form['title']
    note.content = request.form.get('content', '')
    note.tags = request.form.get('tags', '')
    note.team_member_id = int(request.form['team_member_id']) if request.form.get('team_member_id') else None
    db.session.commit()
    flash('Note updated successfully', 'success')
    return redirect(url_for('notes'))


@app.route('/notes/delete/<int:id>', methods=['POST'])
def delete_note(id):
    note = Note.query.get_or_404(id)
    db.session.delete(note)
    db.session.commit()
    flash('Note deleted successfully', 'success')
    return redirect(url_for('notes'))


# Skill Matrix
@app.route('/skill-matrix')
def skill_matrix():
    region = request.args.get('region')

    # Per-skill proficiency filters
    skill_filters = {}
    for s in SKILLS:
        val = request.args.get('skill_' + s)
        if val:
            skill_filters[s] = val

    query = TeamMember.query
    if region:
        query = query.filter(TeamMember.region == region)

    if skill_filters:
        all_ratings = SkillRating.query.all()
        ratings_map = {}
        for r in all_ratings:
            ratings_map.setdefault(r.team_member_id, {})[r.skill] = r.proficiency

        matching_ids = set()
        all_member_ids = {m.id for m in TeamMember.query.all()}
        for mid in all_member_ids:
            member_ratings = ratings_map.get(mid, {})
            match = True
            for s, level in skill_filters.items():
                if member_ratings.get(s, "Haven't Started") != level:
                    match = False
                    break
            if match:
                matching_ids.add(mid)

        if matching_ids:
            query = query.filter(TeamMember.id.in_(matching_ids))
        else:
            query = query.filter(db.false())

    members = query.order_by(TeamMember.name).all()
    all_ratings = SkillRating.query.all()
    ratings = {(r.team_member_id, r.skill): r.proficiency for r in all_ratings}
    return render_template('skill_matrix.html', members=members, ratings=ratings,
                           selected_region=region, skill_filters=skill_filters)


@app.route('/skill-matrix/update', methods=['POST'])
def update_skill_rating():
    team_member_id = int(request.form['team_member_id'])
    skill = request.form['skill']
    proficiency = request.form['proficiency']

    rating = SkillRating.query.filter_by(team_member_id=team_member_id, skill=skill).first()
    if rating:
        rating.proficiency = proficiency
    else:
        rating = SkillRating(team_member_id=team_member_id, skill=skill, proficiency=proficiency)
        db.session.add(rating)
    db.session.commit()

    next_url = request.form.get('next')
    if next_url:
        return redirect(next_url)
    redirect_args = {}
    if request.form.get('filter_region'):
        redirect_args['region'] = request.form['filter_region']
    for s in SKILLS:
        val = request.form.get('filter_skill_' + s)
        if val:
            redirect_args['skill_' + s] = val
    return redirect(url_for('skill_matrix', **redirect_args))


# Reports
@app.route('/reports')
def reports():
    team_members = TeamMember.query.order_by(TeamMember.name).all()
    one_on_ones = OneOnOne.query.order_by(OneOnOne.date.desc()).all()
    opps = Opportunity.query.order_by(Opportunity.updated_at.desc()).all()
    cases = SupportCase.query.order_by(SupportCase.created_at.desc()).all()
    follow_up_items = FollowUp.query.order_by(FollowUp.due_date).all()
    all_notes = Note.query.order_by(Note.created_at.desc()).all()

    skill_ratings = SkillRating.query.all()

    return render_template('reports.html',
                           team_members=team_members,
                           one_on_ones=one_on_ones,
                           opportunities=opps,
                           cases=cases,
                           follow_ups=follow_up_items,
                           notes=all_notes,
                           skill_ratings=skill_ratings)


@app.route('/reports/generate', methods=['POST'])
def generate_report():
    from reports import generate_pdf_report, generate_csv_report

    report_format = request.form.get('format', 'pdf')
    start_date = request.form.get('start_date')
    end_date = request.form.get('end_date')

    selected = {
        'team_members': request.form.getlist('team_members'),
        'one_on_ones': request.form.getlist('one_on_ones'),
        'opportunities': request.form.getlist('opportunities'),
        'support_cases': request.form.getlist('support_cases'),
        'follow_ups': request.form.getlist('follow_ups'),
        'notes': request.form.getlist('notes'),
        'skill_matrix': request.form.getlist('skill_matrix')
    }

    data = {
        'team_members': TeamMember.query.filter(TeamMember.id.in_(selected['team_members'])).all() if selected['team_members'] else [],
        'one_on_ones': OneOnOne.query.filter(OneOnOne.id.in_(selected['one_on_ones'])).all() if selected['one_on_ones'] else [],
        'opportunities': Opportunity.query.filter(Opportunity.id.in_(selected['opportunities'])).all() if selected['opportunities'] else [],
        'support_cases': SupportCase.query.filter(SupportCase.id.in_(selected['support_cases'])).all() if selected['support_cases'] else [],
        'follow_ups': FollowUp.query.filter(FollowUp.id.in_(selected['follow_ups'])).all() if selected['follow_ups'] else [],
        'notes': Note.query.filter(Note.id.in_(selected['notes'])).all() if selected['notes'] else [],
        'skill_matrix': []
    }

    if selected['skill_matrix']:
        sm_members = TeamMember.query.filter(TeamMember.id.in_(selected['skill_matrix'])).all()
        for member in sm_members:
            ratings = {r.skill: r.proficiency for r in SkillRating.query.filter_by(team_member_id=member.id).all()}
            data['skill_matrix'].append({'member': member, 'ratings': ratings})

    if report_format == 'pdf':
        filepath = generate_pdf_report(data, start_date, end_date)
        return send_file(filepath, as_attachment=True, download_name='se_team_report.pdf')
    else:
        filepath = generate_csv_report(data, start_date, end_date)
        return send_file(filepath, as_attachment=True, download_name='se_team_report.csv')


def migrate_db():
    """Add new opportunity columns if they don't exist and migrate old stage values."""
    from sqlalchemy import inspect
    inspector = inspect(db.engine)
    existing_cols = {col['name'] for col in inspector.get_columns('opportunities')}

    new_cols = {
        'salesforce_link': 'VARCHAR(500)',
        'confidence': 'INTEGER',
        'sales_rep': 'VARCHAR(100)',
        'products': 'VARCHAR(500)',
        'rfp': 'VARCHAR(1)',
        'demo': 'VARCHAR(1)',
        'pov_status': 'VARCHAR(20)',
        'latest_update_date': 'DATE',
        'latest_update_notes': 'TEXT',
    }
    for col_name, col_type in new_cols.items():
        if col_name not in existing_cols:
            db.session.execute(db.text(f'ALTER TABLE opportunities ADD COLUMN {col_name} {col_type}'))

    # Migrate old text stages to numeric 1-6
    stage_map = {
        'Prospecting': '1', 'Qualification': '2', 'Demo': '3',
        'POC': '4', 'Negotiation': '5', 'Closed Won': '6', 'Closed Lost': '6',
    }
    for old, new in stage_map.items():
        db.session.execute(
            db.text("UPDATE opportunities SET stage = :new WHERE stage = :old"),
            {'new': new, 'old': old}
        )
    # Set POV status for old POC-stage records
    if 'pov_status' not in existing_cols:
        db.session.execute(
            db.text("UPDATE opportunities SET pov_status = 'None' WHERE pov_status IS NULL")
        )

    db.session.commit()


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        migrate_db()
    app.run(debug=True)
