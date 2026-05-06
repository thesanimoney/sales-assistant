from schemas import AnalysisReport, MeetingType, TechnicalAnalysisReport
from pathlib import Path

PRIMARY = "#4285F4"
CHARCOAL = "#434343"
LIGHT_BG = "#F5F8FF"
MUTED = "#8A94A6"
BORDER = "#E4E9F2"
SUCCESS = "#34A853"
WARNING = "#FBBC04"
DANGER = "#EA4335"
DANGER_BG = "#FDECEA"
WARNING_BG = "#FEF7E0"


def sales_report_to_html(
    report: AnalysisReport,
    meeting_type: MeetingType,
    meeting_date: str,
    duration_minutes: float,
    filepath: Path,
) -> str:
    """Convert AnalysisReport to DSUA-branded HTML email."""

    def status_color(status: str) -> str:
        return {
            "strong": SUCCESS,
            "partial": WARNING,
            "weak": WARNING,
            "missing": DANGER,
        }.get(status.lower(), MUTED)

    def score_color(score: int) -> str:
        if score >= 8:
            return SUCCESS
        if score >= 5:
            return WARNING
        return DANGER

    def score_badge(score: int) -> str:
        return f"""
        <span style="display:inline-block;padding:3px 10px;background:{score_color(score)};color:#ffffff;border-radius:12px;font-size:12px;font-weight:bold;font-family:Arial,sans-serif;">
            {score}/10
        </span>
        """

    # Scorecard rows
    scorecard_rows = "".join(
        f"""
        <tr>
            <td style="padding:10px 12px;border-bottom:1px solid {BORDER};font-family:Arial,sans-serif;font-size:13px;color:{CHARCOAL};">{label}</td>
            <td style="padding:10px 12px;border-bottom:1px solid {BORDER};text-align:center;">{score_badge(item.score)}</td>
            <td style="padding:10px 12px;border-bottom:1px solid {BORDER};font-family:Arial,sans-serif;font-size:13px;color:{MUTED};">{item.comment}</td>
        </tr>
    """
        for label, item in [
            ("Discovery Depth", report.scorecard.discovery_depth),
            ("Decision Process Clarity", report.scorecard.decision_process_clarity),
            ("Budget Signals", report.scorecard.budget_signals),
            ("Competition Awareness", report.scorecard.competition_awareness),
            ("Value Articulation", report.scorecard.value_articulation),
            ("Next Step Quality", report.scorecard.next_step_quality),
            ("Rapport & Trust", report.scorecard.rapport_and_trust),
            ("Listening Ratio", report.scorecard.listening_ratio),
            ("SPIN Execution", report.scorecard.spin_execution),
        ]
    )

    # SPIN sections
    spin_rows = "".join(
        f"""
        <tr>
            <td style="padding:10px 12px;border-bottom:1px solid {BORDER};font-family:Arial,sans-serif;font-size:13px;color:{CHARCOAL};font-weight:bold;">{label}</td>
            <td style="padding:10px 12px;border-bottom:1px solid {BORDER};text-align:center;">{score_badge(section.score)}</td>
            <td style="padding:10px 12px;border-bottom:1px solid {BORDER};font-family:Arial,sans-serif;font-size:13px;color:{MUTED};">
            {"<br>".join("• " + g for g in section.critical_gaps) if section.critical_gaps else "<i>No critical gaps</i>"}
            </td>
        </tr>
    """
        for label, section in [
            ("Situation", report.spin_analysis.situation),
            ("Problem", report.spin_analysis.problem),
            ("Implication", report.spin_analysis.implication),
            ("Need-Payoff", report.spin_analysis.need_payoff),
        ]
    )

    # MEDDIC rows
    meddic_rows = "".join(
        f"""
        <tr>
            <td style="padding:10px 12px;border-bottom:1px solid {BORDER};font-family:Arial,sans-serif;font-size:13px;color:{CHARCOAL};font-weight:bold;">{label}</td>
            <td style="padding:10px 12px;border-bottom:1px solid {BORDER};text-align:center;">
                <span style="display:inline-block;padding:3px 10px;background:{status_color(pillar.status.value if hasattr(pillar.status, 'value') else pillar.status)};color:#ffffff;border-radius:12px;font-size:11px;font-weight:bold;text-transform:uppercase;font-family:Arial,sans-serif;">
                    {pillar.status.value if hasattr(pillar.status, 'value') else pillar.status}
                </span>
            </td>
            <td style="padding:10px 12px;border-bottom:1px solid {BORDER};font-family:Arial,sans-serif;font-size:13px;color:{MUTED};">{pillar.gap}</td>
        </tr>
    """
        for label, pillar in [
            ("Metrics", report.meddic.metrics),
            ("Economic Buyer", report.meddic.economic_buyer),
            ("Decision Criteria", report.meddic.decision_criteria),
            ("Decision Process", report.meddic.decision_process),
            ("Identify Pain", report.meddic.identify_pain),
            ("Champion", report.meddic.champion),
        ]
    )

    # Missed questions
    missed_html = "".join(
        f"""
        <tr>
            <td style="padding:12px;border-bottom:1px solid {BORDER};vertical-align:top;">
                <div style="font-family:Arial,sans-serif;font-size:13px;color:{CHARCOAL};font-weight:bold;margin-bottom:4px;">{q.question}</div>
                <div style="font-family:Arial,sans-serif;font-size:11px;color:{PRIMARY};text-transform:uppercase;font-weight:bold;margin-bottom:4px;">[{q.type.value if hasattr(q.type, 'value') else q.type}]</div>
                <div style="font-family:Arial,sans-serif;font-size:12px;color:{MUTED};margin-bottom:4px;"><b>Why:</b> {q.why_it_matters}</div>
                <div style="font-family:Arial,sans-serif;font-size:12px;color:{MUTED};"><b>Best moment:</b> {q.best_moment_to_ask}</div>
            </td>
        </tr>
    """
        for q in report.missed_questions
    )

    # Next actions
    actions_html = "".join(
        f"""
        <tr>
            <td style="padding:12px;border-bottom:1px solid {BORDER};vertical-align:top;width:30px;">
                <div style="background:{PRIMARY};color:#ffffff;width:28px;height:28px;border-radius:50%;text-align:center;line-height:28px;font-family:Arial,sans-serif;font-size:13px;font-weight:bold;">{a.priority}</div>
            </td>
            <td style="padding:12px;border-bottom:1px solid {BORDER};vertical-align:top;">
                <div style="font-family:Arial,sans-serif;font-size:13px;color:{CHARCOAL};font-weight:bold;margin-bottom:4px;">{a.action}</div>
                <div style="font-family:Arial,sans-serif;font-size:12px;color:{MUTED};margin-bottom:4px;">{a.why}</div>
                <div style="font-family:Arial,sans-serif;font-size:11px;color:{PRIMARY};font-weight:bold;">⏱ {a.do_by}</div>
            </td>
        </tr>
    """
        for a in report.next_actions
    )

    # Objections
    objections_html = "".join(
        f"""
        <div style="padding:14px 16px;background:#ffffff;border:1px solid {BORDER};border-radius:6px;margin-bottom:10px;">
            <div style="font-family:Arial,sans-serif;font-size:13px;color:{CHARCOAL};font-weight:bold;margin-bottom:8px;">"{o.objection}"</div>
            <div style="display:inline-block;padding:2px 8px;background:{LIGHT_BG};color:{PRIMARY};font-family:Arial,sans-serif;font-size:11px;font-weight:bold;text-transform:uppercase;border-radius:4px;margin-bottom:10px;">{o.type.value if hasattr(o.type, 'value') else o.type}</div>
            <div style="font-family:Arial,sans-serif;font-size:12px;color:{MUTED};margin-bottom:6px;"><b style="color:{CHARCOAL};">Handled:</b> {o.how_it_was_handled}</div>
            <div style="font-family:Arial,sans-serif;font-size:12px;color:{MUTED};margin-bottom:6px;"><b style="color:{CHARCOAL};">Should have been:</b> {o.how_it_should_have_been_handled}</div>
            <div style="margin-top:8px;padding:10px;background:{LIGHT_BG};border-left:3px solid {PRIMARY};font-family:Arial,sans-serif;font-size:12px;color:{CHARCOAL};font-style:italic;">{o.better_language}</div>
        </div>
    """
        for o in report.objections
    )

    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Call Analysis: {report.meeting_title}</title>
