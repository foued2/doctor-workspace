"""
Cross-Domain Stressor
=====================
Tests whether the Doctor can generalize reasoning beyond its training domain.

The generator produces cases in specific domains (ambulance dispatch, port inspection, etc.).
This stressor introduces completely different domains:
- Legal contracts
- Medical instructions
- System design specs
- Ambiguous business rules
- Academic policies
- Financial regulations

The question: Can the Doctor apply its reasoning principles to unfamiliar domains,
or has it just learned to pattern-match within its comfort zone?
"""

from __future__ import annotations

import random
from typing import Any, Dict, List

from external_stress_layer import StressCase, StressKind


# Legal contract clauses
LEGAL_CONTRACTS = [
    {
        "domain": "legal_contract",
        "title": "Software License Agreement",
        "content": "This license grants non-exclusive rights to use the software. The licensee may not sublicense or transfer these rights without explicit written consent. However, the licensor reserves the right to terminate this agreement at any time without cause. In the event of termination, all copies must be destroyed within 30 days. Disputes shall be resolved through binding arbitration.",
        "ground_truth": "partial",
        "reason": "Termination clause conflicts with usage rights; arbitration requirement may not be enforceable in all jurisdictions",
    },
    {
        "domain": "legal_contract",
        "title": "Non-Disclosure Agreement",
        "content": "Receiving party agrees not to disclose any confidential information for a period of 5 years from the date of disclosure. This obligation survives termination of the business relationship. Exceptions include information already in the public domain or independently developed. The definition of 'confidential information' is not further specified.",
        "ground_truth": "undefined",
        "reason": "Critical term 'confidential information' left undefined, making scope unclear",
    },
    {
        "domain": "legal_contract",
        "title": "Service Level Agreement",
        "content": "Provider guarantees 99.9% uptime measured monthly. Downtime excludes scheduled maintenance windows of up to 4 hours per month. Force majeure events include natural disasters, government actions, and 'other circumstances beyond reasonable control.' Credits for downtime are 5% of monthly fee per hour of downtime, capped at 50% of monthly fee.",
        "ground_truth": "partial",
        "reason": "Force majeure clause is vague; credit calculation may not cover actual damages",
    },
    {
        "domain": "legal_contract",
        "title": "Employment Contract",
        "content": "Employee agrees to work exclusively for Employer during business hours. Non-compete clause restricts employment with competitors for 12 months post-termination within a 50-mile radius. Compensation is $X annually, subject to performance review. Termination may be with or without cause, requiring 2 weeks notice from either party.",
        "ground_truth": "partial",
        "reason": "Non-compete may be unenforceable depending on jurisdiction; performance review criteria unspecified",
    },
]

# Medical/healthcare instructions
MEDICAL_INSTRUCTIONS = [
    {
        "domain": "medical",
        "title": "Medication Dosage Protocol",
        "content": "Administer 500mg of medication X every 8 hours for 10 days. Take with food to reduce gastric irritation. If patient experiences severe allergic reaction (difficulty breathing, swelling), discontinue immediately and seek emergency care. For mild side effects (nausea, headache), continue treatment and monitor. Elderly patients (>65) may require dose adjustment, but specific guidelines are not provided.",
        "ground_truth": "partial",
        "reason": "Elderly dosing unspecified; 'severe' vs 'mild' reaction criteria subjective",
    },
    {
        "domain": "medical",
        "title": "Surgical Pre-Op Instructions",
        "content": "Patient must fast for 8 hours before procedure. Clear liquids allowed up to 2 hours before arrival. Regular medications should be taken with small sip of water unless otherwise directed by physician. Blood thinners must be discontinued 5 days prior. Diabetic patients should consult their endocrinologist regarding insulin adjustment on the day of surgery.",
        "ground_truth": "correct",
        "reason": "Clear, specific, and complete instructions with appropriate exceptions",
    },
    {
        "domain": "medical",
        "title": "Emergency Triage Protocol",
        "content": "Priority 1: Immediate life-threatening conditions (airway compromise, severe hemorrhage). Priority 2: Urgent but stable (fractures, moderate pain). Priority 3: Non-urgent (minor lacerations, chronic complaints). When resources are insufficient for all Priority 1 patients, allocate based on 'greatest likelihood of benefit with least resource utilization.' No further guidance provided for tie-breaking.",
        "ground_truth": "undefined",
        "reason": "Resource allocation criterion is vague and ethically contested without clear tie-breaking",
    },
]

