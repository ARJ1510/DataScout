import streamlit as st
import pandas as pd
import os
from data_utils import extract_text_from_pdf, extract_text_from_doc
from Cleaning import clean_dataframe_with_ai
from eda_utils import (
    generate_basic_stats,
    create_categorical_plot,
    create_numerical_plot,
    generate_correlation_heatmap_fig
)
from llm_utils import ask_llama
import io

st.set_page_config(page_title="DataScout 🎯", layout="wide")
st.title("DataScout 🎯")
st.markdown("Your buddy for analytics.")

# This line ensures the API key is securely loaded via secrets
os.environ["TOGETHER_API_KEY"] = st.secrets["TOGETHER_API_KEY"]

uploaded_file = st.file_uploader("📁 Upload a file", type=["csv", "xlsx", "xls", "pdf", "docx", "txt"])

if uploaded_file:
    file_extension = uploaded_file.name.split(".")[-1].lower()
    try:
        if file_extension == "csv":
            file_size_mb = uploaded_file.size / (1024 * 1024)
            if file_size_mb > 100:
                st.warning(f"⚠️ File is large ({file_size_mb:.2f} MB). Analyzing a sample of the first 1,000,000 rows.")
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

    df_cleaned, original_shape = clean_dataframe_with_ai(df)
    st.subheader("🧼 Cleaned Data Preview")
    st.dataframe(df_cleaned)
    csv = df_cleaned.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 Download Cleaned Data as CSV", data=csv,
        file_name='cleaned_data.csv', mime='text/csv'
    )
    st.success(f"✅ Cleaned: From {original_shape[0]} rows to {df_cleaned.shape[0]} rows.")
    st.session_state.df = df_cleaned

    st.subheader("📈 Dataset Summary")
    st.write("✅ Rows:", df_cleaned.shape[0], "| Columns:", df_cleaned.shape[1])
    stats_df = generate_basic_stats(df_cleaned)
    st.write(stats_df)

    st.subheader("📊 Visual Analysis")
    cat_cols = df_cleaned.select_dtypes(include='object').columns.tolist()
    num_cols = df_cleaned.select_dtypes(include='number').columns.tolist()
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### Categorical Column Analysis")
        if cat_cols:
            selected_cat_col = st.selectbox("Select a Categorical Column", cat_cols)
            if selected_cat_col:
                fig = create_categorical_plot(df_cleaned, selected_cat_col)
                st.plotly_chart(fig, use_container_width=True)
                buf = io.BytesIO(); fig.write_image(buf, format="png", scale=2)
                st.download_button(
                    label=f"📥 Download '{selected_cat_col}' Chart", data=buf.getvalue(),
                    file_name=f"{selected_cat_col}_chart.png", mime="image/png", key=f'cat_{selected_cat_col}'
                )
    with col2:
        st.markdown("#### Numerical Column Analysis")
        if num_cols:
            selected_num_col = st.selectbox("Select a Numerical Column", num_cols)
            if selected_num_col:
                fig = create_numerical_plot(df_cleaned, selected_num_col)
                st.plotly_chart(fig, use_container_width=True)
                buf = io.BytesIO(); fig.write_image(buf, format="png", scale=2)
                st.download_button(
                    label=f"📥 Download '{selected_num_col}' Chart", data=buf.getvalue(),
                    file_name=f"{selected_num_col}_chart.png", mime="image/png", key=f'num_{selected_num_col}'
                )

    st.subheader("📉 Correlation Heatmap")
    heatmap_fig = generate_correlation_heatmap_fig(df_cleaned)
    if heatmap_fig:
        st.plotly_chart(heatmap_fig, use_container_width=True)
        buf = io.BytesIO(); heatmap_fig.write_image(buf, format="png", scale=2)
        st.download_button(
            label="📥 Download Heatmap", data=buf.getvalue(),
            file_name="correlation_heatmap.png", mime="image/png"
        )
    else:
        st.info("Not enough numeric columns to show a correlation heatmap.")

    st.subheader("🧠 Ask AI about your data")
    user_question = st.text_input("🔍 Ask a question")
    if st.button("Submit Question"):
        if user_question.strip():
            with st.spinner("🤖 LLaMA is thinking..."):
                data_sample = df_cleaned.head(10).to_csv(index=False)
                prompt = f"Based on the data, answer: {user_question}\n\nData:\n{data_sample}"
                # Pass the key from secrets to the function call
                api_key = st.secrets["TOGETHER_API_KEY"]
                response = ask_llama(prompt, api_key)
                st.markdown("### 🤖 LLaMA's Response"); st.write(response)