</head>
<body style="margin:0;padding:0;background:#F5F8FF;font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:#F5F8FF;padding:30px 0;">
<tr><td align="center">

<table width="720" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(66,133,244,0.08);">

    <!-- Header -->
    <tr>
        <td style="background:{PRIMARY};padding:28px 32px;">
            <div style="font-family:Arial,sans-serif;color:#ffffff;font-size:11px;font-weight:bold;letter-spacing:1.5px;text-transform:uppercase;opacity:0.85;margin-bottom:6px;">
                Data Science UA · Call Analysis
            </div>
            <div style="font-family:Arial,sans-serif;color:#ffffff;font-size:22px;font-weight:bold;line-height:1.3;">
                {report.meeting_title}
            </div>
            <div style="font-family:Arial,sans-serif;color:#ffffff;font-size:12px;opacity:0.8;margin-top:8px;">
                {meeting_date} · {duration_minutes:.0f} min · {meeting_type.upper()}
            </div>
        </td>
    </tr>

    <!-- TL;DR -->
    <tr>
        <td style="padding:28px 32px;border-bottom:1px solid {BORDER};">
            <div style="font-family:Arial,sans-serif;color:{PRIMARY};font-size:11px;font-weight:bold;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:10px;">
                TL;DR
            </div>
            <div style="font-family:Arial,sans-serif;color:{CHARCOAL};font-size:14px;line-height:1.6;margin-bottom:16px;">
                {report.tldr}
            </div>
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td width="33%" style="padding-right:10px;vertical-align:top;">
                        <div style="background:{LIGHT_BG};padding:14px;border-radius:6px;">
                            <div style="font-family:Arial,sans-serif;color:{MUTED};font-size:10px;font-weight:bold;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Deal Health</div>
                            <div style="font-family:Arial,sans-serif;color:{CHARCOAL};font-size:13px;line-height:1.4;">{report.deal_health}</div>
                        </div>
                    </td>
                    <td width="34%" style="padding:0 5px;vertical-align:top;">
                        <div style="background:{LIGHT_BG};padding:14px;border-radius:6px;">
                            <div style="font-family:Arial,sans-serif;color:{MUTED};font-size:10px;font-weight:bold;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Biggest Problem</div>
                            <div style="font-family:Arial,sans-serif;color:{CHARCOAL};font-size:13px;line-height:1.4;">{report.biggest_problem}</div>
                        </div>
                    </td>
                    <td width="33%" style="padding-left:10px;vertical-align:top;">
                        <div style="background:{LIGHT_BG};padding:14px;border-radius:6px;">
                            <div style="font-family:Arial,sans-serif;color:{MUTED};font-size:10px;font-weight:bold;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Top Next Action</div>
                            <div style="font-family:Arial,sans-serif;color:{CHARCOAL};font-size:13px;line-height:1.4;">{report.most_important_next_action}</div>
                        </div>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
    
    <!-- Scorecard -->
    <tr>
        <td style="padding:28px 32px;border-bottom:1px solid {BORDER};">
            <div style="font-family:Arial,sans-serif;color:{PRIMARY};font-size:11px;font-weight:bold;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:14px;">
                Scorecard · Overall {report.scorecard.overall.score}/10
            </div>
            <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid {BORDER};border-radius:6px;overflow:hidden;">
                <tr style="background:{LIGHT_BG};">
                    <th style="padding:10px 12px;text-align:left;font-family:Arial,sans-serif;font-size:11px;color:{MUTED};text-transform:uppercase;font-weight:bold;">Dimension</th>
                    <th style="padding:10px 12px;text-align:center;font-family:Arial,sans-serif;font-size:11px;color:{MUTED};text-transform:uppercase;font-weight:bold;width:80px;">Score</th>
                    <th style="padding:10px 12px;text-align:left;font-family:Arial,sans-serif;font-size:11px;color:{MUTED};text-transform:uppercase;font-weight:bold;">Comment</th>
                </tr>
                {scorecard_rows}
            </table>
            <div style="margin-top:14px;padding:12px 16px;background:{LIGHT_BG};border-left:4px solid {PRIMARY};border-radius:4px;font-family:Arial,sans-serif;font-size:13px;color:{CHARCOAL};font-style:italic;">
                <b>Overall:</b> {report.scorecard.overall.comment}
            </div>
        </td>
    </tr>

    <!-- SPIN -->
    <tr>
        <td style="padding:28px 32px;border-bottom:1px solid {BORDER};">
            <div style="font-family:Arial,sans-serif;color:{PRIMARY};font-size:11px;font-weight:bold;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:14px;">
                SPIN Analysis · Overall {report.spin_analysis.overall_score}/10
            </div>
            <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid {BORDER};border-radius:6px;overflow:hidden;">
                <tr style="background:{LIGHT_BG};">
                    <th style="padding:10px 12px;text-align:left;font-family:Arial,sans-serif;font-size:11px;color:{MUTED};text-transform:uppercase;font-weight:bold;width:130px;">Type</th>
                    <th style="padding:10px 12px;text-align:center;font-family:Arial,sans-serif;font-size:11px;color:{MUTED};text-transform:uppercase;font-weight:bold;width:80px;">Score</th>
                    <th style="padding:10px 12px;text-align:left;font-family:Arial,sans-serif;font-size:11px;color:{MUTED};text-transform:uppercase;font-weight:bold;">Critical Gaps</th>
                </tr>
                
                {spin_rows}
            </table>
            <div style="margin-top:14px;padding:12px 16px;background:{LIGHT_BG};border-left:4px solid {PRIMARY};border-radius:4px;font-family:Arial,sans-serif;font-size:13px;color:{CHARCOAL};font-style:italic;">
                {report.spin_analysis.overall_verdict}
            </div>
        </td>
    </tr>

    <!-- MEDDIC -->
    <tr>
        <td style="padding:28px 32px;border-bottom:1px solid {BORDER};">
            <div style="font-family:Arial,sans-serif;color:{PRIMARY};font-size:11px;font-weight:bold;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:14px;">
                MEDDIC Qualification · Overall {report.meddic.overall_score}/10
            </div>
            <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid {BORDER};border-radius:6px;overflow:hidden;">
                <tr style="background:{LIGHT_BG};">
                    <th style="padding:10px 12px;text-align:left;font-family:Arial,sans-serif;font-size:11px;color:{MUTED};text-transform:uppercase;font-weight:bold;width:160px;">Pillar</th>
                    <th style="padding:10px 12px;text-align:center;font-family:Arial,sans-serif;font-size:11px;color:{MUTED};text-transform:uppercase;font-weight:bold;width:100px;">Status</th>
                    <th style="padding:10px 12px;text-align:left;font-family:Arial,sans-serif;font-size:11px;color:{MUTED};text-transform:uppercase;font-weight:bold;">Gap</th>
                </tr>
                {meddic_rows}
            </table>
        </td>
    </tr>

    <!-- Missed questions -->
    <tr>
        <td style="padding:28px 32px;border-bottom:1px solid {BORDER};">
            <div style="font-family:Arial,sans-serif;color:{PRIMARY};font-size:11px;font-weight:bold;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:14px;">
                Missed Questions
            </div>
            <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid {BORDER};border-radius:6px;overflow:hidden;">
                {missed_html}
            </table>
        </td>
    </tr>

    <!-- Objections -->
    <tr>
        <td style="padding:28px 32px;border-bottom:1px solid {BORDER};">
            <div style="font-family:Arial,sans-serif;color:{PRIMARY};font-size:11px;font-weight:bold;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:14px;">
                Objections Analysis
            </div>
            {objections_html}
        </td>
    </tr>

    <!-- Next actions -->
    <tr>
        <td style="padding:28px 32px;border-bottom:1px solid {BORDER};">
            <div style="font-family:Arial,sans-serif;color:{PRIMARY};font-size:11px;font-weight:bold;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:14px;">
                Recommended Next Actions
            </div>
            <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid {BORDER};border-radius:6px;overflow:hidden;">
                {actions_html}
            </table>
        </td>
    </tr>

    <!-- Follow-up email draft -->
    <tr>
        <td style="padding:28px 32px;border-bottom:1px solid {BORDER};">
            <div style="font-family:Arial,sans-serif;color:{PRIMARY};font-size:11px;font-weight:bold;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:14px;">
                Follow-up Email Draft
            </div>
            <div style="background:{LIGHT_BG};border-radius:6px;padding:18px 20px;">
                <div style="font-family:Arial,sans-serif;font-size:12px;color:{MUTED};margin-bottom:6px;"><b>Subject:</b></div>
                <div style="font-family:Arial,sans-serif;font-size:14px;color:{CHARCOAL};font-weight:bold;margin-bottom:14px;">{report.follow_up_email.subject}</div>
                <div style="font-family:Arial,sans-serif;font-size:13px;color:{CHARCOAL};line-height:1.6;white-space:pre-wrap;">{report.follow_up_email.body}</div>
            </div>
        </td>
    </tr>

    <!-- Footer -->
    <tr>
        <td style="background:{LIGHT_BG};padding:20px 32px;text-align:center;">
            <div style="font-family:Arial,sans-serif;font-size:11px;color:{MUTED};">
                Generated by AI Call Analyst · <span style="color:{PRIMARY};font-weight:bold;">Data Science UA</span>
            </div>
            <div style="font-family:Arial,sans-serif;font-size:10px;color:{MUTED};margin-top:4px;">
                Participants: {", ".join(report.participants)}
            </div>
        </td>
    </tr>

