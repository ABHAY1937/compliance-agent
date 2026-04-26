from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
import anthropic
import json
from datetime import datetime, date
import random
from dotenv import load_dotenv
import os

load_dotenv()
client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))

app = FastAPI(title="AI Compliance Monitoring - Report Drafting Agent")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = anthropic.Anthropic()

# --- Mock validated operational metrics (as would come from Agent 3 validation) ---
SAMPLE_METRICS = {
    "institution_name": "FinCorp Global Bank",
    "institution_id": "FCB-2024-001",
    "reporting_period": "Q1 2025",
    "report_date": str(date.today()),
    "validated_by": "Agent 3 - Data Validation Agent",
    "validation_timestamp": datetime.now().isoformat(),

    "capital_adequacy": {
        "tier1_capital": 4250000000,
        "tier2_capital": 850000000,
        "total_capital": 5100000000,
        "risk_weighted_assets": 38200000000,
        "tier1_ratio": 11.13,
        "total_capital_ratio": 13.35,
        "minimum_required_tier1": 6.0,
        "minimum_required_total": 8.0,
        "status": "COMPLIANT"
    },

    "liquidity": {
        "hqla_level1": 6200000000,
        "hqla_level2a": 1100000000,
        "hqla_level2b": 420000000,
        "total_hqla": 7720000000,
        "net_cash_outflows_30d": 5980000000,
        "lcr": 129.1,
        "minimum_required_lcr": 100.0,
        "nsfr": 112.4,
        "minimum_required_nsfr": 100.0,
        "status": "COMPLIANT"
    },

    "credit_risk": {
        "total_loan_portfolio": 22500000000,
        "non_performing_loans": 315000000,
        "npl_ratio": 1.40,
        "loan_loss_provisions": 412000000,
        "provision_coverage_ratio": 130.8,
        "large_exposures_count": 3,
        "large_exposures_limit": 10,
        "status": "COMPLIANT"
    },

    "aml_compliance": {
        "transactions_monitored": 4872310,
        "suspicious_activity_reports": 47,
        "high_risk_customers_reviewed": 1243,
        "kyc_completeness_rate": 98.7,
        "pep_screening_coverage": 100.0,
        "sanctions_screening_coverage": 100.0,
        "aml_alerts_resolved_within_sla": 96.2,
        "status": "COMPLIANT"
    },

    "operational_risk": {
        "operational_loss_events": 12,
        "total_operational_losses": 2840000,
        "cyber_incidents": 2,
        "regulatory_breaches": 0,
        "bcm_test_completion": 100.0,
        "it_audit_findings_open": 4,
        "it_audit_findings_critical": 0,
        "status": "MINOR_ISSUES"
    },

    "data_quality": {
        "completeness_score": 98.4,
        "accuracy_score": 97.1,
        "timeliness_score": 99.2,
        "overall_dq_score": 98.2,
        "fields_validated": 2847,
        "fields_with_errors": 51,
        "validation_passed": True
    }
}

REGULATORY_TEMPLATES = {
    "BASEL_III": {
        "name": "Basel III Capital & Liquidity Report",
        "regulator": "Bank for International Settlements / Local Central Bank",
        "sections": ["Capital Adequacy", "Liquidity Coverage", "Net Stable Funding"]
    },
    "AML_CTF": {
        "name": "AML/CTF Compliance Report",
        "regulator": "Financial Intelligence Unit (FIU)",
        "sections": ["Transaction Monitoring", "Customer Due Diligence", "SAR Filing", "Sanctions Screening"]
    },
    "OPERATIONAL_RISK": {
        "name": "Operational Risk & Incident Report",
        "regulator": "Prudential Regulatory Authority",
        "sections": ["Loss Events", "Cyber Security", "Business Continuity", "IT Audit"]
    },
    "COMPREHENSIVE": {
        "name": "Comprehensive Regulatory Compliance Report",
        "regulator": "Multiple Regulators",
        "sections": ["Capital Adequacy", "Liquidity", "Credit Risk", "AML/CTF", "Operational Risk"]
    }
}


class ReportRequest(BaseModel):
    template_type: str = "COMPREHENSIVE"
    institution_name: Optional[str] = None
    custom_notes: Optional[str] = None
    include_recommendations: bool = True


class ChatMessage(BaseModel):
    message: str
    report_context: Optional[Dict[str, Any]] = None


@app.get("/")
def root():
    return {"status": "AI Compliance Report Drafting Agent is running", "version": "1.0.0"}


@app.get("/metrics")
def get_metrics():
    return SAMPLE_METRICS