# System design specifications
SYSTEM_DESIGNS = [
    {
        "domain": "system_design",
        "title": "API Rate Limiting",
        "content": "Implement rate limiting of 100 requests per minute per user. Use sliding window algorithm for accuracy. When limit is exceeded, return 429 Too Many Requests with Retry-After header. Bypass rate limiting for premium tier users. No specification for handling burst traffic or whether unused quota carries over between windows.",
        "ground_truth": "partial",
        "reason": "Burst handling unspecified; quota carryover behavior undefined",
    },
    {
        "domain": "system_design",
        "title": "Data Replication Strategy",
        "content": "Primary database in us-east-1 with read replicas in eu-west-1 and ap-southeast-1. Replication should be asynchronous with eventual consistency. Maximum acceptable replication lag is 'as low as possible.' Conflict resolution follows last-write-wins based on server timestamp. No mechanism specified for detecting or resolving conflicts during network partitions.",
        "ground_truth": "undefined",
        "reason": "'As low as possible' is not a measurable requirement; conflict resolution during partitions unspecified",
    },
    {
        "domain": "system_design",
        "title": "Caching Layer Design",
        "content": "Implement Redis cache with 1-hour TTL for frequently accessed data. Cache invalidation must occur on any data mutation. Use write-through strategy to ensure consistency. Cache size limited to 4GB; eviction policy should be LRU. Hot key problem (single key accessed >10000/s) should be handled but specific strategy not prescribed.",
        "ground_truth": "partial",
        "reason": "Hot key handling required but approach unspecified, leaving implementation ambiguity",
    },
    {
        "domain": "system_design",
        "title": "Event-Driven Architecture",
        "content": "Services communicate exclusively through event bus (Kafka). Events are immutable and append-only. Consumers must handle at-least-once delivery semantics. Event schema versioning is required but migration strategy for breaking changes is 'to be determined.' No dead letter queue or retry mechanism specified for failed consumers.",
        "ground_truth": "undefined",
        "reason": "Schema migration strategy TBD; failure handling for consumers unspecified",
    },
]

# Business rules
BUSINESS_RULES = [
    {
        "domain": "business_rule",
        "title": "Pricing Policy",
        "content": "Standard discount of 10% for orders over $1000. Additional 5% discount for repeat customers. Discounts are cumulative. However, total discount cannot exceed 20% under any circumstances. Seasonal promotions may override these rules during Q4. Specific override mechanics not documented.",
        "ground_truth": "partial",
        "reason": "Q4 override behavior unspecified; interaction between rules unclear at boundaries",
    },
    {
        "domain": "business_rule",
        "title": "Refund Policy",
        "content": "Full refund within 30 days of purchase. Partial refund (50%) between 31-60 days. No refund after 60 days. Items must be unused and in original packaging. Manager discretion allows exceptions 'in special circumstances.' No criteria provided for what constitutes a special circumstance or what exceptions are permissible.",
        "ground_truth": "partial",
        "reason": "Manager exception clause is unconstrained, creating ambiguity about actual policy",
    },
    {
        "domain": "business_rule",
        "title": "Approval Workflow",
        "content": "Expenses under $500 require team lead approval. Expenses $500-$5000 require department head approval. Expenses over $5000 require VP approval. If approver is unavailable (vacation, sick leave), escalation goes to 'next available person at same or higher level.' No definition of unavailable timeframe or how to determine next available person.",
        "ground_truth": "undefined",
        "reason": "Escalation path ambiguous; 'unavailable' and 'next available' undefined",
    },
]

# Academic policies
ACADEMIC_POLICIES = [
    {
        "domain": "academic",
        "title": "Grade Appeal Process",
        "content": "Students may appeal final grades within 10 business days of grade posting. Appeals must be submitted in writing with supporting evidence. Initial review by course instructor. If unresolved, escalates to department committee. Committee decision is final. No specification of what constitutes valid grounds for appeal or standard of review.",
        "ground_truth": "partial",
        "reason": "Grounds for appeal unspecified; review standard undefined",
    },
    {
        "domain": "academic",
        "title": "Academic Integrity Violation",
        "content": "First offense: Course failure and permanent record notation. Second offense: Academic probation for one semester. Third offense: Recommendation for expulsion. Students have right to hearing before academic board. 'Collaboration vs. plagiarism' boundary determined by 'reasonable academic judgment' without specific criteria.",
        "ground_truth": "undefined",
        "reason": "Critical distinction (collaboration vs. plagiarism) left to undefined 'reasonable judgment'",
    },
]

