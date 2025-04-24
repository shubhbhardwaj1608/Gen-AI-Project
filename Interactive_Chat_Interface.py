import streamlit as st
import pandas as pd
from Api_Sql_Gemini import get_table_info, generate_sql_query, run_query
import base64
import plotly.express as px
import time

# --- Page Config ---
st.set_page_config(page_title="Chat Interface_Streamlit | SB", layout="wide")

# --- Apply Background Images ---
def add_bg_from_local(main_bg, sidebar_bg):
    main_bg_ext = "jpg"
    sidebar_bg_ext = "jpg"

    with open(main_bg, "rb") as image_file:
        main_bg_base64 = base64.b64encode(image_file.read()).decode()
    with open(sidebar_bg, "rb") as image_file:
        sidebar_bg_base64 = base64.b64encode(image_file.read()).decode()

    st.markdown(f"""
        <style>
        .stApp {{
            background-image: url("data:image/{main_bg_ext};base64,{main_bg_base64}");
            background-size: cover;
        }}
        section[data-testid="stSidebar"] > div:first-child {{
            background-image: url("data:image/{sidebar_bg_ext};base64,{sidebar_bg_base64}");
            background-size: cover;
        }}
        </style>
        """, unsafe_allow_html=True)

add_bg_from_local("bg_main.jpg", "bg_sidebar.jpg")

# --- Initialize History State ---
if "history" not in st.session_state:
    st.session_state.history = []
if "sql_query" not in st.session_state:
    st.session_state.sql_query = ""
if "query_result" not in st.session_state:
    st.session_state.query_result = None
if "clear_input" not in st.session_state:
    st.session_state.clear_input = False

# --- Sidebar ---
with st.sidebar:
    st.markdown("## ⚙ App Settings")

    st.markdown("### 🧠 Query History")
    if st.session_state.history:
        for i, (q, s) in enumerate(reversed(st.session_state.history), 1):
            with st.expander(f"🕘 Query {i}"):
                st.markdown(f"Q: {q}")
                st.code(s, language="sql")
    else:
        st.info("No queries yet!")

    st.markdown("---")
    if st.checkbox("🔐 Show Gemini API Key"):
        st.code("SHUBH_Api key", language="text")
    else:
        st.text("🔐 Gemini API Key: Hidden")

    st.markdown("---")
    selected_member = st.selectbox(
        "👥 Team Members",
        ["Mandakini Srivastava", "Navansh Mishra", "Shubh Bhardwaj"]
    )

# --- Main Content ---
st.title("💬 Interactive Chat Interface")
st.caption("Powered by Gemini AI | SSMS | SB")

st.header("Ask Anything about Transaction Data")
user_input = st.text_input(
    "🔍 What would you like to know?",
    key="user_question",
    value="" if st.session_state.clear_input else st.session_state.get("user_question", "")
)

if st.session_state.clear_input:
    st.session_state.clear_input = False

# --- Buttons ---
col1, col2 = st.columns([1, 1])
with col1:
    run_clicked = st.button("▶ Run Query")
with col2:
    clear_clicked = st.button("🧹 Clear Chat")

# --- Feedback Slider ---
st.markdown("### ⭐ Rate Your Experience")
rating = st.select_slider('Rate us:', ['', 'Bad', 'Good', 'Excellent'], label_visibility="visible")

if rating and rating != '':
    st.success("✅ Thanks for your valuable feedback!!")

# --- Run Query Logic ---
if run_clicked and user_input.strip():
    with st.spinner("⏳ Please wait AI is thinking..."):
        df_sample = get_table_info()
        sql = generate_sql_query(user_input, df_sample)
        st.session_state.sql_query = sql
        st.session_state.query_result = run_query(sql)
        st.session_state.history.append((user_input, sql))  # Save to history
    st.success("✅ Query executed successfully!")

# --- Clear Chat Logic ---
if clear_clicked:
    st.session_state.sql_query = ""
    st.session_state.query_result = None
    st.session_state.history = []
    st.session_state.clear_input = True
    st.warning("⚠ Chat cleared!")

# --- Progress Bar ---
if run_clicked:
    progress = st.progress(0)
    for percent in range(1, 101):
        time.sleep(0.005)
        progress.progress(percent)

# --- Show Output ---
if st.session_state.sql_query:
    st.subheader("🧠 Gemini Generated SQL")
    st.code(st.session_state.sql_query, language="sql")

if isinstance(st.session_state.query_result, pd.DataFrame):
    st.subheader("📊 Query Result")
    df = st.session_state.query_result
    st.dataframe(df)

    # --- Visualization Section ---
    st.markdown("### 📈 Visualize Your Data")

    if not df.empty:
        chart_type = st.selectbox("📊 Select Chart Type", ["None", "Line Chart", "Bar Chart", "Pie Chart", "Box Plot"])

        numeric_cols = df.select_dtypes(include='number').columns.tolist()
        all_cols = df.columns.tolist()

        if chart_type == "Line Chart":
            x_axis = st.selectbox("Select X-axis", all_cols, key="line_x")
            y_axis = st.multiselect("Select Y-axis (numeric)", numeric_cols, key="line_y")
            if x_axis and y_axis:
                st.line_chart(df.set_index(x_axis)[y_axis])

        elif chart_type == "Bar Chart":
            x_axis = st.selectbox("Select X-axis", all_cols, key="bar_x")
            y_axis = st.selectbox("Select Y-axis (numeric)", numeric_cols, key="bar_y")
            if x_axis and y_axis:
                st.bar_chart(df[[x_axis, y_axis]].set_index(x_axis))

        elif chart_type == "Pie Chart":
            label_col = st.selectbox("Select Category Column", all_cols, key="pie_label")
            value_col = st.selectbox("Select Values Column (numeric)", numeric_cols, key="pie_value")
            if label_col and value_col:
                fig = px.pie(df, names=label_col, values=value_col, title=f"Pie Chart of {value_col} by {label_col}")
                st.plotly_chart(fig)

        elif chart_type == "Box Plot":
            y_col = st.selectbox("Select Column for Box Plot", numeric_cols, key="box_y")
            category_col = st.selectbox("Select Category Column", all_cols, key="box_cat")
            if y_col and category_col:
                fig = px.box(df, x=category_col, y=y_col, title=f"Box Plot of {y_col} by {category_col}")
                st.plotly_chart(fig)

elif isinstance(st.session_state.query_result, str):
    st.error(st.session_state.query_result)

# --- Footer ---
st.markdown("---")
st.caption("© 2025 | Created by Team | Streamlit + Gemini + SSMS_SQL Server")