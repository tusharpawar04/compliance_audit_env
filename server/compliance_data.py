"""
The rulebook and document database.

Contains:
- 8 GDPR-style rules that agents must apply
- 15 company documents with known violations (5 easy, 5 medium, 5 hard)
- Rule categories for partial credit grading

This is the "ground truth" that the environment uses to grade agent responses.
"""

# GDPR-style rules covering key compliance domains
RULES = {
    "RULE_01": "Data Retention: Personal data must not be kept longer than necessary for the purposes for which it was collected. Organizations must define and document retention periods.",
    "RULE_02": "Third-Party Transparency: Organizations must clearly disclose all third parties with whom personal data is shared, including the purpose of sharing and the categories of data shared.",
    "RULE_03": "Opt-Out Rights: Users must be provided with a clear and accessible mechanism to opt out of data processing activities that are not strictly necessary for service delivery.",
    "RULE_04": "Purpose Limitation: Personal data collected for one purpose must not be used for a different, incompatible purpose without obtaining fresh consent from the data subject.",
    "RULE_05": "Breach Notification: Organizations must notify affected individuals and relevant supervisory authorities within 72 hours of discovering a personal data breach.",
    "RULE_06": "Cross-Border Transfers: Personal data transfers to countries outside the EEA must be protected by adequate safeguards such as Standard Contractual Clauses or Binding Corporate Rules.",
    "RULE_07": "Consent Requirements: Consent for data processing must be freely given, specific, informed, and unambiguous. Pre-ticked boxes and silence do not constitute valid consent.",
    "RULE_08": "Deletion Rights: Individuals have the right to request deletion of their personal data when it is no longer necessary for the original purpose or when consent is withdrawn.",
}

# Category mapping for partial credit in medium grader
RULE_CATEGORIES = {
    "RULE_01": "retention",
    "RULE_02": "transparency",
    "RULE_03": "user_rights",
    "RULE_04": "purpose_limitation",
    "RULE_05": "breach_notification",
    "RULE_06": "cross_border",
    "RULE_07": "consent",
    "RULE_08": "user_rights",
}