# Financial regulations
FINANCIAL_REGULATIONS = [
    {
        "domain": "financial",
        "title": "Transaction Reporting Threshold",
        "content": "All cash transactions over $10,000 must be reported to regulatory authority within 15 days. Structured transactions (multiple transactions designed to avoid threshold) must also be reported if they 'appear suspicious.' Daily transactions between $3,000-$10,000 require enhanced due diligence. Definition of 'suspicious' includes but is not limited to: unusual patterns, customer behavior, or transaction purpose.",
        "ground_truth": "partial",
        "reason": "'Suspicious' definition is open-ended; enhanced due diligence procedures unspecified",
    },
    {
        "domain": "financial",
        "title": "Investment Suitability Rule",
        "content": "Financial advisors must recommend only suitable investments based on customer's financial situation, investment objectives, and risk tolerance. Suitability assessment must be updated annually. Products classified as conservative, moderate, or aggressive. No guidance provided for customers whose risk tolerance conflicts with their financial situation (e.g., high income but low risk tolerance near retirement).",
        "ground_truth": "undefined",
        "reason": "Conflicting factors (situation vs. tolerance) with no tie-breaking guidance",
    },
]


class CrossDomainStressor:
    """Generates stress test cases from domains outside the generator's scope.
    
    Tests whether the Doctor's reasoning generalizes to:
    - Legal language and contract structures
    - Medical protocols with safety implications
    - System design with technical trade-offs
    - Business rules with policy ambiguities
    - Academic regulations
    - Financial compliance requirements
    
    These domains use different vocabularies, structures, and ambiguity patterns
    than the generator's domains, testing true generalization.
    """
    
    def __init__(self, seed: int = 42):
        self.rng = random.Random(seed)
        self.case_counter = 0
        
        self.domain_sources = {
            "legal_contract": LEGAL_CONTRACTS,
            "medical": MEDICAL_INSTRUCTIONS,
            "system_design": SYSTEM_DESIGNS,
            "business_rule": BUSINESS_RULES,
            "academic": ACADEMIC_POLICIES,
            "financial": FINANCIAL_REGULATIONS,
        }
    
    def generate_cases(
        self,
        n: int = 20,
        domains: List[str] | None = None,
    ) -> List[StressCase]:
        """Generate cross-domain stress cases.
        
        Args:
            n: Number of cases to generate
            domains: Specific domains to sample from (None = all)
            
        Returns:
            List of StressCase objects
        """
        if domains is None:
            domains = list(self.domain_sources.keys())
        else:
            # Validate domains
            for d in domains:
                if d not in self.domain_sources:
                    raise ValueError(f"Unknown domain: {d}. Available: {list(self.domain_sources.keys())}")
        
        cases = []
        sources = [(d, self.domain_sources[d]) for d in domains]
        
        # Distribute across selected domains
        cases_per_domain = max(1, n // len(sources))
        remainder = n - cases_per_domain * len(sources)
        
        for domain, source_data in sources:
            count = cases_per_domain + (1 if remainder > 0 else 0)
            remainder = max(0, remainder - 1)
            
            # Sample with replacement
            selected = self.rng.choices(source_data, k=count)
            
            for item in selected:
                case = self._create_case(item, domain)
                cases.append(case)
        
        self.rng.shuffle(cases)
        return cases
    
    def _create_case(self, item: Dict[str, Any], domain: str) -> StressCase:
        """Create a StressCase from a cross-domain item."""
        self.case_counter += 1
        case_id = f"CD-{self.case_counter:04d}"
        
        prompt = self._build_prompt(item, domain)
        
        return StressCase(
            case_id=case_id,
            prompt=prompt,
            stress_kind=StressKind.CROSS_DOMAIN,
            ground_truth=item["ground_truth"],
            metadata={
                "source_domain": domain,
                "title": item.get("title", "unknown"),
                "reason": item.get("reason", ""),
            },
        )
    
    def _build_prompt(self, item: Dict[str, Any], domain: str) -> str:
        """Build a prompt from a cross-domain item."""
        return (
            f"[{domain.upper()}] {item['title']}\n"
            f"Content: {item['content']}\n"
            f"Issue: {item.get('reason', 'Assessment needed')}\n"
            f"PROPOSED RESPONSE: Expert analysis of the specification, "
            f"identifying ambiguities, conflicts, and completeness."
        )