@app.get("/templates")
def get_templates():
    return REGULATORY_TEMPLATES


@app.post("/generate-report")
async def generate_report(request: ReportRequest):
    metrics = SAMPLE_METRICS.copy()
    if request.institution_name:
        metrics["institution_name"] = request.institution_name

    template = REGULATORY_TEMPLATES.get(request.template_type, REGULATORY_TEMPLATES["COMPREHENSIVE"])

    prompt = f"""You are an expert regulatory compliance officer and report drafting agent (Agent 4 in an AI compliance monitoring pipeline).

You have received validated operational metrics from Agent 3 (Data Validation Agent). Your task is to convert these validated metrics into a structured regulatory report.

## Validated Metrics Data:
{json.dumps(metrics, indent=2)}

## Report Template: {template['name']}
- Regulator: {template['regulator']}
- Required Sections: {', '.join(template['sections'])}
- Custom Notes: {request.custom_notes or 'None'}

## Your Task:
Generate a comprehensive, professional regulatory compliance report. The report must:

1. Map each internal data field to the appropriate regulatory reporting field
2. Calculate and present all required aggregate metrics
3. Highlight compliance status for each area (COMPLIANT / NON-COMPLIANT / MINOR ISSUES)
4. {"Include recommendations for any areas needing improvement" if request.include_recommendations else "Focus only on status reporting without recommendations"}
5. Handle any missing or partial data gracefully with appropriate notes
6. Follow professional regulatory report formatting standards

Return the report as a JSON object with this exact structure:
{{
  "report_metadata": {{
    "report_id": "unique ID",
    "report_title": "title",
    "institution": "name",
    "reporting_period": "period",
    "generated_at": "timestamp",
    "template_used": "template name",
    "regulator": "regulator name",
    "overall_compliance_status": "COMPLIANT/NON-COMPLIANT/PARTIAL",
    "overall_compliance_score": 0-100,
    "agent_id": "Agent-4-ReportDrafter"
  }},
  "executive_summary": {{
    "summary_text": "2-3 paragraph executive summary",
    "key_findings": ["finding1", "finding2", ...],
    "critical_alerts": ["alert1", ...] or []
  }},
  "sections": [
    {{
      "section_id": "S001",
      "section_name": "Section Name",
      "regulatory_reference": "Basel III Article X / FATF Recommendation Y",
      "compliance_status": "COMPLIANT",
      "compliance_score": 95,
      "metrics": [
        {{
          "field_name": "Internal Field",
          "regulatory_field": "Regulatory Field Name",
          "value": "value",
          "threshold": "threshold or N/A",
          "unit": "% or currency or count",
          "status": "PASS/FAIL/WARNING"
        }}
      ],
      "section_narrative": "Analysis paragraph",
      "recommendations": ["rec1", "rec2"] or []
    }}
  ],
  "data_quality_assessment": {{
    "overall_score": 98.2,
    "completeness": 98.4,
    "accuracy": 97.1,
    "timeliness": 99.2,
    "data_gaps": [] or ["gap1"],
    "notes": "Data quality narrative"
  }},
  "certification": {{
    "prepared_by": "Agent 4 - Report Drafting Agent",
    "validated_by": "Agent 3 - Data Validation Agent",
    "certification_statement": "statement",
    "submission_ready": true or false
  }}
}}

Return ONLY the JSON object, no other text."""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4000,
            messages=[{"role": "user", "content": prompt}]
        )

        raw = response.content[0].text.strip()
        # Strip markdown fences if present
        if raw.startswith("```"):
            raw = raw.split("\n", 1)[1]
            raw = raw.rsplit("```", 1)[0].strip()

        report = json.loads(raw)
        return {"success": True, "report": report, "metrics_used": metrics}

    except json.JSONDecodeError as e:
        raise HTTPException(status_code=500, detail=f"Failed to parse AI response as JSON: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/chat")
async def chat_with_agent(message: ChatMessage):
    context = ""
    if message.report_context:
        context = f"\n\nContext - Current Report Data:\n{json.dumps(message.report_context, indent=2)[:2000]}"

    prompt = f"""You are Agent 4 - the Report Drafting Agent in an AI Compliance Monitoring system. 
You are an expert in regulatory compliance, Basel III, AML/CTF, and financial reporting.
You help users understand compliance reports, explain metrics, and answer regulatory questions.
Be concise, professional, and helpful. Use bullet points when listing items.{context}

User question: {message.message}"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=800,
            messages=[{"role": "user", "content": prompt}]
        )
        return {"response": response.content[0].text}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