# 15 annotated documents: 5 easy, 5 medium, 5 hard
DOCUMENTS = [
    # ===== EASY DOCUMENTS (5) =====
    {
        "doc_id": "EASY_01",
        "company_name": "QuickShop Inc.",
        "document_text": (
            "QuickShop Privacy Policy\n\n"
            "We collect your name, email, and purchase history. "
            "We keep this data forever to improve our services. "
            "By using our site, you agree to all data processing."
        ),
        "difficulty": "easy",
        "violation_ids": ["RULE_01", "RULE_07"],
        "rewrite_keywords": ["retention period", "specific consent", "freely given"],
    },
    {
        "doc_id": "EASY_02",
        "company_name": "FastDelivery LLC",
        "document_text": (
            "FastDelivery Data Policy\n\n"
            "We share your delivery address and phone number with our partners. "
            "We do not disclose which partners or why. "
            "You cannot opt out of this sharing."
        ),
        "difficulty": "easy",
        "violation_ids": ["RULE_02", "RULE_03"],
        "rewrite_keywords": ["third parties", "opt-out mechanism", "partner names"],
    },
    {
        "doc_id": "EASY_03",
        "company_name": "SocialHub",
        "document_text": (
            "SocialHub Terms of Service\n\n"
            "We collect your posts and messages for platform operation. "
            "We may also use this data for advertising purposes. "
            "Continued use of the platform means you consent to all uses."
        ),
        "difficulty": "easy",
        "violation_ids": ["RULE_04", "RULE_07"],
        "rewrite_keywords": ["separate consent", "purpose limitation", "advertising consent"],
    },
    {
        "doc_id": "EASY_04",
        "company_name": "CloudStore Pro",
        "document_text": (
            "CloudStore Data Processing Agreement\n\n"
            "In the event of a data breach, we will investigate and notify you as soon as reasonably possible. "
            "Notification timelines depend on the severity of the breach."
        ),
        "difficulty": "easy",
        "violation_ids": ["RULE_05"],
        "rewrite_keywords": ["72 hours", "supervisory authority", "breach notification"],
    },
    {
        "doc_id": "EASY_05",
        "company_name": "GlobalTech Services",
        "document_text": (
            "GlobalTech Privacy Notice\n\n"
            "We transfer your data to our servers located worldwide, including countries outside the EEA. "
            "We ensure your data is protected by our internal security policies."
        ),
        "difficulty": "easy",
        "violation_ids": ["RULE_06"],
        "rewrite_keywords": ["Standard Contractual Clauses", "adequate safeguards", "Binding Corporate Rules"],
    },
    # ===== MEDIUM DOCUMENTS (5) =====
    {
        "doc_id": "MEDIUM_01",
        "company_name": "HealthTrack Analytics",
        "document_text": (
            "HealthTrack Privacy Policy\n\n"
            "We collect health metrics, activity data, and location information to provide personalized fitness recommendations. "
            "This data is retained for the lifetime of your account to ensure continuity of service. "
            "We share anonymized data with research partners to improve health outcomes. "
            "By creating an account, you consent to our data practices."
        ),
        "difficulty": "medium",
        "violation_ids": ["RULE_01", "RULE_02", "RULE_07"],
        "rewrite_keywords": ["retention period", "research partners", "specific consent", "anonymization details"],
    },
    {
        "doc_id": "MEDIUM_02",
        "company_name": "EduPlatform Global",
        "document_text": (
            "EduPlatform Data Processing Agreement\n\n"
            "We collect student performance data for course delivery. "
            "This data may also be used to develop new educational products and services. "
            "We transfer data to our cloud providers in the US and Asia. "
            "Students can request deletion of their data by contacting support, subject to legal retention requirements."
        ),
        "difficulty": "medium",
        "violation_ids": ["RULE_04", "RULE_06", "RULE_08"],
        "rewrite_keywords": ["separate consent", "Standard Contractual Clauses", "deletion process", "retention requirements"],
    },
    {
        "doc_id": "MEDIUM_03",
        "company_name": "AdNetwork Plus",
        "document_text": (
            "AdNetwork Privacy Policy\n\n"
            "We collect browsing history, device identifiers, and location data to serve targeted advertisements. "
            "We share this data with hundreds of advertising partners. A full list is available upon request. "
            "Users can opt out of targeted advertising by adjusting browser settings, though this may affect service quality."
        ),
        "difficulty": "medium",
        "violation_ids": ["RULE_02", "RULE_03"],
        "rewrite_keywords": ["partner list", "clear opt-out", "accessible mechanism", "service quality"],
    },
    {
        "doc_id": "MEDIUM_04",
        "company_name": "SecureBank Online",
        "document_text": (
            "SecureBank Data Breach Response Policy\n\n"
            "In the event of a data breach, we will conduct a thorough investigation to determine the scope and impact. "
            "Affected customers will be notified by email within 10 business days. "
            "We will also notify relevant authorities as required by law."
        ),
        "difficulty": "medium",
        "violation_ids": ["RULE_05"],
        "rewrite_keywords": ["72 hours", "supervisory authority", "without undue delay"],
    },
    {
        "doc_id": "MEDIUM_05",
        "company_name": "TravelBooker International",
        "document_text": (
            "TravelBooker Terms and Conditions\n\n"
            "We collect passport details, payment information, and travel preferences. "
            "This data is stored indefinitely to facilitate future bookings and customer service. "
            "We share your information with airlines, hotels, and tourism boards as necessary. "
            "You may request deletion of your account, but we retain transaction records for 7 years for tax purposes."
        ),
        "difficulty": "medium",
        "violation_ids": ["RULE_01", "RULE_02", "RULE_08"],
        "rewrite_keywords": ["retention period", "third parties", "deletion rights", "legal basis"],
    },
    # ===== HARD DOCUMENTS (5) =====
    {
        "doc_id": "HARD_01",
        "company_name": "MegaCorp Enterprises",
        "document_text": (
            "MegaCorp Global Privacy Statement\n\n"
            "We collect personal data including name, contact details, employment history, financial information, and behavioral data. "
            "This data is used for service delivery, product development, marketing, and research. "
            "We retain data for as long as necessary to fulfill these purposes, which may extend beyond the active customer relationship. "
            "We share data with subsidiaries, service providers, and business partners globally. "
            "Data may be transferred to countries with varying data protection standards. "
            "By using our services, you acknowledge and accept our data practices. "
            "You may contact us to exercise your rights, subject to verification and legal limitations."
        ),
        "difficulty": "hard",
        "violation_ids": ["RULE_01", "RULE_02", "RULE_04", "RULE_06", "RULE_07"],
        "rewrite_keywords": [
            "specific retention periods",
            "named third parties",
            "separate consent",
            "Standard Contractual Clauses",
            "freely given consent",
            "purpose limitation",
        ],
    },
    {
        "doc_id": "HARD_02",
        "company_name": "DataBroker Solutions",
        "document_text": (
            "DataBroker Privacy Policy\n\n"
            "We aggregate data from multiple sources including public records, social media, and partner networks. "
            "This data is used to create consumer profiles for marketing, risk assessment, and analytics. "
            "We do not provide a direct opt-out mechanism, but you may contact us to request removal from specific datasets. "
            "Data is retained indefinitely to maintain profile accuracy and historical trends. "
            "We share profiles with clients in various industries including finance, insurance, and retail. "
            "Consent for data processing is obtained through our partners' terms of service."
        ),
        "difficulty": "hard",
        "violation_ids": ["RULE_01", "RULE_03", "RULE_04", "RULE_07"],
        "rewrite_keywords": [
            "retention period",
            "clear opt-out mechanism",
            "purpose limitation",
            "specific consent",
            "freely given",
            "profile deletion",
        ],
    },
    {
        "doc_id": "HARD_03",
        "company_name": "FinTech Innovations",
        "document_text": (
            "FinTech Data Processing and Security Policy\n\n"
            "We process financial transactions, credit history, and behavioral analytics. "
            "Data is stored across multiple jurisdictions including the US, Singapore, and Switzerland. "
            "In case of a security incident, we will assess the risk and notify affected parties according to our internal protocols. "
            "We share data with payment processors, credit bureaus, and regulatory bodies as required. "
            "Users can request data deletion, but we retain transaction records for 10 years for compliance purposes. "
            "Continued use of our platform constitutes acceptance of data transfers and processing activities."
        ),
        "difficulty": "hard",
        "violation_ids": ["RULE_05", "RULE_06", "RULE_07", "RULE_08"],
        "rewrite_keywords": [
            "72 hours",
            "supervisory authority",
            "Standard Contractual Clauses",
            "specific consent",
            "deletion rights",
            "legal basis",
        ],
    },
    {
        "doc_id": "HARD_04",
        "company_name": "SmartHome Devices Inc.",
        "document_text": (
            "SmartHome Privacy and Data Use Policy\n\n"
            "Our devices collect usage patterns, voice recordings, video footage, and environmental data. "
            "This data is used for device operation, feature improvement, and development of new products and services. "
            "We may also use this data for targeted advertising and market research. "
            "Data is shared with cloud service providers, analytics partners, and third-party developers. "
            "We retain data for up to 5 years or longer if required for product development. "
            "Users can delete their account, but device usage data may be retained in anonymized form. "
            "By setting up a device, you agree to our data collection and use practices."
        ),
        "difficulty": "hard",
        "violation_ids": ["RULE_01", "RULE_02", "RULE_04", "RULE_07", "RULE_08"],
        "rewrite_keywords": [
            "specific retention periods",
            "named third parties",
            "separate consent",
            "advertising consent",
            "deletion rights",
            "anonymization",
        ],
    },
    {
        "doc_id": "HARD_05",
        "company_name": "GlobalHealth Research Network",
        "document_text": (
            "GlobalHealth Data Sharing Framework\n\n"
            "We collect medical records, genetic data, and lifestyle information from participating healthcare providers. "
            "This data is used for medical research, drug development, and public health initiatives. "
            "We share data with pharmaceutical companies, academic institutions, and government health agencies worldwide. "
            "Data is transferred internationally to research centers in the US, EU, and Asia. "
            "We retain data indefinitely to support longitudinal studies and future research. "
            "Participants can withdraw from future studies, but data already collected cannot be deleted due to research integrity requirements. "
            "Consent is obtained through healthcare provider agreements. "
            "In case of a data breach, we will notify participants and authorities within a reasonable timeframe based on the nature of the breach."
        ),
        "difficulty": "hard",
        "violation_ids": ["RULE_01", "RULE_02", "RULE_04", "RULE_05", "RULE_06", "RULE_07", "RULE_08"],
        "rewrite_keywords": [
            "retention period",
            "named third parties",
            "separate consent",
            "72 hours",
            "Standard Contractual Clauses",
            "specific consent",
            "deletion rights",
            "research ethics",
        ],
    },
]
