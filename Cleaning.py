import streamlit as st
import pandas as pd
import json
from llm_utils import ask_llama

def generate_cleaning_prompt(df):
    """Generates a detailed prompt for the AI to create a cleaning plan."""
    sample_data = df.head(15).to_csv()
    column_info = pd.DataFrame({
        'dtype': df.dtypes,
        'unique_values_sample': [df[col].unique()[:5] for col in df.columns]
    }).to_string()

    prompt = f"""
    You are an expert data scientist. Your task is to create a robust data cleaning plan.
    Look for:
    - Missing values (best imputation strategy)
    - Wrong data types (convert if needed)
    - Outliers (suggest handling: remove, cap, or flag)
    - Duplicate rows
    - Inconsistent text (standardize casing/whitespace)
    - Date/time parsing if applicable
    - Numeric scaling/normalization if needed

    **Column Information:**
    {column_info}

    **Data Sample (first 15 rows):**
    ```csv
    {sample_data}
    ```

    **Instructions:**
    Return a valid JSON object only, in this format:
    {{
      "cleaning_plan": [
        {{"operation": "handle_missing", "details": {{"column": "col_name", "strategy": "mean"}}}},
        {{"operation": "handle_outliers", "details": {{"column": "col_name", "method": "IQR"}}}},
        {{"operation": "scale_numeric", "details": {{"column": "col_name", "method": "minmax"}}}},
        {{"operation": "parse_dates", "details": {{"column": "col_name"}}}}
      ]
    }}
    """
    return prompt


def execute_cleaning_plan(df, plan):
    """Executes the cleaning plan provided by the AI."""
    df_cleaned = df.copy()
    try:
        plan_data = json.loads(plan)
        steps = plan_data.get("cleaning_plan", [])
    except json.JSONDecodeError:
        print("Error: AI did not return a valid JSON plan.")
        return df_cleaned

    for step in steps:
        op = step.get("operation")
        details = step.get("details", {})
        col = details.get("column")

        # 1. Handle Missing
        if op == "handle_missing" and col in df_cleaned.columns:
            strategy = details.get("strategy", "drop")
            if strategy == "median":
                df_cleaned[col].fillna(df_cleaned[col].median(), inplace=True)
            elif strategy == "mean":
                df_cleaned[col].fillna(df_cleaned[col].mean(), inplace=True)
            elif strategy == "mode":
                if not df_cleaned[col].mode().empty:
                    df_cleaned[col].fillna(df_cleaned[col].mode()[0], inplace=True)
            else:
                df_cleaned.dropna(subset=[col], inplace=True)

        # 2. Change Type
        elif op == "change_type" and col in df_cleaned.columns:
            new_type = details.get("new_type")
            if new_type == "numeric":
                df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')
            elif new_type == "datetime":
                df_cleaned[col] = pd.to_datetime(df_cleaned[col], errors='coerce')
            else:
                try:
                    df_cleaned[col] = df_cleaned[col].astype(new_type, errors='ignore')
                except Exception:
                    pass

        # 3. Remove Duplicates
        elif op == "remove_duplicates":
            df_cleaned.drop_duplicates(inplace=True)

        # 4. Normalize Text
        elif op == "normalize_text" and col in df_cleaned.columns:
            df_cleaned[col] = df_cleaned[col].astype(str).str.lower().str.strip()

        # 5. Map Values
        elif op == "map_values" and col in df_cleaned.columns:
            mapping = details.get("mapping", {})
            df_cleaned[col].replace(mapping, inplace=True)

        # 6. Handle Outliers
        elif op == "handle_outliers" and col in df_cleaned.columns:
            method = details.get("method", "IQR")
            if pd.api.types.is_numeric_dtype(df_cleaned[col]):
                if method == "IQR":
                    Q1 = df_cleaned[col].quantile(0.25)
                    Q3 = df_cleaned[col].quantile(0.75)
                    IQR = Q3 - Q1
                    lower = Q1 - 1.5 * IQR
                    upper = Q3 + 1.5 * IQR
                    df_cleaned[col] = df_cleaned[col].clip(lower, upper)

        # 7. Scale Numeric
        elif op == "scale_numeric" and col in df_cleaned.columns:
            method = details.get("method", "minmax")
            if pd.api.types.is_numeric_dtype(df_cleaned[col]):
                if method == "minmax":
                    col_min, col_max = df_cleaned[col].min(), df_cleaned[col].max()
                    if col_max > col_min:
                        df_cleaned[col] = (df_cleaned[col] - col_min) / (col_max - col_min)
                elif method == "zscore":
                    mean, std = df_cleaned[col].mean(), df_cleaned[col].std()
                    if std > 0:
                        df_cleaned[col] = (df_cleaned[col] - mean) / std

        # 8. Parse Dates
        elif op == "parse_dates" and col in df_cleaned.columns:
            df_cleaned[col] = pd.to_datetime(df_cleaned[col], errors="coerce")

    return df_cleaned


@st.cache_data
def _get_ai_cleaning_plan(_df):
    """Internal cached function to get the plan from the AI. No UI here."""
    prompt = generate_cleaning_prompt(_df)
    api_key = st.secrets["TOGETHER_API_KEY"]
    ai_plan_str = ask_llama(prompt, api_key, is_json=True)
    return ai_plan_str


def clean_dataframe_with_ai(df):
    """Orchestrates the AI-driven cleaning process with UI elements."""
    original_shape = df.shape

    st.info("🤖 Asking AI to generate a custom cleaning plan... (This happens only once per dataset)")

    ai_plan_str = _get_ai_cleaning_plan(df)

    if ai_plan_str.startswith("❌"):
        st.error("Failed to get a cleaning plan from the AI. Defaulting to basic cleaning.")
        df_cleaned = df.dropna(how='all').drop_duplicates()
        return df_cleaned, original_shape

    st.success("✅ AI has generated a cleaning plan!")

    try:
        plan_data = json.loads(ai_plan_str)
        steps = plan_data.get("cleaning_plan", [])
        if steps:
            st.markdown("### 🧾 Cleaning Plan Steps")
            for i, step in enumerate(steps, start=1):
                op = step.get("operation", "unknown").replace("_", " ").title()
                details = step.get("details", {})
                detail_str = ", ".join([f"**{k}**: {v}" for k, v in details.items()])
                st.markdown(f"- **Step {i}: {op}** → {detail_str}")
        else:
            st.info("⚠️ No cleaning steps returned from AI.")
    except Exception:
        st.json(ai_plan_str)  # fallback to raw JSON if parsing fails

    st.info("⚙️ Executing the AI-generated cleaning plan...")
    df_cleaned = execute_cleaning_plan(df, ai_plan_str)
    st.success("✅ Cleaning complete!")

    return df_cleaned, original_shape
