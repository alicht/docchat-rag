#!/usr/bin/env python3
"""
Generate test PDFs with mixed content for DocChat RAG testing.
Creates Mixed_Policies.pdf and Medical_and_Legal.pdf with Topic X-Y patterns.
"""

from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import black, darkblue
import os

def create_mixed_policies_pdf():
    """Create Mixed_Policies.pdf with HR, contracts, real estate, and IT policies."""
    
    doc = SimpleDocTemplate(
        "rag_test_pdfs/Mixed_Policies.pdf",
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=darkblue,
        spaceAfter=12
    )
    topic_style = ParagraphStyle(
        'TopicStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=black,
        spaceBefore=12,
        spaceAfter=6
    )
    
    story = []
    
    # Title page
    story.append(Paragraph("Mixed Policies and Procedures Manual", title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Comprehensive Guide to HR, Contracts, Real Estate, and IT Policies", styles['Normal']))
    story.append(PageBreak())
    
    # HR Policies Section (Pages 2-6)
    hr_topics = [
        ("Topic 1-1: Employee Onboarding Process", 
         "All new employees must complete orientation within 48 hours of start date. This includes safety training, company policy review, and IT setup. HR will coordinate with department managers to ensure smooth integration."),
        
        ("Topic 1-2: Performance Review Guidelines", 
         "Annual performance reviews are conducted every January. Employees receive 360-degree feedback from peers, subordinates, and supervisors. Goals are set collaboratively between employee and manager."),
        
        ("Topic 2-1: Vacation Policy and Accrual Rates", 
         "Employees accrue vacation time at 1.5 days per month for years 1-3, 2 days per month for years 4-7, and 2.5 days per month thereafter. Maximum carryover is 10 days into the following year."),
        
        ("Topic 2-2: Remote Work Guidelines", 
         "Remote work requires manager approval and home office setup meeting ergonomic standards. Employees must maintain core hours overlap of 10 AM - 2 PM company time for collaboration."),
        
        ("Topic 3-1: Disciplinary Action Procedures", 
         "Progressive discipline follows verbal warning, written warning, final warning, termination sequence. Documentation must be maintained in employee file with HR oversight at each step."),
        
        ("Topic 3-2: Equal Opportunity Employment Policy", 
         "Company maintains zero tolerance for discrimination based on race, gender, age, religion, sexual orientation, or disability. All complaints are investigated within 10 business days."),
        
        ("Topic 4-1: Benefits Enrollment Periods", 
         "Open enrollment occurs annually in November for following year coverage. New employees have 30 days from start date to enroll. Life events allow special enrollment periods."),
        
        ("Topic 4-2: Health and Safety Protocols", 
         "Safety incidents must be reported within 24 hours to both supervisor and safety coordinator. Monthly safety meetings are mandatory for all departments with physical work environments.")
    ]
    
    for i, (topic_title, content) in enumerate(hr_topics):
        if i > 0 and i % 2 == 0:  # New page every 2 topics
            story.append(PageBreak())
        
        story.append(Paragraph(topic_title, topic_style))
        story.append(Paragraph(content, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
    
    story.append(PageBreak())
    
    # Contract Policies Section (Pages 7-11)
    contract_topics = [
        ("Topic 5-1: Vendor Contract Approval Process", 
         "All vendor contracts exceeding $10,000 require legal review and CFO approval. Contracts under $10,000 need department head sign-off. Payment terms must not exceed 30 days."),
        
        ("Topic 5-2: Service Level Agreement Standards", 
         "SLAs must specify uptime requirements (minimum 99.5%), response times, and penalty clauses. Monthly performance reports are required from all service providers."),
        
        ("Topic 6-1: Non-Disclosure Agreement Templates", 
         "Standard NDA templates are available for employees, contractors, and business partners. Legal department maintains three tiers: standard, enhanced, and mutual NDAs."),
        
        ("Topic 6-2: Employment Contract Modifications", 
         "Contract amendments require HR approval and employee signature. Salary changes, role modifications, and reporting structure changes must be documented in writing."),
        
        ("Topic 7-1: Intellectual Property Assignment", 
         "All work-related inventions, software, and creative works belong to the company. Employees must disclose potential IP conflicts and assign rights upon creation."),
        
        ("Topic 7-2: Termination and Severance Policies", 
         "Severance packages vary by position level and tenure. Standard package includes 2 weeks per year of service, with minimum 4 weeks for all eligible employees."),
        
        ("Topic 8-1: Client Contract Negotiation Guidelines", 
         "Sales team can approve standard terms up to $50,000. Legal review required for custom terms or contracts exceeding this threshold. Net 30 payment terms are standard."),
        
        ("Topic 8-2: Contract Renewal and Amendment Process", 
         "Contract renewals must be initiated 90 days before expiration. Automatic renewal clauses require 60-day written notice for termination. Amendment tracking is mandatory.")
    ]
    
    for i, (topic_title, content) in enumerate(contract_topics):
        if i > 0 and i % 2 == 0:
            story.append(PageBreak())
        
        story.append(Paragraph(topic_title, topic_style))
        story.append(Paragraph(content, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
    
    story.append(PageBreak())
    
    # Real Estate Policies Section (Pages 12-16)
    real_estate_topics = [
        ("Topic 9-1: Office Lease Management", 
         "Lease agreements require board approval for terms exceeding 5 years or $500,000 annually. Property inspections are conducted quarterly with maintenance reports filed monthly."),
        
        ("Topic 9-2: Space Allocation and Utilization", 
         "Office space is allocated based on 150 sq ft per employee for open office, 200 sq ft for private offices. Utilization studies are conducted annually to optimize space usage."),
        
        ("Topic 10-1: Facility Maintenance Standards", 
         "Preventive maintenance schedules are established for HVAC, electrical, and plumbing systems. Emergency repairs require immediate vendor notification and cost approval."),
        
        ("Topic 10-2: Security and Access Control", 
         "Building access cards are issued to all employees and tracked by security system. Visitor badges are required for all non-employees and tracked daily."),
        
        ("Topic 11-1: Environmental Compliance", 
         "All facilities must comply with local environmental regulations. Waste disposal, energy efficiency, and air quality standards are monitored monthly."),
        
        ("Topic 11-2: Emergency Evacuation Procedures", 
         "Fire drills are conducted quarterly with evacuation routes posted throughout facility. Emergency contact lists are updated monthly and shared with local authorities."),
        
        ("Topic 12-1: Parking and Transportation Policy", 
         "Employee parking is allocated by seniority and carpooling preference. Public transportation subsidies are available for employees using mass transit."),
        
        ("Topic 12-2: Subletting and Space Sharing", 
         "Excess office space may be sublet with landlord approval and legal review. Shared space agreements must specify utilities, maintenance, and liability responsibilities.")
    ]
    
    for i, (topic_title, content) in enumerate(real_estate_topics):
        if i > 0 and i % 2 == 0:
            story.append(PageBreak())
        
        story.append(Paragraph(topic_title, topic_style))
        story.append(Paragraph(content, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
    
    story.append(PageBreak())
    
    # IT Policies Section (Pages 17-20)
    it_topics = [
        ("Topic 13-1: Password Security Requirements", 
         "Passwords must be minimum 12 characters with uppercase, lowercase, numbers, and special characters. Password changes required every 90 days with no reuse of last 12 passwords."),
        
        ("Topic 13-2: Software Installation and Licensing", 
         "Only IT-approved software may be installed on company devices. All software licenses are tracked and audited annually. Personal software installation is prohibited."),
        
        ("Topic 14-1: Data Backup and Recovery Procedures", 
         "Critical data is backed up daily to cloud storage with 7-day retention. Disaster recovery plan includes 4-hour RTO and 1-hour RPO for mission-critical systems."),
        
        ("Topic 14-2: Network Access and VPN Usage", 
         "VPN access is required for all remote connections to company resources. Multi-factor authentication is mandatory for all external access attempts."),
        
        ("Topic 15-1: Email and Communication Policies", 
         "Business email is monitored for compliance and security. Personal use is limited and subject to company monitoring policies. Retention period is 7 years."),
        
        ("Topic 15-2: Mobile Device Management", 
         "Company-issued mobile devices require MDM enrollment. Personal devices accessing company email must meet minimum security requirements including device encryption."),
        
        ("Topic 16-1: Incident Response Procedures", 
         "Security incidents must be reported to IT within 30 minutes of discovery. Incident response team activates within 2 hours for all critical security events."),
        
        ("Topic 16-2: Technology Asset Management", 
         "All IT assets are tagged and tracked through lifecycle management system. Asset disposal follows secure data destruction protocols with certificate of destruction.")
    ]
    
    for i, (topic_title, content) in enumerate(it_topics):
        if i > 0 and i % 2 == 0:
            story.append(PageBreak())
        
        story.append(Paragraph(topic_title, topic_style))
        story.append(Paragraph(content, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
    
    doc.build(story)
    print("Created Mixed_Policies.pdf with 20 pages")

def create_medical_legal_pdf():
    """Create Medical_and_Legal.pdf with patient guidelines and legal contracts."""
    
    doc = SimpleDocTemplate(
        "rag_test_pdfs/Medical_and_Legal.pdf",
        pagesize=letter,
        rightMargin=inch,
        leftMargin=inch,
        topMargin=inch,
        bottomMargin=inch
    )
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'CustomTitle',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=darkblue,
        spaceAfter=12
    )
    topic_style = ParagraphStyle(
        'TopicStyle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=black,
        spaceBefore=12,
        spaceAfter=6
    )
    
    story = []
    
    # Title page
    story.append(Paragraph("Medical and Legal Compliance Manual", title_style))
    story.append(Spacer(1, 0.5*inch))
    story.append(Paragraph("Patient Care Guidelines and Legal Contract Standards", styles['Normal']))
    story.append(PageBreak())
    
    # Patient Care Guidelines Section (Pages 2-11)
    medical_topics = [
        ("Topic 1-1: Patient Intake and Registration", 
         "All patients must complete intake forms including insurance verification and medical history. Photo ID and insurance cards are required for registration."),
        
        ("Topic 1-2: Consent for Treatment Procedures", 
         "Informed consent must be obtained before any medical procedure. Patients must understand risks, benefits, and alternatives. Documentation is required in medical record."),
        
        ("Topic 2-1: HIPAA Privacy and Security Rules", 
         "Patient health information is protected under HIPAA regulations. Access is limited to authorized personnel only. Breach notification required within 60 days."),
        
        ("Topic 2-2: Medical Record Documentation Standards", 
         "All medical encounters must be documented within 24 hours. Records must be legible, dated, and signed by attending physician. Amendments require proper authorization."),
        
        ("Topic 3-1: Prescription Medication Protocols", 
         "Prescription orders must include patient name, drug name, dosage, quantity, and prescriber signature. Controlled substances require DEA number verification."),
        
        ("Topic 3-2: Laboratory Test Ordering and Results", 
         "Lab orders must specify test type, urgency, and clinical indication. Results are reviewed by ordering physician within 24 hours. Abnormal values require immediate attention."),
        
        ("Topic 4-1: Emergency Response Procedures", 
         "Code blue activation requires immediate response team assembly. CPR and advanced life support protocols follow current AHA guidelines. Documentation is mandatory."),
        
        ("Topic 4-2: Infection Control and Prevention", 
         "Hand hygiene is required before and after patient contact. Personal protective equipment must be used per isolation precautions. Exposure incidents require immediate reporting."),
        
        ("Topic 5-1: Patient Discharge Planning", 
         "Discharge planning begins at admission and involves multidisciplinary team. Patients receive written instructions and follow-up appointments before leaving."),
        
        ("Topic 5-2: Quality Assurance and Patient Safety", 
         "Patient safety events are reported through incident reporting system. Root cause analysis is conducted for all serious safety events. Improvement plans are implemented."),
        
        ("Topic 6-1: Telemedicine and Remote Care", 
         "Telemedicine encounters require patient consent and technology verification. Audio and video quality must meet clinical standards. Documentation follows same standards as in-person visits."),
        
        ("Topic 6-2: Medical Equipment Maintenance", 
         "All medical devices require regular calibration and maintenance per manufacturer specifications. Equipment logs are maintained and reviewed monthly."),
        
        ("Topic 7-1: Patient Rights and Responsibilities", 
         "Patients have right to informed consent, privacy, and respectful treatment. Patient responsibilities include providing accurate information and following treatment plans."),
        
        ("Topic 7-2: Billing and Insurance Processing", 
         "Medical coding must accurately reflect services provided. Insurance claims are submitted within 30 days of service. Patient financial responsibility is communicated clearly."),
        
        ("Topic 8-1: Staff Training and Competency", 
         "All clinical staff must maintain current certifications and complete annual competency testing. Continuing education requirements vary by role and license type."),
        
        ("Topic 8-2: Vendor and Contractor Management", 
         "Medical vendors must provide proof of insurance and clinical credentials. Service contracts include performance metrics and quality standards. Regular audits are conducted.")
    ]
    
    for i, (topic_title, content) in enumerate(medical_topics):
        if i > 0 and i % 2 == 0:
            story.append(PageBreak())
        
        story.append(Paragraph(topic_title, topic_style))
        story.append(Paragraph(content, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
    
    story.append(PageBreak())
    
    # Legal Contract Standards Section (Pages 12-20)
    legal_topics = [
        ("Topic 9-1: Contract Formation and Validity", 
         "Valid contracts require offer, acceptance, consideration, and legal capacity. All material terms must be clearly defined. Contracts exceeding $500 require written documentation."),
        
        ("Topic 9-2: Force Majeure and Contract Suspension", 
         "Force majeure clauses protect parties from unforeseeable events preventing contract performance. Notice requirements and mitigation efforts must be specified."),
        
        ("Topic 10-1: Indemnification and Liability Limits", 
         "Indemnification clauses must specify scope of protection and excluded events. Liability caps should be reasonable and enforceable under applicable law."),
        
        ("Topic 10-2: Dispute Resolution and Arbitration", 
         "Dispute resolution clauses specify mediation before arbitration. Arbitration rules and venue must be clearly defined. Class action waivers require specific language."),
        
        ("Topic 11-1: Intellectual Property and Trade Secrets", 
         "IP ownership must be clearly assigned in contracts. Trade secret protection requires confidentiality agreements and access controls. Registration deadlines must be tracked."),
        
        ("Topic 11-2: Termination Rights and Procedures", 
         "Termination clauses specify grounds for termination and notice requirements. Post-termination obligations include data return and confidentiality continuation."),
        
        ("Topic 12-1: Compliance and Regulatory Requirements", 
         "Contracts must include compliance representations and audit rights. Regulatory changes may trigger contract modification requirements. Violation remedies must be specified."),
        
        ("Topic 12-2: Payment Terms and Default Remedies", 
         "Payment terms specify amount, timing, and method of payment. Default remedies include late fees, acceleration, and collection rights. Grace periods should be reasonable."),
        
        ("Topic 13-1: Data Protection and Privacy Compliance", 
         "Data processing agreements must comply with GDPR, CCPA, and other privacy laws. Data breach notification and remediation procedures are mandatory."),
        
        ("Topic 13-2: Insurance and Risk Management", 
         "Minimum insurance requirements include general liability, professional liability, and cyber liability. Additional insured status and waiver of subrogation may be required."),
        
        ("Topic 14-1: International Contract Considerations", 
         "International contracts must address currency, governing law, and jurisdiction. Import/export compliance and tax implications require careful consideration."),
        
        ("Topic 14-2: Electronic Signatures and Digital Contracts", 
         "Electronic signatures must comply with ESIGN Act and UETA requirements. Digital contract platforms must provide audit trails and tamper protection."),
        
        ("Topic 15-1: Service Level Agreements and Performance", 
         "SLAs must include measurable performance metrics and monitoring procedures. Service credits and penalty calculations should be clearly defined."),
        
        ("Topic 15-2: Contract Renewal and Amendment Process", 
         "Renewal options must specify terms and notice requirements. Amendment procedures require written agreement and proper authorization levels."),
        
        ("Topic 16-1: Merger and Acquisition Contract Impact", 
         "Change of control provisions may trigger consent requirements or termination rights. Assignment and successor liability must be addressed."),
        
        ("Topic 16-2: Environmental and Sustainability Clauses", 
         "Environmental compliance representations and sustainability goals are increasingly common. Carbon footprint reduction and green procurement requirements may apply.")
    ]
    
    for i, (topic_title, content) in enumerate(legal_topics):
        if i > 0 and i % 2 == 0:
            story.append(PageBreak())
        
        story.append(Paragraph(topic_title, topic_style))
        story.append(Paragraph(content, styles['Normal']))
        story.append(Spacer(1, 0.3*inch))
    
    doc.build(story)
    print("Created Medical_and_Legal.pdf with 20 pages")

if __name__ == "__main__":
    # Create the test PDFs
    create_mixed_policies_pdf()
    create_medical_legal_pdf()
    print("Test PDFs generated successfully!")