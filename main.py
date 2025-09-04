import streamlit as st
import pandas as pd
import os
import io
import tempfile

from data_utils import extract_text_from_pdf, extract_text_from_doc
from Cleaning import clean_dataframe_with_ai
from eda_utils import (
    generate_basic_stats,
    create_categorical_plot,
    create_numerical_plot,
    generate_correlation_heatmap_fig
)
from llm_utils import ask_llama

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

# App Config
st.set_page_config(page_title="DataScout", layout="wide")
st.title("DataScout 🎯")
st.caption("Your AI-powered data buddy for cleaning & analysis.")

# API Key Check

if "TOGETHER_API_KEY" not in st.secrets:
    st.error("TOGETHER_API_KEY not found in secrets. Please add it to your app's settings.")
    st.stop()

# File Upload

uploaded_file = st.file_uploader("📁 Upload a file", type=["csv", "xlsx", "xls", "pdf", "docx", "txt"])

if uploaded_file:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    try:
        if file_extension == "csv":
            file_size_mb = uploaded_file.size / (1024 * 1024)
            if file_size_mb > 100:
                st.warning(f"⚠️ Large file ({file_size_mb:.2f} MB). Sampling first 1,000,000 rows.")
                df = pd.read_csv(uploaded_file, low_memory=False, nrows=1000000)
            else:
                df = pd.read_csv(uploaded_file, low_memory=False)
        elif file_extension in ["xlsx", "xls"]:
            df = pd.read_excel(uploaded_file)
        elif file_extension == "pdf":
            st.text_area("📄 Extracted Text", extract_text_from_pdf(uploaded_file)["Content"][0], height=300)
            st.stop()
        elif file_extension == "docx":
            st.text_area("📄 Extracted Text", extract_text_from_doc(uploaded_file)["Content"][0], height=300)
            st.stop()
        elif file_extension == "txt":
            st.text_area("📄 Extracted Text", uploaded_file.read().decode("utf-8"), height=300)
            st.stop()
    except Exception as e:
        st.error(f"⚠️ Error reading the file: {e}")
        st.stop()

    # AI Cleaning
    df_cleaned, original_shape = clean_dataframe_with_ai(df)

    # Dashboard Tabs

    tab1, tab2, tab3, tab4 = st.tabs(["🧼 Cleaning & Data", "📈 EDA Summary", "📊 Visuals", "🤖 AI Insights"])

    # Tab 1: Cleaned Data
    with tab1:
        st.subheader("🧼 Cleaned Data Preview")
        st.dataframe(df_cleaned)
        csv = df_cleaned.to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download Cleaned Data", csv, "cleaned_data.csv", "text/csv")
        st.success(f"✅ Cleaned: From {original_shape[0]} → {df_cleaned.shape[0]} rows")

    # Tab 2: EDA Summary
    with tab2:
        st.subheader("📈 Dataset Summary")
        st.write("✅ Rows:", df_cleaned.shape[0], "| Columns:", df_cleaned.shape[1])
        stats_df = generate_basic_stats(df_cleaned)
        st.write(stats_df)

    # Tab 3: Visuals
    with tab3:
        st.subheader("📊 Visual Analysis")
        cat_cols = df_cleaned.select_dtypes(include='object').columns.tolist()
        num_cols = df_cleaned.select_dtypes(include='number').columns.tolist()
        col1, col2 = st.columns(2)

        with col1:
            if cat_cols:
                selected_cat_col = st.selectbox("Select a Categorical Column", cat_cols)
                if selected_cat_col:
                    fig = create_categorical_plot(df_cleaned, selected_cat_col, show_percentage=True)
                    if fig: st.plotly_chart(fig, use_container_width=True)

        with col2:
            if num_cols:
                selected_num_col = st.selectbox("Select a Numerical Column", num_cols)
                if selected_num_col:
                    fig = create_numerical_plot(df_cleaned, selected_num_col, add_kde=True)
                    if fig: st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 📉 Correlation Heatmap")
        heatmap_fig = generate_correlation_heatmap_fig(df_cleaned)
        if heatmap_fig:
            st.plotly_chart(heatmap_fig, use_container_width=True)
        else:
            st.info("Not enough numeric columns for a heatmap.")

    # Tab 4: AI Insights
    with tab4:
        st.subheader("🤖 AI Insights Report")

        ai_insights_text = ""

        if st.button("Generate AI Insights"):
            with st.spinner("Analyzing dataset with AI..."):
                stats_summary = generate_basic_stats(df_cleaned).to_string()
                sample_data = df_cleaned.head(5).to_csv(index=False)
                prompt = f"""
                You are a professional data analyst.
                Based on the dataset summary and sample, provide a short insights report.

                ### Dataset Summary:
                {stats_summary}

                ### Sample Data:
                {sample_data}

                Please return insights as bullet points (3-6 points), highlighting:
                - Data quality issues (missing values, outliers, etc.)
                - Interesting patterns (skewed distributions, dominant categories)
                - Any potential next steps
                """
                api_key = st.secrets["TOGETHER_API_KEY"]
                response = ask_llama(prompt, api_key)
                ai_insights_text = response
                st.markdown("### 📌 AI Insights")
                st.write(response)

        # PDF Download
        if ai_insights_text:
            if st.button("📥 Download Insights as PDF"):
                styles = getSampleStyleSheet()
                doc_elements = []

                doc_elements.append(Paragraph("DataScout AI Insights Report", styles["Title"]))
                doc_elements.append(Spacer(1, 20))

                doc_elements.append(Paragraph("Dataset Overview", styles["Heading2"]))
                doc_elements.append(Paragraph(f"Rows: {df_cleaned.shape[0]}, Columns: {df_cleaned.shape[1]}", styles["Normal"]))
                doc_elements.append(Spacer(1, 12))

                doc_elements.append(Paragraph("AI Insights", styles["Heading2"]))
                doc_elements.append(Paragraph(ai_insights_text.replace("\n", "<br/>"), styles["Normal"]))

                with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_file:
                    pdf_path = tmp_file.name
                    doc = SimpleDocTemplate(pdf_path)
                    doc.build(doc_elements)

                    with open(pdf_path, "rb") as f:
                        st.download_button(
                            label="📥 Download PDF Report",
                            data=f,
                            file_name="DataScout_AI_Insights.pdf",
                            mime="application/pdf"
                        )

        # --- AI Q&A ---
        st.subheader("💬 Ask AI a Question")
        user_question = st.text_input("🔍 Ask about your dataset")
        if st.button("Submit Question"):
            if user_question.strip():
                with st.spinner("🤖 LLaMA is thinking..."):
                    stats_summary = generate_basic_stats(df_cleaned).to_string()
                    data_sample = df_cleaned.head(5).to_csv(index=False)
                    prompt = f"""
                    You are a data analyst. Use the dataset summary and sample to answer.

                    ### Dataset Summary:
                    {stats_summary}

                    ### Sample Data:
                    {data_sample}

                    ### User Question:
                    {user_question}
                    """
                    api_key = st.secrets["TOGETHER_API_KEY"]
                    response = ask_llama(prompt, api_key)
                    st.markdown("### 🤖 LLaMA's Response")
                    st.write(response)
