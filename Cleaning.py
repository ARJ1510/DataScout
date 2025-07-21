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
    You are an expert data scientist. Your task is to create a data cleaning plan for the following dataset.
    Analyze the sample data and column information provided.
    Identify potential issues and suggest cleaning operations.

    **Column Information:**
    {column_info}

    **Data Sample (first 15 rows):**
    ```csv
    {sample_data}
    ```

    **Instructions:**
    Based on your analysis, provide a step-by-step cleaning plan in JSON format.
    The JSON should be a list of "steps", where each step is an object with a "operation" and "details".
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
        elif op == "change_type" and col in df_cleaned.columns:
            new_type = details.get("new_type")
            if new_type == "numeric":
                df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')
            else:
                df_cleaned[col] = df_cleaned[col].astype(new_type, errors='ignore')
        elif op == "remove_duplicates":
            df_cleaned.drop_duplicates(inplace=True)
        elif op == "normalize_text" and col in df_cleaned.columns:
            df_cleaned[col] = df_cleaned[col].str.lower().str.strip()
        elif op == "map_values" and col in df_cleaned.columns:
            mapping = details.get("mapping", {})
            df_cleaned[col].replace(mapping, inplace=True)
    return df_cleaned


@st.cache_data
def _get_ai_cleaning_plan(_df):
    """Internal cached function to get the plan from the AI. No UI here."""
    prompt = generate_cleaning_prompt(_df)
    # Pass the key from secrets
    api_key = st.secrets["TOGETHER_API_KEY"]
    ai_plan_str = ask_llama(prompt, api_key, is_json=True)
    return ai_plan_str


def clean_dataframe_with_ai(df):
    """Orchestrates the AI-driven cleaning process with UI elements."""
    original_shape = df.shape

    st.info("🤖 Asking AI to generate a custom cleaning plan... (This happens only once per dataset)")

    # Call the cached function to get the plan
    ai_plan_str = _get_ai_cleaning_plan(df)

    if ai_plan_str.startswith("❌"):
        st.error("Failed to get a cleaning plan from the AI. Defaulting to basic cleaning.")
        df_cleaned = df.dropna(how='all').drop_duplicates()
        return df_cleaned, original_shape

    st.success("✅ AI has generated a cleaning plan!")
    st.json(ai_plan_str)

    st.info("⚙️ Executing the AI-generated cleaning plan...")
    df_cleaned = execute_cleaning_plan(df, ai_plan_str)
    st.success("✅ Cleaning complete!")

    return df_cleaned, original_shape