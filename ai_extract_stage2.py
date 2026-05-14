import instructor
from google import genai
import json
import os
from dotenv import load_dotenv
from pydantic import BaseModel, Field
from typing import Optional

load_dotenv()

# ── 1. Same NoticeStructure as before — no change ─────────────────────────

class DocumentClassification(BaseModel):
    document_category: str = Field(
        description="""What type of document is this? Choose one of:
        college_notice, resume, research_paper, invoice, 
        admission_form, exam_result, fee_receipt, email, other"""
    )
    belongs_to_system: bool = Field(
        description="""Should this document be processed by the 
        college notice system? True only for college_notice type."""
    )
    reason: str = Field(
        description="One sentence explaining what this document is"
    )


class NoticeStructure(BaseModel):
    notice_type: str = Field(
        description="""Type of notice. One of: exam_reschedule, 
        event, fee_deadline, holiday, result, general"""
    )
    title: str = Field(
        description="Short clear title for the notice, max 10 words"
    )
    department: str = Field(
        description="Target department. Use 'all' if it applies to everyone"
    )
    audience: str = Field(
        description="""Who this notice is for. 
        E.g. '3rd year CSE', 'all students', 'faculty'"""
    )
    notice_date: Optional[str] = Field(
        default=None,
        description="Date notice was issued, YYYY-MM-DD format"
    )
    event_date: Optional[str] = Field(
        default=None,
        description="Main event or deadline date, YYYY-MM-DD format"
    )
    venue: Optional[str] = Field(
        default=None,
        description="Location or venue mentioned in the notice"
    )
    urgency: str = Field(
        description="Urgency level. One of: high, normal, low"
    )
    summary: str = Field(
        description="One sentence summary of the notice"
    )
    issued_by: Optional[str] = Field(
        default=None,
        description="Name and designation of person who issued notice"
    )
    action_required: Optional[str] = Field(
        default=None,
        description="What the reader needs to do, if anything"
    )
    confidence: float = Field(
        description="Confidence in extraction from 0.0 to 1.0"
    )


class FinalOutput(BaseModel):
    classification: DocumentClassification
    extracted_notice: Optional[NoticeStructure] = Field(
        default=None,
        description="Filled only if document_category is college_notice"
    )


# ── 2. Set up Instructor with Gemini ──────────────────────────────────────

genai_client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))

client = instructor.from_genai(
    client=genai_client,
    model="gemini-2.5-flash",
    mode=instructor.Mode.GENAI_STRUCTURED_OUTPUTS,
)


# ── 3. Extraction function ─────────────────────────────────────────────────

def extract_notice_fields(raw_text: str, source_file: str) -> FinalOutput:
    print(f"  Sending to Gemini for extraction...")

    result = client.chat.completions.create(
        messages=[
            {
                "role": "user",
                "content": f"""You are an intelligent document processing 
assistant for a college management system.

Your job has two steps:

STEP 1 - Classify the document:
Identify what type of document this is and whether it belongs 
in the college notice system.

STEP 2 - Extract fields (only if it is a college notice):
If and only if the document is a college notice, extract all 
relevant structured fields.

Rules:
- If a field is not mentioned, return null for optional fields
- For dates, always use YYYY-MM-DD format
- Urgency: high = exams/fees/deadlines, normal = events, low = info
- Never guess information not present in the text
- Confidence 0.9+ only if all key fields are clearly present

Document text:
---
{raw_text}
---

Classify and extract now."""
            }
        ],
        response_model=FinalOutput,
    )

    return result
# ── 4. Process all Stage 1 outputs ────────────────────────────────────────

def process_all_extractions():
    print("=== Stage 2: AI Field Extraction (Gemini) ===\n")

    output_files = [f for f in os.listdir("outputs") if f.endswith("_extracted.json")]

    if not output_files:
        print("  No Stage 1 output files found in outputs/ folder.")
        print("  Run stage1_extractor.py first.")
        return

    for filename in output_files:
        filepath = os.path.join("outputs", filename)

        with open(filepath, "r", encoding="utf-8") as f:
            stage1_data = json.load(f)

        raw_text = stage1_data.get("raw_text", "")
        source = stage1_data.get("file_name", filename)

        if not raw_text.strip():
            print(f"  Skipping {filename} — empty text")
            continue

        # Skip already processed files — saves API calls
        out_filename = filename.replace("_extracted.json", "_stage2.json")
        out_path = os.path.join("outputs", out_filename)

        if os.path.exists(out_path):
            print(f"  [SKIP] Already processed, skipping: {source}")
            continue

        print(f"\n  Processing: {source}")
        print(f"  Text length: {len(raw_text)} characters")

        try:
            result = extract_notice_fields(raw_text, source)

            classification = result.classification
            print(f"\n  Document category : {classification.document_category}")
            print(f"  Belongs to system : {classification.belongs_to_system}")
            print(f"  Reason            : {classification.reason}")

            if not classification.belongs_to_system:
                print(f"\n  ⏭  Not a college notice — logged and skipped")
                rejected = {
                    "source_file": source,
                    "category": classification.document_category,
                    "reason": classification.reason,
                    "action": "rejected"
                }
                reject_path = os.path.join(
                    "outputs",
                    out_filename.replace("_stage2.json", "_rejected.json")
                )
                with open(reject_path, "w", encoding="utf-8") as f:
                    json.dump(rejected, f, indent=2)
                continue

            notice = result.extracted_notice
            if not notice:
                print(f"\n  ⚠️  Classified as notice but extraction failed")
                continue

            fields = notice.model_dump()
            final_output = {
                "source_file": source,
                "file_type": stage1_data.get("file_type"),
                "processed_at": stage1_data.get("processed_at"),
                "category": classification.document_category,
                "extracted_fields": fields
            }

            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(final_output, f, indent=2, ensure_ascii=False)

            print(f"\n  ✅ Notice extracted successfully!")
            print(f"  Type      : {fields['notice_type']}")
            print(f"  Title     : {fields['title']}")
            print(f"  Audience  : {fields['audience']}")
            print(f"  Urgency   : {fields['urgency']}")
            print(f"  Confidence: {fields['confidence']}")
            print(f"  Summary   : {fields['summary']}")
            print(f"  Saved to  : {out_path}")

        except Exception as e:
            print(f"\n  ❌ Failed for {source}: {e}")


if __name__ == "__main__":
    process_all_extractions()