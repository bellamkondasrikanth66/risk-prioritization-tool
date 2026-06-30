import streamlit as st
import pandas as pd

# Set up page configuration
st.set_page_config(
    page_title="Risk-Based Test Prioritization Tool",
    page_icon="🎯",
    layout="wide"
)

# Initialize session state to store test cases if not already present
if 'test_cases' not in st.session_state:
    st.session_state.test_cases = [
        {"ID": "TC001", "Name": "User Authentication / Login", "Likelihood": 3, "Impact": 5, "Detection": 2},
        {"ID": "TC002", "Name": "Checkout Payment Gateway", "Likelihood": 4, "Impact": 5, "Detection": 3},
        {"ID": "TC003", "Name": "Profile Picture Upload", "Likelihood": 2, "Impact": 2, "Detection": 1},
        {"ID": "TC004", "Name": "Dark Mode Toggle", "Likelihood": 1, "Impact": 1, "Detection": 1},
    ]

# Title and Description
st.title("🎯 Risk-Based Test Case Prioritization Tool")
st.markdown("""
This prototype helps QA teams prioritize test execution suites based on an **FMEA (Failure Mode and Effects Analysis)** methodology.
Input your test cases, assign risk metrics (1-5), and the tool will dynamically calculate the **Risk Priority Number (RPN)** to rank your testing order.
""")

st.divider()

# Layout split: Left for Input, Right for Output Matrix
col1, col2 = st.columns([1, 2])

with col1:
    st.header("📝 Add New Test Case")
    with st.form(key='test_case_form', clear_on_submit=True):
        tc_id = st.text_input("Test Case ID", placeholder="e.g., TC005")
        tc_name = st.text_input("Test Case Name/Component", placeholder="e.g., Report Generation API")
        
        st.markdown("**Risk Parameter Scoring (1 = Low Risk, 5 = High Risk)**")
        likelihood = st.slider("Likelihood of Failure (L)", 1, 5, 3, help="Probability of defect occurrence.")
        impact = st.slider("Business Impact (I)", 1, 5, 3, help="Severity of impact on business/users if it fails.")
        detection = st.slider("Detection Difficulty (D)", 1, 5, 3, help="How hard it is to catch this defect easily.")
        
        submit_button = st.form_submit_button(label="Add to Suite")
        
        if submit_button:
            if tc_id and tc_name:
                # Append new test case data to session state
                st.session_state.test_cases.append({
                    "ID": tc_id,
                    "Name": tc_name,
                    "Likelihood": likelihood,
                    "Impact": impact,
                    "Detection": detection
                })
                st.success(f"Added {tc_id} successfully!")
            else:
                st.error("Please fill out both Test Case ID and Name.")

with col2:
    st.header("📊 Prioritized Test Execution Matrix")
    
    if st.session_state.test_cases:
        # Convert list of dicts to DataFrame
        df = pd.DataFrame(st.session_state.test_cases)
        
        # Algorithm implementation: Calculate composite RPN score
        df['RPN'] = df['Likelihood'] * df['Impact'] * df['Detection']
        
        # Sort by RPN descending, breaking ties with Business Impact descending
        df_sorted = df.sort_values(by=['RPN', 'Impact'], ascending=[False, False]).reset_index(drop=True)
        
        # Add an explicit Execution Order index column starting at 1
        df_sorted.index = df_sorted.index + 1
        df_sorted.index.name = "Execution Order"
        
        # Function to color code high-risk items dynamically
        def highlight_high_rpn(val):
            if val >= 45:
                return 'background-color: #ffcccc; color: #800000; font-weight: bold;'
            elif val >= 15:
                return 'background-color: #ffe6cc; color: #b35900;'
            else:
                return 'background-color: #e6ffcc; color: #2b5900;'

        # Render dataframe with styled visual indicators
        st.dataframe(
            df_sorted.style.applymap(highlight_high_rpn, subset=['RPN']),
            use_container_width=True
        )
        
        # Metrics Summary Cards
        st.markdown("### 📈 Test Strategy Summary")
        m_col1, m_col2, m_col3 = st.columns(3)
        m_col1.metric("Total Test Cases", len(df_sorted))
        m_col2.metric("Highest Risk RPN Score", int(df_sorted['RPN'].max()))
        m_col3.metric("Critical Suite Size (RPN ≥ 45)", len(df_sorted[df_sorted['RPN'] >= 45]))
        
        # Clear Data Option
        if st.button("Reset Matrix"):
            st.session_state.test_cases = []
            st.experimental_rerun()
    else:
        st.info("No test cases added yet. Use the left panel to populate the matrix.")