</table>

</td></tr>
</table>
</body>
</html>"""

    filepath.write_text(html, encoding="utf-8")
    return html


# ---Technical Report Generation---
def technical_report_to_html(
    report: TechnicalAnalysisReport,
    meeting_type: MeetingType,
    meeting_date: str,
    duration_minutes: float,
    filepath: Path,
) -> str:
    """Convert TechnicalAnalysisReport to DSUA-branded HTML email."""

    def score_color(score: int) -> str:
        if score >= 8:
            return SUCCESS
        if score >= 5:
            return WARNING
        return DANGER

    def severity_color(severity: str) -> str:
        return {
            "high": DANGER,
            "medium": WARNING,
            "low": SUCCESS,
        }.get(severity.lower(), MUTED)

    def severity_bg(severity: str) -> str:
        return {
            "high": DANGER_BG,
            "medium": WARNING_BG,
            "low": LIGHT_BG,
        }.get(severity.lower(), LIGHT_BG)

    def score_badge(score: int) -> str:
        return f"""
        <span style="display:inline-block;padding:3px 10px;background:{score_color(score)};color:#ffffff;border-radius:12px;font-size:12px;font-weight:bold;font-family:Arial,sans-serif;">
            {score}/10
        </span>
        """

    def chip(text: str, bg: str = LIGHT_BG, color: str = PRIMARY) -> str:
        """Small inline tag/chip element for categories, statuses, etc."""
        return (
            f'<span style="display:inline-block;padding:4px 10px;background:{bg};color:{color};'
            f"font-family:Arial,sans-serif;font-size:11px;font-weight:bold;text-transform:uppercase;"
            f'border-radius:4px;margin:0 6px 8px 0;">{text}</span>'
        )

    def section_kicker(text: str) -> str:
        """The small uppercase section label used at the top of each card."""
        return (
            f'<div style="font-family:Arial,sans-serif;color:{PRIMARY};font-size:11px;'
            f'font-weight:bold;letter-spacing:1.5px;text-transform:uppercase;margin-bottom:14px;">'
            f"{text}</div>"
        )

    def bullet_list(items: list[str], color: str = CHARCOAL) -> str:
        """Render a list of strings as styled bullets (table-friendly)."""
        if not items:
            return f'<div style="font-family:Arial,sans-serif;font-size:13px;color:{MUTED};font-style:italic;">None identified</div>'
        rows = "".join(
            f'<div style="font-family:Arial,sans-serif;font-size:13px;color:{color};line-height:1.6;margin-bottom:6px;">• {item}</div>'
            for item in items
        )
        return rows

    # --- Snapshot: stack chips ---
    stack_chips = "".join(
    f"""<span style="
        display:inline-block;
        background:#ffffff;
        color:{PRIMARY};
        font-family:Arial,sans-serif;
        font-size:12px;
        font-weight:600;
        padding:6px 12px;
        margin:0 6px 6px 0;
        border-radius:14px;
        border:1px solid {PRIMARY};
        white-space:nowrap;
    ">{item}</span>"""
    for item in report.snapshot.systems_and_stack
)

    # --- Scorecard rows ---
    scorecard_rows = "".join(
        f"""
        <tr>
            <td style="padding:10px 12px;border-bottom:1px solid {BORDER};font-family:Arial,sans-serif;font-size:13px;color:{CHARCOAL};">{label}</td>
            <td style="padding:10px 12px;border-bottom:1px solid {BORDER};text-align:center;">{score_badge(item.score)}</td>
            <td style="padding:10px 12px;border-bottom:1px solid {BORDER};font-family:Arial,sans-serif;font-size:13px;color:{MUTED};">{item.comment}</td>
        </tr>
        """
        for label, item in [
            ("Problem Clarity", report.scorecard.problem_clarity),
            ("Solution Alignment", report.scorecard.solution_alignment),
            ("Technical Depth", report.scorecard.technical_depth),
            ("Requirement Completeness", report.scorecard.requirement_completeness),
            ("Risk Identification", report.scorecard.risk_identification),
            ("Next Step Quality", report.scorecard.next_step_quality),
        ]
    )

    # --- What went well / wrong: shared moment renderer ---
    def render_moments(moments, accent_color: str, accent_bg: str) -> str:
        if not moments:
            return f'<div style="font-family:Arial,sans-serif;font-size:13px;color:{MUTED};font-style:italic;">None identified</div>'
        return "".join(
            f"""
            <div style="padding:14px 16px;background:#ffffff;border:1px solid {BORDER};border-left:4px solid {accent_color};border-radius:6px;margin-bottom:10px;">
                <div style="font-family:Arial,sans-serif;font-size:13px;color:{CHARCOAL};font-weight:bold;margin-bottom:8px;">{m.moment}</div>
                <div style="background:{accent_bg};border-radius:4px;padding:10px 12px;font-family:Arial,sans-serif;font-size:12px;color:{CHARCOAL};font-style:italic;margin-bottom:8px;">"{m.quote}"</div>
                <div style="font-family:Arial,sans-serif;font-size:12px;color:{MUTED};"><b style="color:{CHARCOAL};">Why it matters:</b> {m.why_it_matters}</div>
            </div>
            """
            for m in moments
        )

    went_well_html = render_moments(report.what_went_well, SUCCESS, LIGHT_BG)
    went_wrong_html = render_moments(report.what_went_wrong, DANGER, DANGER_BG)

    # --- Missed questions ---
    missed_html = "".join(
        f"""
        <tr>
            <td style="padding:12px;border-bottom:1px solid {BORDER};vertical-align:top;">
                <div style="font-family:Arial,sans-serif;font-size:13px;color:{CHARCOAL};font-weight:bold;margin-bottom:6px;">{q.question}</div>
                <div style="margin-bottom:6px;">{chip(q.category, bg=LIGHT_BG, color=PRIMARY)}</div>
                <div style="font-family:Arial,sans-serif;font-size:12px;color:{MUTED};margin-bottom:4px;"><b>Why:</b> {q.why_it_matters}</div>
                <div style="font-family:Arial,sans-serif;font-size:12px;color:{MUTED};"><b>Best moment:</b> {q.best_moment_to_ask}</div>
            </td>
        </tr>
        """
        for q in report.missed_questions
    )

    # --- Requirements: 4-quadrant grid ---
    def req_quadrant(title: str, items: list[str]) -> str:
        return f"""
        <div style="background:{LIGHT_BG};border-radius:6px;padding:14px 16px;height:100%;">
            <div style="font-family:Arial,sans-serif;color:{MUTED};font-size:10px;font-weight:bold;text-transform:uppercase;letter-spacing:1px;margin-bottom:10px;">{title}</div>
            {bullet_list(items)}
        </div>
        """

    requirements_html = f"""
    <table width="100%" cellpadding="0" cellspacing="0">
        <tr>
            <td width="50%" style="padding:0 6px 12px 0;vertical-align:top;">
                {req_quadrant("Functional", report.requirements.functional)}
            </td>
            <td width="50%" style="padding:0 0 12px 6px;vertical-align:top;">
                {req_quadrant("Non-functional", report.requirements.non_functional)}
            </td>
        </tr>
        <tr>
            <td width="50%" style="padding:0 6px 0 0;vertical-align:top;">
                {req_quadrant("Constraints", report.requirements.constraints)}
            </td>
            <td width="50%" style="padding:0 0 0 6px;vertical-align:top;">
                {req_quadrant("Assumptions (unverified)", report.requirements.assumptions)}
            </td>
        </tr>
    </table>
    """

    # --- Risks (sorted by severity: high → medium → low) ---
    severity_rank = {"high": 0, "medium": 1, "low": 2}
    sorted_risks = sorted(
        report.risks,
        key=lambda r: severity_rank.get(
            (
                r.severity.lower()
                if hasattr(r.severity, "lower")
                else r.severity.value.lower()
            ),
            3,
        ),
    )

    risks_html = (
        "".join(
            f"""
        <div style="padding:14px 16px;background:#ffffff;border:1px solid {BORDER};border-left:4px solid {severity_color(r.severity if isinstance(r.severity, str) else r.severity.value)};border-radius:6px;margin-bottom:10px;">
            <div style="margin-bottom:8px;">
                {chip(r.severity if isinstance(r.severity, str) else r.severity.value, bg=severity_bg(r.severity if isinstance(r.severity, str) else r.severity.value), color=severity_color(r.severity if isinstance(r.severity, str) else r.severity.value))}
                {chip(r.category if isinstance(r.category, str) else r.category.value, bg=LIGHT_BG, color=PRIMARY)}
            </div>
            <div style="font-family:Arial,sans-serif;font-size:13px;color:{CHARCOAL};font-weight:bold;margin-bottom:6px;">{r.risk}</div>
            <div style="font-family:Arial,sans-serif;font-size:12px;color:{MUTED};margin-bottom:4px;"><b style="color:{CHARCOAL};">Evidence:</b> {r.evidence}</div>
            <div style="font-family:Arial,sans-serif;font-size:12px;color:{MUTED};"><b style="color:{CHARCOAL};">Mitigation:</b> {r.mitigation}</div>
        </div>
        """
            for r in sorted_risks
        )
        or f'<div style="font-family:Arial,sans-serif;font-size:13px;color:{MUTED};font-style:italic;">No major risks identified</div>'
    )

    # --- Open questions ---
    open_questions_html = (
        "".join(
            f"""
        <tr>
            <td style="padding:12px;border-bottom:1px solid {BORDER};vertical-align:top;">
                <div style="font-family:Arial,sans-serif;font-size:13px;color:{CHARCOAL};font-weight:bold;margin-bottom:6px;">❓ {q.question}</div>
                <div style="font-family:Arial,sans-serif;font-size:12px;color:{MUTED};margin-bottom:4px;"><b style="color:{CHARCOAL};">Blocks:</b> {q.blocks}</div>
                <div style="font-family:Arial,sans-serif;font-size:12px;color:{MUTED};"><b style="color:{CHARCOAL};">Owner:</b> {q.owner}</div>
            </td>
        </tr>
        """
            for q in report.open_questions
        )
        or f'<tr><td style="padding:12px;font-family:Arial,sans-serif;font-size:13px;color:{MUTED};font-style:italic;">No open questions — alignment is clean</td></tr>'
    )

    # --- Next actions ---
    actions_html = "".join(
        f"""
        <tr>
            <td style="padding:12px;border-bottom:1px solid {BORDER};vertical-align:top;width:30px;">
                <div style="background:{PRIMARY};color:#ffffff;width:28px;height:28px;border-radius:50%;text-align:center;line-height:28px;font-family:Arial,sans-serif;font-size:13px;font-weight:bold;">{a.priority}</div>
            </td>
            <td style="padding:12px;border-bottom:1px solid {BORDER};vertical-align:top;">
                <div style="font-family:Arial,sans-serif;font-size:13px;color:{CHARCOAL};font-weight:bold;margin-bottom:4px;">{a.action}</div>
                <div style="font-family:Arial,sans-serif;font-size:12px;color:{MUTED};margin-bottom:4px;">{a.why}</div>
                <div style="font-family:Arial,sans-serif;font-size:11px;color:{PRIMARY};font-weight:bold;">⏱ {a.do_by}</div>
            </td>
        </tr>
        """
        for a in report.next_actions
    )

    # --- Assemble HTML ---
    html = f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,initial-scale=1">
    <title>Technical Call Analysis: {report.meeting_title}</title>
