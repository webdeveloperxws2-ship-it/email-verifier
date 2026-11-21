# app.py
import streamlit as st
import pandas as pd
from validator import check_syntax, check_mx, check_smtp, is_disposable

st.set_page_config(page_title="Bulk Email Verifier", layout="wide")
st.title("📧 Bulk Email Verifier")
st.write("Paste your emails or upload a file to verify their deliverability.")

# Input method
option = st.radio("Choose Input Method:", ["Paste emails", "Upload file"])

emails = []
if option == "Paste emails":
    text = st.text_area("Paste emails here (one per line):", height=200)
    if text:
        emails = [e.strip() for e in text.splitlines() if e.strip()]
else:
    file = st.file_uploader("Upload CSV, Excel, or TXT file", type=["csv", "xlsx", "txt"])
    if file:
        if file.name.endswith(".csv"):
            df = pd.read_csv(file)
        elif file.name.endswith(".xlsx"):
            df = pd.read_excel(file)
        else:
            df = pd.read_csv(file, header=None)
        
        # Assuming emails are in the first column
        emails = df.iloc[:, 0].dropna().astype(str).tolist()

if st.button("🚀 Verify Emails"):
    if not emails:
        st.warning("Please provide at least one email.")
    else:
        results = []
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i, email in enumerate(emails):
            status_text.text(f"Verifying {i+1}/{len(emails)}: {email}")
            
            domain = email.split("@")[-1] if "@" in email else ""
            
            # Validation Steps
            syntax_ok = check_syntax(email)
            mx_ok = check_mx(domain) if syntax_ok else False
            smtp_ok = check_smtp(email, domain) if mx_ok else False
            disp = is_disposable(email) if syntax_ok else False

            # Determine Status
            if not syntax_ok:
                status = "Invalid (Syntax)"
            elif not mx_ok:
                status = "Invalid (No MX Record)"
            elif disp:
                status = "Disposable / Fake"
            elif smtp_ok:
                status = "Valid (Mailbox Confirmed)"
            else:
                status = "Domain Valid (Mailbox Unverified)" 

            results.append({"Email": email, "Status": status})
            progress_bar.progress((i + 1) / len(emails))

        status_text.text("Verification Complete! ✅")
        
        # Show Results
        df_result = pd.DataFrame(results)
        st.dataframe(df_result, width='stretch')

        # Export options
        csv_all = df_result.to_csv(index=False).encode("utf-8")
        
        valid_df = df_result[df_result["Status"] == "Valid / Deliverable"]
        csv_valid = valid_df.to_csv(index=False).encode("utf-8")

        col1, col2 = st.columns(2)
        with col1:
            st.download_button("⬇️ Download ALL (With Status)", csv_all, "all_results.csv", "text/csv")
        with col2:
            st.download_button("⬇️ Download VALID Only", csv_valid, "valid_only.csv", "text/csv")