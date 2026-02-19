import os
import csv
import tempfile
from datetime import datetime
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle


def generate_pdf_report(data, start_date=None, end_date=None):
    """Generate a PDF report with selected items."""
    fd, filepath = tempfile.mkstemp(suffix='.pdf')
    os.close(fd)

    doc = SimpleDocTemplate(filepath, pagesize=letter,
                            rightMargin=72, leftMargin=72,
                            topMargin=72, bottomMargin=18)

    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle(name='SectionTitle',
                              parent=styles['Heading2'],
                              spaceAfter=12,
                              textColor=colors.HexColor('#f15822')))

    story = []

    # Title
    title = Paragraph("SE Team Manager Report", styles['Title'])
    story.append(title)
    story.append(Spacer(1, 12))

    # Date range
    date_text = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    if start_date or end_date:
        date_text += f" | Date Range: {start_date or 'Beginning'} to {end_date or 'Now'}"
    story.append(Paragraph(date_text, styles['Normal']))
    story.append(Spacer(1, 24))

    # Team Members Section
    if data['team_members']:
        story.append(Paragraph("Team Members", styles['SectionTitle']))
        table_data = [['Name', 'Email', 'Region', 'Location', 'Rep 1', 'Rep 2', 'Rep 3', 'Rep 4', 'Role']]
        for member in data['team_members']:
            table_data.append([
                member.name,
                member.email,
                member.region,
                member.location or '-',
                member.aligned_rep or '-',
                member.aligned_rep_2 or '-',
                member.aligned_rep_3 or '-',
                member.aligned_rep_4 or '-',
                member.role
            ])
        table = Table(table_data, colWidths=[1*inch, 1.2*inch, 0.6*inch, 0.7*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch, 0.8*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f15822')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        story.append(table)
        story.append(Spacer(1, 24))

    # 1-1 Meetings Section
    if data['one_on_ones']:
        story.append(Paragraph("1-1 Meetings", styles['SectionTitle']))
        for meeting in data['one_on_ones']:
            story.append(Paragraph(f"<b>{meeting.team_member.name}</b> - {meeting.date.strftime('%Y-%m-%d')}", styles['Normal']))
            if meeting.mood:
                story.append(Paragraph(f"Mood: {meeting.mood}", styles['Normal']))
            if meeting.notes:
                story.append(Paragraph(f"Notes: {meeting.notes[:500]}", styles['Normal']))
            if meeting.action_items:
                story.append(Paragraph(f"Action Items: {meeting.action_items[:500]}", styles['Normal']))
            story.append(Spacer(1, 12))
        story.append(Spacer(1, 12))

    # Opportunities Section
    if data['opportunities']:
        story.append(Paragraph("Opportunities", styles['SectionTitle']))
        table_data = [['Name', 'Account', 'Stage', 'Value', 'SE', 'Close Date']]
        for opp in data['opportunities']:
            table_data.append([
                opp.name[:30],
                opp.account[:20],
                opp.stage,
                f"${opp.value:,.0f}",
                opp.team_member.name,
                opp.close_date.strftime('%Y-%m-%d') if opp.close_date else '-'
            ])
        table = Table(table_data, colWidths=[1.5*inch, 1.2*inch, 1*inch, 0.8*inch, 1.2*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#2e7d32')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        story.append(table)
        story.append(Spacer(1, 24))

    # Live POVs Section
    if data.get('live_povs'):
        story.append(Paragraph("Live POVs", styles['SectionTitle']))
        table_data = [['Name', 'Account', 'Stage', 'Value', 'SE', 'Close Date']]
        for pov in data['live_povs']:
            table_data.append([
                pov.name[:30],
                pov.account[:20],
                pov.stage,
                f"${pov.value:,.0f}",
                pov.team_member.name,
                pov.close_date.strftime('%Y-%m-%d') if pov.close_date else '-'
            ])
        table = Table(table_data, colWidths=[1.5*inch, 1.2*inch, 1*inch, 0.8*inch, 1.2*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ed6c02')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        story.append(table)
        story.append(Spacer(1, 24))

    # Support Cases Section
    if data['support_cases']:
        story.append(Paragraph("Support Cases", styles['SectionTitle']))
        table_data = [['Title', 'Customer', 'Status', 'Priority', 'SE', 'Created']]
        for case in data['support_cases']:
            table_data.append([
                case.title[:30],
                case.customer[:20] if case.customer else '-',
                case.status,
                case.priority,
                case.team_member.name,
                case.created_at.strftime('%Y-%m-%d')
            ])
        table = Table(table_data, colWidths=[1.5*inch, 1.2*inch, 1*inch, 0.8*inch, 1.2*inch, 1*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#ffc107')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        story.append(table)
        story.append(Spacer(1, 24))

    # Follow-ups Section
    if data['follow_ups']:
        story.append(Paragraph("Follow-ups", styles['SectionTitle']))
        table_data = [['Title', 'Due Date', 'Status', 'Priority', 'Team Member']]
        for item in data['follow_ups']:
            table_data.append([
                item.title[:30],
                item.due_date.strftime('%Y-%m-%d'),
                item.status,
                item.priority,
                item.team_member.name if item.team_member else '-'
            ])
        table = Table(table_data, colWidths=[2*inch, 1*inch, 1*inch, 0.8*inch, 1.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1822e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('FONTSIZE', (0, 1), (-1, -1), 9),
        ]))
        story.append(table)
        story.append(Spacer(1, 24))

    # Notes Section
    if data['notes']:
        story.append(Paragraph("Notes", styles['SectionTitle']))
        for note in data['notes']:
            story.append(Paragraph(f"<b>{note.title}</b> - {note.created_at.strftime('%Y-%m-%d')}", styles['Normal']))
            if note.team_member:
                story.append(Paragraph(f"Team Member: {note.team_member.name}", styles['Normal']))
            if note.tags:
                story.append(Paragraph(f"Tags: {note.tags}", styles['Normal']))
            if note.content:
                story.append(Paragraph(f"{note.content[:500]}", styles['Normal']))
            story.append(Spacer(1, 12))

    # Skill Matrix Section
    if data.get('skill_matrix'):
        skills = ['Password Safe', 'EPM Win-Mac', 'EPM-L', 'Remote Support', 'PRA', 'AD Bridge', 'Insights', 'Entitle']
        story.append(Paragraph("Skill Matrix", styles['SectionTitle']))
        table_data = [['SE', 'Region'] + skills]
        for entry in data['skill_matrix']:
            member = entry['member']
            ratings = entry['ratings']
            row = [member.name, member.region]
            for skill in skills:
                row.append(ratings.get(skill, "Haven't Started"))
            table_data.append(row)
        col_widths = [1.1*inch, 0.7*inch] + [0.7*inch] * len(skills)
        table = Table(table_data, colWidths=col_widths)
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#f1822e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 8),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.lightgrey),
            ('FONTSIZE', (0, 1), (-1, -1), 7),
        ]))
        story.append(table)
        story.append(Spacer(1, 24))

    doc.build(story)
    return filepath


def generate_csv_report(data, start_date=None, end_date=None):
    """Generate a CSV report with selected items."""
    fd, filepath = tempfile.mkstemp(suffix='.csv')
    os.close(fd)

    with open(filepath, 'w', newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)

        # Header
        writer.writerow(['SE Team Manager Report'])
        writer.writerow([f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}'])
        if start_date or end_date:
            writer.writerow([f'Date Range: {start_date or "Beginning"} to {end_date or "Now"}'])
        writer.writerow([])

        # Team Members
        if data['team_members']:
            writer.writerow(['TEAM MEMBERS'])
            writer.writerow(['Name', 'Email', 'Region', 'Location', 'Rep 1', 'Rep 1 Location', 'Rep 2', 'Rep 2 Location', 'Rep 3', 'Rep 3 Location', 'Rep 4', 'Rep 4 Location', 'Role', 'Created'])
            for member in data['team_members']:
                writer.writerow([
                    member.name,
                    member.email,
                    member.region,
                    member.location or '',
                    member.aligned_rep or '',
                    member.aligned_rep_location or '',
                    member.aligned_rep_2 or '',
                    member.aligned_rep_2_location or '',
                    member.aligned_rep_3 or '',
                    member.aligned_rep_3_location or '',
                    member.aligned_rep_4 or '',
                    member.aligned_rep_4_location or '',
                    member.role,
                    member.created_at.strftime('%Y-%m-%d')
                ])
            writer.writerow([])

        # 1-1 Meetings
        if data['one_on_ones']:
            writer.writerow(['1-1 MEETINGS'])
            writer.writerow(['Team Member', 'Date', 'Mood', 'Notes', 'Action Items'])
            for meeting in data['one_on_ones']:
                writer.writerow([
                    meeting.team_member.name,
                    meeting.date.strftime('%Y-%m-%d'),
                    meeting.mood or '',
                    meeting.notes or '',
                    meeting.action_items or ''
                ])
            writer.writerow([])

        # Opportunities
        if data['opportunities']:
            writer.writerow(['OPPORTUNITIES'])
            writer.writerow(['Name', 'Account', 'Stage', 'Value', 'SE', 'Close Date', 'Created', 'Updated'])
            for opp in data['opportunities']:
                writer.writerow([
                    opp.name,
                    opp.account,
                    opp.stage,
                    opp.value,
                    opp.team_member.name,
                    opp.close_date.strftime('%Y-%m-%d') if opp.close_date else '',
                    opp.created_at.strftime('%Y-%m-%d'),
                    opp.updated_at.strftime('%Y-%m-%d')
                ])
            writer.writerow([])

        # Live POVs
        if data.get('live_povs'):
            writer.writerow(['LIVE POVS'])
            writer.writerow(['Name', 'Account', 'Stage', 'Value', 'SE', 'Close Date', 'Created', 'Updated'])
            for pov in data['live_povs']:
                writer.writerow([
                    pov.name,
                    pov.account,
                    pov.stage,
                    pov.value,
                    pov.team_member.name,
                    pov.close_date.strftime('%Y-%m-%d') if pov.close_date else '',
                    pov.created_at.strftime('%Y-%m-%d'),
                    pov.updated_at.strftime('%Y-%m-%d')
                ])
            writer.writerow([])

        # Support Cases
        if data['support_cases']:
            writer.writerow(['SUPPORT CASES'])
            writer.writerow(['Title', 'Customer', 'Status', 'Priority', 'SE', 'Description', 'Created', 'Resolved'])
            for case in data['support_cases']:
                writer.writerow([
                    case.title,
                    case.customer or '',
                    case.status,
                    case.priority,
                    case.team_member.name,
                    case.description or '',
                    case.created_at.strftime('%Y-%m-%d'),
                    case.resolved_at.strftime('%Y-%m-%d') if case.resolved_at else ''
                ])
            writer.writerow([])

        # Follow-ups
        if data['follow_ups']:
            writer.writerow(['FOLLOW-UPS'])
            writer.writerow(['Title', 'Description', 'Due Date', 'Status', 'Priority', 'Team Member', 'Related Type', 'Related ID'])
            for item in data['follow_ups']:
                writer.writerow([
                    item.title,
                    item.description or '',
                    item.due_date.strftime('%Y-%m-%d'),
                    item.status,
                    item.priority,
                    item.team_member.name if item.team_member else '',
                    item.related_type or '',
                    item.related_id or ''
                ])
            writer.writerow([])

        # Notes
        if data['notes']:
            writer.writerow(['NOTES'])
            writer.writerow(['Title', 'Content', 'Tags', 'Team Member', 'Created'])
            for note in data['notes']:
                writer.writerow([
                    note.title,
                    note.content or '',
                    note.tags or '',
                    note.team_member.name if note.team_member else '',
                    note.created_at.strftime('%Y-%m-%d')
                ])
            writer.writerow([])

        # Skill Matrix
        if data.get('skill_matrix'):
            skills = ['Password Safe', 'EPM Win-Mac', 'EPM-L', 'Remote Support', 'PRA', 'AD Bridge', 'Insights', 'Entitle']
            writer.writerow(['SKILL MATRIX'])
            writer.writerow(['SE', 'Region'] + skills)
            for entry in data['skill_matrix']:
                member = entry['member']
                ratings = entry['ratings']
                row = [member.name, member.region]
                for skill in skills:
                    row.append(ratings.get(skill, "Haven't Started"))
                writer.writerow(row)

    return filepath
