import base64
import os
from datetime import date

import requests
import streamlit as st
from dotenv import load_dotenv

load_dotenv()
BACKEND_URL = os.getenv("BACKEND_URL", "http://127.0.0.1:8000").rstrip("/")

st.set_page_config(page_title="LegalEase", page_icon="⚖️", layout="wide")
st.markdown(
    """<style>
    .main-title{text-align:center;font-size:2.4rem;font-weight:700}
    .subtitle{text-align:center;color:#8b95a5;margin-bottom:1.5rem}
    .preview{background:#111827;color:#f3f4f6;padding:24px;border-radius:14px;
    max-height:650px;overflow-y:auto;line-height:1.65;border:1px solid #263244}
    .notice{background:#fff7ed;border-left:4px solid #f97316;padding:12px 16px;
    border-radius:6px;color:#7c2d12}
    </style>""",
    unsafe_allow_html=True,
)
st.markdown('<div class="main-title">⚖️ LegalEase</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">AI-powered legal document drafting and export</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="notice"><b>Review notice:</b> LegalEase creates AI-generated drafts. '
    'It is not legal advice. Review jurisdiction-specific requirements with a qualified '
    'legal professional before signing.</div>',
    unsafe_allow_html=True,
)

if "document" not in st.session_state:
    st.session_state.document = ""

with st.sidebar:
    st.header("Document details")
    document_type = st.selectbox(
        "Document type",
        ["Employment Contract", "Non-Disclosure Agreement", "Lease Agreement",
         "Employment Offer Letter", "Freelance Work Contract", "Service Agreement",
         "General Agreement", "Custom Legal Document"],
    )
    if document_type == "Custom Legal Document":
        document_type = st.text_input("Custom document type", "Custom Legal Document")

    parties = st.text_area(
        "Parties involved",
        placeholder="Jane Doe (Service Provider), TechNova Inc. (Client)",
        height=110,
    )
    terms = st.text_area(
        "Terms & conditions",
        placeholder="Payment within 30 days; Confidentiality must be maintained; Either party may terminate with 15 days notice",
        height=180,
        help="Separate clauses with semicolons.",
    )
    effective_date = st.date_input("Effective date", value=date.today())
    logo = st.file_uploader("Optional logo", type=["png", "jpg", "jpeg"])
    generate = st.button("Generate Document", type="primary", use_container_width=True)

if generate:
    if not parties.strip() or not terms.strip():
        st.error("Please enter the parties and terms before generating.")
    else:
        payload = {
            "document_type": document_type.strip(),
            "parties": parties.strip(),
            "terms": terms.strip(),
            "effective_date": effective_date.isoformat(),
        }
        with st.spinner("Generating your draft..."):
            try:
                response = requests.post(f"{BACKEND_URL}/generate", json=payload, timeout=120)
                if response.ok:
                    st.session_state.document = response.json()["content"]
                    st.success("Document generated.")
                else:
                    try:
                        detail = response.json().get("detail", response.text)
                    except ValueError:
                        detail = response.text
                    st.error(f"Backend error: {detail}")
            except requests.RequestException as exc:
                st.error(f"Could not reach FastAPI. Check BACKEND_URL. Details: {exc}")

left, right = st.columns([1.25, 1])
with left:
    st.subheader("Editable document")
    edited = st.text_area(
        "Edit generated content",
        value=st.session_state.document,
        height=650,
        label_visibility="collapsed",
    )
    st.session_state.document = edited

with right:
    st.subheader("Preview")
    if st.session_state.document.strip():
        escaped = (
            st.session_state.document.replace("&", "&amp;")
            .replace("<", "&lt;").replace(">", "&gt;").replace("\n", "<br>")
        )
        st.markdown(f'<div class="preview">{escaped}</div>', unsafe_allow_html=True)
    else:
        st.info("Generate a document to see the preview.")

st.divider()
st.subheader("Export")

if st.session_state.document.strip():
    logo_b64 = None
    if logo:
        logo_b64 = base64.b64encode(logo.getvalue()).decode("utf-8")
    export_payload = {
        "document_type": document_type,
        "content": st.session_state.document,
        "terms": terms,
        "logo_base64": logo_b64,
    }

    c1, c2, c3 = st.columns(3)
    with c1:
        try:
            r = requests.post(f"{BACKEND_URL}/export/txt", json=export_payload, timeout=30)
            if r.ok:
                st.download_button("Download TXT", r.content, "legalease_document.txt",
                                   "text/plain", use_container_width=True)
            else:
                st.error("TXT export failed.")
        except requests.RequestException:
            st.error("Backend unavailable.")
    with c2:
        try:
            r = requests.post(f"{BACKEND_URL}/export/docx", json=export_payload, timeout=30)
            if r.ok:
                st.download_button(
                    "Download DOCX", r.content, "legalease_document.docx",
                    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
                    use_container_width=True,
                )
            else:
                st.error("DOCX export failed.")
        except requests.RequestException:
            st.error("Backend unavailable.")
    with c3:
        try:
            r = requests.post(f"{BACKEND_URL}/export/pdf", json=export_payload, timeout=30)
            if r.ok:
                st.download_button("Download PDF", r.content, "legalease_document.pdf",
                                   "application/pdf", use_container_width=True)
            else:
                st.error("PDF export failed.")
        except requests.RequestException:
            st.error("Backend unavailable.")
else:
    st.caption("Generate a document before exporting.")