</head>
<body style="margin:0;padding:0;background:{LIGHT_BG};font-family:Arial,sans-serif;">
<table width="100%" cellpadding="0" cellspacing="0" style="background:{LIGHT_BG};padding:30px 0;">
<tr><td align="center">

<table width="720" cellpadding="0" cellspacing="0" style="background:#ffffff;border-radius:8px;overflow:hidden;box-shadow:0 2px 8px rgba(66,133,244,0.08);">

    <!-- Header -->
    <tr>
        <td style="background:{PRIMARY};padding:28px 32px;">
            <div style="font-family:Arial,sans-serif;color:#ffffff;font-size:11px;font-weight:bold;letter-spacing:1.5px;text-transform:uppercase;opacity:0.85;margin-bottom:6px;">
                Data Science UA · Technical Call Analysis
            </div>
            <div style="font-family:Arial,sans-serif;color:#ffffff;font-size:22px;font-weight:bold;line-height:1.3;">
                {report.meeting_title}
            </div>
            <div style="font-family:Arial,sans-serif;color:#ffffff;font-size:12px;opacity:0.8;margin-top:8px;">
                {meeting_date} · {duration_minutes:.0f} min · {meeting_type.upper()}
            </div>
        </td>
    </tr>

    <!-- TL;DR -->
    <tr>
        <td style="padding:28px 32px;border-bottom:1px solid {BORDER};">
            {section_kicker("TL;DR")}
            <div style="font-family:Arial,sans-serif;color:{CHARCOAL};font-size:14px;line-height:1.6;">
                {report.tldr}
            </div>
        </td>
    </tr>

    <!-- Snapshot -->
    <tr>
        <td style="padding:28px 32px;border-bottom:1px solid {BORDER};">
            {section_kicker("Call Snapshot")}
            <table width="100%" cellpadding="0" cellspacing="0">
                <tr>
                    <td width="50%" style="padding-right:10px;vertical-align:top;">
                        <div style="background:{LIGHT_BG};padding:14px;border-radius:6px;margin-bottom:10px;">
                            <div style="font-family:Arial,sans-serif;color:{MUTED};font-size:10px;font-weight:bold;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Technical Context</div>
                            <div style="font-family:Arial,sans-serif;color:{CHARCOAL};font-size:13px;line-height:1.4;">{report.snapshot.technical_context}</div>
                        </div>
                    </td>
                    <td width="50%" style="padding-left:10px;vertical-align:top;">
                        <div style="background:{LIGHT_BG};padding:14px;border-radius:6px;margin-bottom:10px;">
                            <div style="font-family:Arial,sans-serif;color:{MUTED};font-size:10px;font-weight:bold;text-transform:uppercase;letter-spacing:1px;margin-bottom:6px;">Objective</div>
                            <div style="font-family:Arial,sans-serif;color:{CHARCOAL};font-size:13px;line-height:1.4;">{report.snapshot.objective}</div>
                        </div>
                    </td>
                </tr>
            </table>
            <div style="background:{LIGHT_BG};padding:16px;border-radius:8px;">
    <div style="font-family:Arial,sans-serif;color:{MUTED};font-size:10px;font-weight:bold;text-transform:uppercase;letter-spacing:1px;margin-bottom:12px;">
        Systems & Stack Mentioned
    </div>
    <div>{stack_chips}</div>
