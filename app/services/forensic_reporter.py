"""
Forensic PDF Report Generator for the Cyber-Forensic Honeypot.
Generates professional, forensic-grade investigation reports.
"""
import os
import random
from datetime import datetime
from typing import List, Optional

from fpdf import FPDF

from app.core.logging import logger
from app.models.requests import Message
from app.models.responses import ExtractedIntelligence


class ForensicPDF(FPDF):
    """Custom PDF class with forensic report styling."""

    # Color constants (Gov-Tech palette)
    NAVY = (10, 36, 99)
    DARK_BLUE = (20, 60, 140)
    ACCENT_BLUE = (41, 98, 255)
    BLACK = (0, 0, 0)
    DARK_GRAY = (51, 51, 51)
    MEDIUM_GRAY = (120, 120, 120)
    LIGHT_GRAY = (230, 230, 230)
    WHITE = (255, 255, 255)
    RED_ACCENT = (180, 30, 30)
    AGENT_BG = (232, 240, 254)
    SCAMMER_BG = (254, 235, 235)

    def header(self):
        """Override header - we handle it manually in the report."""
        pass

    def footer(self):
        """Page footer with page number and classification."""
        self.set_y(-20)
        self.set_font("Helvetica", "I", 7)
        self.set_text_color(*self.MEDIUM_GRAY)
        self.cell(0, 5, "CONFIDENTIAL - Law Enforcement Use Only", align="C", new_x="LMARGIN", new_y="NEXT")
        self.cell(0, 5, f"Page {self.page_no()}/{{nb}}", align="C")