</div>
        </td>
    </tr>

    <!-- Scorecard -->
    <tr>
        <td style="padding:28px 32px;border-bottom:1px solid {BORDER};">
            {section_kicker(f"Scorecard · Overall {report.scorecard.overall.score}/10")}
            <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid {BORDER};border-radius:6px;overflow:hidden;">
                <tr style="background:{LIGHT_BG};">
                    <th style="padding:10px 12px;text-align:left;font-family:Arial,sans-serif;font-size:11px;color:{MUTED};text-transform:uppercase;font-weight:bold;">Dimension</th>
                    <th style="padding:10px 12px;text-align:center;font-family:Arial,sans-serif;font-size:11px;color:{MUTED};text-transform:uppercase;font-weight:bold;width:80px;">Score</th>
                    <th style="padding:10px 12px;text-align:left;font-family:Arial,sans-serif;font-size:11px;color:{MUTED};text-transform:uppercase;font-weight:bold;">Comment</th>
                </tr>
                {scorecard_rows}
            </table>
            <div style="margin-top:14px;padding:12px 16px;background:{LIGHT_BG};border-left:4px solid {PRIMARY};border-radius:4px;font-family:Arial,sans-serif;font-size:13px;color:{CHARCOAL};font-style:italic;">
                <b>Overall:</b> {report.scorecard.overall.comment}
            </div>
        </td>
    </tr>

    <!-- What went well -->
    <tr>
        <td style="padding:28px 32px;border-bottom:1px solid {BORDER};">
            {section_kicker("✓ What Went Well")}
            {went_well_html}
        </td>
    </tr>

    <!-- What went wrong -->
    <tr>
        <td style="padding:28px 32px;border-bottom:1px solid {BORDER};">
            {section_kicker("✗ What Went Wrong")}
            {went_wrong_html}
        </td>
    </tr>

    <!-- Missed technical questions -->
    <tr>
        <td style="padding:28px 32px;border-bottom:1px solid {BORDER};">
            {section_kicker("Missed Technical Questions")}
            <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid {BORDER};border-radius:6px;overflow:hidden;">
                {missed_html}
            </table>
        </td>
    </tr>

    <!-- Requirements -->
    <tr>
        <td style="padding:28px 32px;border-bottom:1px solid {BORDER};">
            {section_kicker("Requirements Extracted")}
            {requirements_html}
        </td>
    </tr>

    <!-- Risks (always visually loud) -->
    <tr>
        <td style="padding:28px 32px;border-bottom:1px solid {BORDER};background:#FFFCFA;">
            {section_kicker("⚠ Risks & Red Flags")}
            {risks_html}
        </td>
    </tr>

    <!-- Open questions -->
    <tr>
        <td style="padding:28px 32px;border-bottom:1px solid {BORDER};">
            {section_kicker("Open Questions — Need Resolution")}
            <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid {BORDER};border-radius:6px;overflow:hidden;">
                {open_questions_html}
            </table>
        </td>
    </tr>

    <!-- Next actions -->
    <tr>
        <td style="padding:28px 32px;border-bottom:1px solid {BORDER};">
            {section_kicker("Recommended Next Actions")}
            <table width="100%" cellpadding="0" cellspacing="0" style="border:1px solid {BORDER};border-radius:6px;overflow:hidden;">
                {actions_html}
            </table>
        </td>
    </tr>

    <!-- Follow-up message draft -->
    <tr>
        <td style="padding:28px 32px;border-bottom:1px solid {BORDER};">
            {section_kicker("Follow-up Message Draft")}
            <div style="background:{LIGHT_BG};border-radius:6px;padding:18px 20px;">
                <div style="font-family:Arial,sans-serif;font-size:12px;color:{MUTED};margin-bottom:6px;"><b>Subject:</b></div>
                <div style="font-family:Arial,sans-serif;font-size:14px;color:{CHARCOAL};font-weight:bold;margin-bottom:14px;">{report.follow_up_message.subject}</div>
                <div style="font-family:Arial,sans-serif;font-size:13px;color:{CHARCOAL};line-height:1.6;white-space:pre-wrap;">{report.follow_up_message.body}</div>
            </div>
        </td>
    </tr>

    <!-- Footer -->
    <tr>
        <td style="background:{LIGHT_BG};padding:20px 32px;text-align:center;">
            <div style="font-family:Arial,sans-serif;font-size:11px;color:{MUTED};">
                Generated by AI Call Analyst · <span style="color:{PRIMARY};font-weight:bold;">Data Science UA</span>
            </div>
            <div style="font-family:Arial,sans-serif;font-size:10px;color:{MUTED};margin-top:4px;">
                Participants: {", ".join(report.participants)}
            </div>
        </td>
    </tr>

</table>

</td></tr>
</table>
</body>
</html>"""

    filepath.write_text(html, encoding="utf-8")
    return html