class ForensicReporter:
    """Generates forensic-grade PDF investigation reports."""

    FORENSICS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "forensics")

    def __init__(self):
        """Initialize forensic reporter and ensure output directory exists."""
        os.makedirs(self.FORENSICS_DIR, exist_ok=True)

    def _generate_case_id(self, session_id: str) -> str:
        """Generate a case ID from the session ID."""
        # Use session_id directly for traceability
        clean_id = session_id.replace("-", "").replace("_", "")[:8].upper()
        if not clean_id:
            clean_id = f"{random.randint(1000, 9999):04d}"
        return f"CFA-{datetime.now().year}-{clean_id}"

    def _safe_text(self, text: str) -> str:
        """Sanitize text for PDF output, replacing unsupported characters."""
        if not text:
            return "N/A"
        # Replace common problematic Unicode characters with ASCII equivalents
        replacements = {
            '\u2018': "'", '\u2019': "'",  # Smart single quotes
            '\u201c': '"', '\u201d': '"',  # Smart double quotes
            '\u2013': '-', '\u2014': '--',  # En/em dashes
            '\u2026': '...',               # Ellipsis
            '\u00a0': ' ',                 # Non-breaking space
            '\u20b9': 'Rs.',               # Indian Rupee symbol
            '\u2022': '*',                 # Bullet
            '\u2713': '[Y]',               # Checkmark
            '\u2717': '[X]',               # X mark
        }
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        # Strip any remaining non-latin1 characters
        return text.encode('latin-1', errors='replace').decode('latin-1')

    def generate_forensic_report(
        self,
        session_id: str,
        extracted_intelligence: ExtractedIntelligence,
        conversation_history: List[Message],
        agent_notes: str = "",
        scam_detected: bool = True,
        total_messages: int = 0
    ) -> Optional[str]:
        """
        Generate a comprehensive forensic investigation PDF report.
        DEPRECATED: Use generate_forensic_report_bytes() for MongoDB storage.

        Args:
            session_id: The session identifier (used as Case ID).
            extracted_intelligence: Intelligence data extracted from conversation.
            conversation_history: Full list of Message objects from the session.
            agent_notes: Summary notes about the scam interaction.
            scam_detected: Whether a scam was detected.
            total_messages: Total messages exchanged.

        Returns:
            Path to the generated PDF file, or None on failure.
        """
        try:
            case_id = self._generate_case_id(session_id)
            generation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            msg_count = total_messages or len(conversation_history)

            pdf = ForensicPDF(orientation="P", unit="mm", format="A4")
            pdf.alias_nb_pages()
            pdf.set_auto_page_break(auto=True, margin=25)
            pdf.add_page()

            # ── HEADER BANNER ──
            self._render_header(pdf, case_id, generation_date)

            # ── EXECUTIVE SUMMARY ──
            self._render_executive_summary(pdf, agent_notes, scam_detected, msg_count, extracted_intelligence)

            # ── PRIMARY SUSPECT DATA TABLE ──
            self._render_suspect_table(pdf, extracted_intelligence)

            # ── BEHAVIORAL MARKERS ──
            self._render_behavioral_markers(pdf, extracted_intelligence)

            # ── EVIDENCE LOG ──
            self._render_evidence_log(pdf, conversation_history)

            # ── FORENSIC FOOTER ──
            self._render_forensic_footer(pdf)

            # Save file
            filename = f"CyberCrime_Report_{case_id}.pdf"
            filepath = os.path.join(self.FORENSICS_DIR, filename)
            pdf.output(filepath)

            logger.info(f"Forensic report generated: {filepath} (Case: {case_id})")
            return filepath

        except Exception as e:
            logger.error(f"Failed to generate forensic report - Session: {session_id}, Error: {e}")
            return None

    def generate_forensic_report_bytes(
        self,
        session_id: str,
        extracted_intelligence: ExtractedIntelligence,
        conversation_history: List[Message],
        agent_notes: str = "",
        scam_detected: bool = True,
        total_messages: int = 0
    ) -> Optional[bytes]:
        """
        Generate a forensic PDF report and return as bytes for MongoDB storage.

        Args:
            session_id: The session identifier (used as Case ID).
            extracted_intelligence: Intelligence data extracted from conversation.
            conversation_history: Full list of Message objects from the session.
            agent_notes: Summary notes about the scam interaction.
            scam_detected: Whether a scam was detected.
            total_messages: Total messages exchanged.

        Returns:
            PDF content as bytes, or None on failure.
        """
        try:
            case_id = self._generate_case_id(session_id)
            generation_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S UTC")
            msg_count = total_messages or len(conversation_history)

            pdf = ForensicPDF(orientation="P", unit="mm", format="A4")
            pdf.alias_nb_pages()
            pdf.set_auto_page_break(auto=True, margin=25)
            pdf.add_page()

            # ── HEADER BANNER ──
            self._render_header(pdf, case_id, generation_date)

            # ── EXECUTIVE SUMMARY ──
            self._render_executive_summary(pdf, agent_notes, scam_detected, msg_count, extracted_intelligence)

            # ── PRIMARY SUSPECT DATA TABLE ──
            self._render_suspect_table(pdf, extracted_intelligence)

            # ── BEHAVIORAL MARKERS ──
            self._render_behavioral_markers(pdf, extracted_intelligence)

            # ── EVIDENCE LOG ──
            self._render_evidence_log(pdf, conversation_history)

            # ── FORENSIC FOOTER ──
            self._render_forensic_footer(pdf)

            # Generate PDF as bytes
            pdf_bytes = pdf.output()

            logger.info(f"Forensic report generated as bytes (Case: {case_id}, Size: {len(pdf_bytes)} bytes)")
            return pdf_bytes

        except Exception as e:
            logger.error(f"Failed to generate forensic report bytes - Session: {session_id}, Error: {e}")
            return None

    # ──────────────────────────────────────────────
    # Section renderers
    # ──────────────────────────────────────────────

    def _render_header(self, pdf: ForensicPDF, case_id: str, generation_date: str):
        """Render the professional header banner."""
        # Top accent bar
        pdf.set_fill_color(*ForensicPDF.NAVY)
        pdf.rect(10, 10, 190, 3, "F")

        # Main banner background
        pdf.set_fill_color(*ForensicPDF.DARK_BLUE)
        pdf.rect(10, 13, 190, 32, "F")

        # Title text
        pdf.set_y(16)
        pdf.set_font("Helvetica", "B", 14)
        pdf.set_text_color(*ForensicPDF.WHITE)
        pdf.cell(0, 7, "CONFIDENTIAL", align="C", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "B", 11)
        pdf.cell(0, 6, "Cybercrime Forensic Investigation Report", align="C", new_x="LMARGIN", new_y="NEXT")

        # Subtitle line
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(180, 200, 255)
        pdf.cell(0, 5, "Autonomous Honeypot Intelligence Division", align="C", new_x="LMARGIN", new_y="NEXT")

        # Bottom accent bar
        pdf.set_fill_color(*ForensicPDF.ACCENT_BLUE)
        pdf.rect(10, 45, 190, 1.5, "F")

        # Metadata row
        pdf.set_y(50)
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*ForensicPDF.DARK_GRAY)

        col_w = 63
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(20, 5, "Case ID: ", new_x="RIGHT")
        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*ForensicPDF.ACCENT_BLUE)
        pdf.cell(col_w - 20, 5, case_id, new_x="RIGHT")

        pdf.set_text_color(*ForensicPDF.DARK_GRAY)
        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(14, 5, "Date: ", new_x="RIGHT")
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(col_w - 14, 5, generation_date, new_x="RIGHT")

        pdf.set_font("Helvetica", "B", 8)
        pdf.cell(24, 5, "Investigator: ", new_x="RIGHT")
        pdf.set_font("Helvetica", "", 8)
        pdf.cell(col_w - 24, 5, "Cyber-Forensic Agent (AI)", new_x="LMARGIN", new_y="NEXT")

        # Divider
        pdf.ln(3)
        pdf.set_draw_color(*ForensicPDF.LIGHT_GRAY)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)

    def _render_section_title(self, pdf: ForensicPDF, title: str):
        """Render a styled section title."""
        y = pdf.get_y()
        # Blue left accent bar
        pdf.set_fill_color(*ForensicPDF.ACCENT_BLUE)
        pdf.rect(10, y, 3, 7, "F")

        pdf.set_x(16)
        pdf.set_font("Helvetica", "B", 11)
        pdf.set_text_color(*ForensicPDF.NAVY)
        pdf.cell(0, 7, self._safe_text(title), new_x="LMARGIN", new_y="NEXT")
        pdf.ln(2)

    def _render_executive_summary(
        self, pdf: ForensicPDF, agent_notes: str, scam_detected: bool,
        msg_count: int, intelligence: ExtractedIntelligence
    ):
        """Render the executive summary / incident analysis section."""
        self._render_section_title(pdf, "1. INCIDENT ANALYSIS (Executive Summary)")

        # Status badge
        pdf.set_font("Helvetica", "B", 9)
        if scam_detected:
            pdf.set_fill_color(*ForensicPDF.RED_ACCENT)
            pdf.set_text_color(*ForensicPDF.WHITE)
            pdf.cell(50, 6, "  SCAM CONFIRMED  ", fill=True, new_x="RIGHT")
        else:
            pdf.set_fill_color(*ForensicPDF.MEDIUM_GRAY)
            pdf.set_text_color(*ForensicPDF.WHITE)
            pdf.cell(50, 6, "  INCONCLUSIVE  ", fill=True, new_x="RIGHT")

        pdf.set_text_color(*ForensicPDF.DARK_GRAY)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 6, f"  Total Messages Exchanged: {msg_count}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        # Impersonation line
        targets = getattr(intelligence, 'impersonationTargets', [])
        if targets:
            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*ForensicPDF.DARK_GRAY)
            pdf.cell(40, 5, "Impersonation: ", new_x="RIGHT")
            pdf.set_font("Helvetica", "", 9)
            pdf.cell(0, 5, self._safe_text(", ".join(targets)), new_x="LMARGIN", new_y="NEXT")
            pdf.ln(1)

        # Agent notes summary
        if agent_notes:
            pdf.set_font("Helvetica", "B", 9)
            pdf.cell(40, 5, "Agent Summary: ", new_x="RIGHT")
            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*ForensicPDF.DARK_GRAY)
            pdf.multi_cell(150, 5, self._safe_text(agent_notes))
        pdf.ln(4)

    def _render_suspect_table(self, pdf: ForensicPDF, intelligence: ExtractedIntelligence):
        """Render primary suspect data as a bordered table."""
        self._render_section_title(pdf, "2. PRIMARY SUSPECT DATA")

        # Prepare table rows: (Label, Value)
        phone_val = ", ".join(intelligence.phoneNumbers) if intelligence.phoneNumbers else "Not extracted"
        bank_val = ", ".join(intelligence.bankAccounts) if intelligence.bankAccounts else "Not extracted"
        upi_val = ", ".join(intelligence.upiIds) if intelligence.upiIds else "Not extracted"
        link_val = ", ".join(intelligence.phishingLinks) if intelligence.phishingLinks else "Not extracted"

        rows = [
            ("Suspect Mobile", phone_val),
            ("Target Account", bank_val),
            ("Payment ID (UPI)", upi_val),
            ("Malicious URL", link_val),
        ]

        # Include internal fields if present
        emails = getattr(intelligence, 'emails', [])
        if emails:
            rows.append(("Email Addresses", ", ".join(emails)))
        amounts = getattr(intelligence, 'amounts', [])
        if amounts:
            rows.append(("Monetary Amounts", ", ".join(amounts)))

        label_w = 50
        value_w = 140
        row_h = 8

        # Table header
        pdf.set_fill_color(*ForensicPDF.NAVY)
        pdf.set_text_color(*ForensicPDF.WHITE)
        pdf.set_font("Helvetica", "B", 9)
        pdf.set_draw_color(*ForensicPDF.NAVY)
        pdf.cell(label_w, row_h, "  Field", border=1, fill=True, new_x="RIGHT")
        pdf.cell(value_w, row_h, "  Extracted Value", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

        # Table rows
        pdf.set_draw_color(*ForensicPDF.MEDIUM_GRAY)
        for i, (label, value) in enumerate(rows):
            if i % 2 == 0:
                pdf.set_fill_color(*ForensicPDF.LIGHT_GRAY)
            else:
                pdf.set_fill_color(*ForensicPDF.WHITE)

            pdf.set_font("Helvetica", "B", 9)
            pdf.set_text_color(*ForensicPDF.DARK_GRAY)
            pdf.cell(label_w, row_h, f"  {label}", border=1, fill=True, new_x="RIGHT")

            pdf.set_font("Helvetica", "", 9)
            pdf.set_text_color(*ForensicPDF.BLACK)
            pdf.cell(value_w, row_h, f"  {self._safe_text(value)}", border=1, fill=True, new_x="LMARGIN", new_y="NEXT")

        pdf.ln(6)

    def _render_behavioral_markers(self, pdf: ForensicPDF, intelligence: ExtractedIntelligence):
        """Render high-risk keyword behavioral markers."""
        self._render_section_title(pdf, "3. BEHAVIORAL MARKERS")

        keywords = intelligence.suspiciousKeywords
        if not keywords:
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(*ForensicPDF.MEDIUM_GRAY)
            pdf.cell(0, 6, "No high-risk keywords detected.", new_x="LMARGIN", new_y="NEXT")
            pdf.ln(4)
            return

        # Threat level badge
        count = len(keywords)
        if count >= 8:
            level, color = "CRITICAL", ForensicPDF.RED_ACCENT
        elif count >= 4:
            level, color = "HIGH", (200, 120, 0)
        else:
            level, color = "MODERATE", (180, 160, 0)

        pdf.set_font("Helvetica", "B", 9)
        pdf.set_fill_color(*color)
        pdf.set_text_color(*ForensicPDF.WHITE)
        pdf.cell(45, 6, f"  Threat Level: {level}", fill=True, new_x="RIGHT")
        pdf.set_text_color(*ForensicPDF.DARK_GRAY)
        pdf.set_font("Helvetica", "", 9)
        pdf.cell(0, 6, f"  {count} high-risk keyword(s) detected", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        # Keyword chips (inline boxes)
        pdf.set_font("Helvetica", "", 8)
        x_start = 15
        x = x_start
        max_x = 195
        for kw in sorted(keywords):
            kw_safe = self._safe_text(kw)
            w = pdf.get_string_width(kw_safe) + 8
            if x + w > max_x:
                pdf.ln(7)
                x = x_start
            pdf.set_x(x)
            pdf.set_fill_color(240, 240, 250)
            pdf.set_draw_color(*ForensicPDF.ACCENT_BLUE)
            pdf.set_text_color(*ForensicPDF.DARK_BLUE)
            pdf.cell(w, 6, f" {kw_safe} ", border=1, fill=True, new_x="RIGHT")
            x = pdf.get_x() + 2

        pdf.ln(10)

    def _render_evidence_log(self, pdf: ForensicPDF, conversation_history: List[Message]):
        """Render the full conversation transcript as an evidence log."""
        pdf.add_page()
        self._render_section_title(pdf, "4. EVIDENCE LOG (Full Transcript)")

        if not conversation_history:
            pdf.set_font("Helvetica", "I", 9)
            pdf.set_text_color(*ForensicPDF.MEDIUM_GRAY)
            pdf.cell(0, 6, "No conversation data available.", new_x="LMARGIN", new_y="NEXT")
            return

        pdf.set_font("Helvetica", "", 8)
        pdf.set_text_color(*ForensicPDF.DARK_GRAY)
        pdf.cell(0, 5, f"Total entries: {len(conversation_history)}", new_x="LMARGIN", new_y="NEXT")
        pdf.ln(3)

        for idx, msg in enumerate(conversation_history):
            is_agent = msg.sender in ("user", "agent", "honeypot")
            sender_label = "Cyber-Forensic Agent" if is_agent else "Target (Scammer)"

            # Check remaining space, add page if needed
            if pdf.get_y() > 260:
                pdf.add_page()

            # Shaded background for distinction
            y_before = pdf.get_y()

            if is_agent:
                pdf.set_fill_color(*ForensicPDF.AGENT_BG)
                tag_color = ForensicPDF.DARK_BLUE
            else:
                pdf.set_fill_color(*ForensicPDF.SCAMMER_BG)
                tag_color = ForensicPDF.RED_ACCENT

            # Turn label
            pdf.set_font("Helvetica", "B", 8)
            pdf.set_text_color(*tag_color)
            turn_label = f"[{idx + 1:02d}] {sender_label}"

            # Timestamp if available
            ts = ""
            if hasattr(msg, 'timestamp') and msg.timestamp:
                try:
                    ts_dt = datetime.fromtimestamp(msg.timestamp / 1000)
                    ts = ts_dt.strftime(" | %H:%M:%S")
                except (ValueError, OSError):
                    pass

            pdf.cell(0, 5, f"{turn_label}{ts}", fill=True, new_x="LMARGIN", new_y="NEXT")

            # Message body
            pdf.set_font("Helvetica", "", 8)
            pdf.set_text_color(*ForensicPDF.BLACK)
            safe_text = self._safe_text(msg.text)
            pdf.set_x(15)
            pdf.multi_cell(180, 4.5, safe_text, fill=True)
            pdf.ln(2)

    def _render_forensic_footer(self, pdf: ForensicPDF):
        """Render the legal forensic footnote at the bottom."""
        # Ensure we have enough space
        if pdf.get_y() > 250:
            pdf.add_page()

        pdf.ln(6)
        pdf.set_draw_color(*ForensicPDF.NAVY)
        pdf.line(10, pdf.get_y(), 200, pdf.get_y())
        pdf.ln(4)

        pdf.set_fill_color(245, 245, 252)
        y = pdf.get_y()
        pdf.rect(10, y, 190, 20, "F")

        pdf.set_y(y + 2)
        pdf.set_font("Helvetica", "B", 7)
        pdf.set_text_color(*ForensicPDF.NAVY)
        pdf.cell(0, 4, "FORENSIC INTEGRITY NOTICE", align="C", new_x="LMARGIN", new_y="NEXT")

        pdf.set_font("Helvetica", "", 7)
        pdf.set_text_color(*ForensicPDF.MEDIUM_GRAY)
        notice = (
            "This document contains autonomously extracted digital evidence. "
            "Data integrity has been preserved for law enforcement review via automated behavioral analysis. "
            "All intelligence was gathered through a passive honeypot engagement system. "
            "No personally identifiable information of legitimate users has been compromised in this process."
        )
        pdf.set_x(15)
        pdf.multi_cell(180, 3.5, notice, align="C")
