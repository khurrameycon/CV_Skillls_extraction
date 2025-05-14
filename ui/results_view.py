# ui/results_view.py
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import json
from typing import List, Dict, Any

def display_overview(results: List[Dict[str, Any]]):
    """Display an overview of the evaluation results"""
    total_cvs = len(results)
    successful = sum(1 for r in results if "error" not in r)
    failed = total_cvs - successful
    
    st.subheader("Evaluation Summary")
    
    col1, col2, col3 = st.columns(3)
    col1.metric("Total CVs", total_cvs)
    col2.metric("Successfully Evaluated", successful)
    col3.metric("Failed Evaluations", failed)
    
    if successful > 0:
        avg_score = sum(r.get("score", 0) for r in results if "error" not in r) / successful
        st.metric("Average Score", f"{avg_score:.2f}/10")

def display_ranking_table(results: List[Dict[str, Any]]):
    """Display a table of the ranked CVs"""
    if not results:
        st.warning("No evaluation results to display.")
        return
    
    # Prepare data for the table
    table_data = []
    for r in results:
        if "error" in r:
            table_data.append({
                "Rank": r.get("rank", "-"),
                "Filename": r.get("filename", "Unknown"),
                "Overall Score": "-",
                "Skills": "-",
                "Experience": "-",
                "Education": "-",
                "Status": "Failed"
            })
        else:
            eval_data = r.get("evaluation", {})
            table_data.append({
                "Rank": r.get("rank", "-"),
                "Filename": r.get("filename", "Unknown"),
                "Overall Score": f"{r.get('score', 0):.2f}",
                "Skills": eval_data.get("skills", {}).get("score", "-"),
                "Experience": eval_data.get("experience", {}).get("score", "-"),
                "Education": eval_data.get("education", {}).get("score", "-"),
                "Status": "Success"
            })
    
    # Create a DataFrame and display as a table
    df = pd.DataFrame(table_data)
    st.dataframe(df, use_container_width=True)

def display_detailed_evaluation(results: List[Dict[str, Any]]):
    """Display detailed evaluation for each CV"""
    if not results:
        return
    
    st.subheader("Detailed Evaluations")
    
    # Create a selectbox to choose which CV to view in detail
    cv_options = [f"{r.get('rank', '-')}. {r.get('filename', 'Unknown')}" for r in results]
    selected_cv = st.selectbox("Select a CV to view detailed evaluation", cv_options)
    
    if selected_cv:
        # Extract the index from the selected option
        selected_index = cv_options.index(selected_cv)
        cv_result = results[selected_index]
        
        st.markdown(f"### {cv_result.get('filename', 'Unknown')}")
        
        if "error" in cv_result:
            st.error(f"Error evaluating this CV: {cv_result['error']}")
            return
        
        eval_data = cv_result.get("evaluation", {})
        
        # Display overall score
        st.metric("Overall Weighted Score", f"{cv_result.get('score', 0):.2f}/10")
        
        # Create tabs for different categories
        tabs = st.tabs(["Skills", "Experience", "Education", "Overall"])
        
        # Skills tab
        with tabs[0]:
            skills_data = eval_data.get("skills", {})
            st.metric("Skills Score", f"{skills_data.get('score', 0)}/10")
            st.markdown("#### Reasoning")
            st.write(skills_data.get("reasoning", "No reasoning provided"))
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Strengths")
                strengths = skills_data.get("strengths", [])
                if strengths:
                    for strength in strengths:
                        st.markdown(f"- {strength}")
                else:
                    st.write("No strengths identified")
            
            with col2:
                st.markdown("#### Gaps")
                gaps = skills_data.get("gaps", [])
                if gaps:
                    for gap in gaps:
                        st.markdown(f"- {gap}")
                else:
                    st.write("No gaps identified")
        
        # Experience tab
        with tabs[1]:
            experience_data = eval_data.get("experience", {})
            st.metric("Experience Score", f"{experience_data.get('score', 0)}/10")
            st.markdown("#### Reasoning")
            st.write(experience_data.get("reasoning", "No reasoning provided"))
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Strengths")
                strengths = experience_data.get("strengths", [])
                if strengths:
                    for strength in strengths:
                        st.markdown(f"- {strength}")
                else:
                    st.write("No strengths identified")
            
            with col2:
                st.markdown("#### Gaps")
                gaps = experience_data.get("gaps", [])
                if gaps:
                    for gap in gaps:
                        st.markdown(f"- {gap}")
                else:
                    st.write("No gaps identified")
        
        # Education tab
        with tabs[2]:
            education_data = eval_data.get("education", {})
            st.metric("Education Score", f"{education_data.get('score', 0)}/10")
            st.markdown("#### Reasoning")
            st.write(education_data.get("reasoning", "No reasoning provided"))
            
            col1, col2 = st.columns(2)
            with col1:
                st.markdown("#### Strengths")
                strengths = education_data.get("strengths", [])
                if strengths:
                    for strength in strengths:
                        st.markdown(f"- {strength}")
                else:
                    st.write("No strengths identified")
            
            with col2:
                st.markdown("#### Gaps")
                gaps = education_data.get("gaps", [])
                if gaps:
                    for gap in gaps:
                        st.markdown(f"- {gap}")
                else:
                    st.write("No gaps identified")
        
        # Overall tab
        with tabs[3]:
            overall_data = eval_data.get("overall", {})
            st.metric("Overall Assessment", f"{overall_data.get('score', 0)}/10")
            st.markdown("#### Reasoning")
            st.write(overall_data.get("reasoning", "No reasoning provided"))

def display_scoring_visualization(results: List[Dict[str, Any]]):
    """Display visualizations of the scores"""
    # Filter out results with errors
    valid_results = [r for r in results if "error" not in r]
    
    if not valid_results:
        return
    
    st.subheader("Score Visualization")
    
    # Prepare data for the chart
    chart_data = []
    for r in valid_results[:10]:  # Limit to top 10 for readability
        eval_data = r.get("evaluation", {})
        
        chart_data.append({
            "Filename": r.get("filename", "Unknown")[:20],  # Truncate long filenames
            "Skills": eval_data.get("skills", {}).get("score", 0),
            "Experience": eval_data.get("experience", {}).get("score", 0),
            "Education": eval_data.get("education", {}).get("score", 0),
            "Weighted Score": r.get("score", 0)
        })
    
    df = pd.DataFrame(chart_data)
    
    # Create a bar chart
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Plot bars for each category
    x = range(len(df))
    width = 0.2
    
    ax.bar([i - width*1.5 for i in x], df["Skills"], width=width, label="Skills")
    ax.bar([i - width*0.5 for i in x], df["Experience"], width=width, label="Experience")
    ax.bar([i + width*0.5 for i in x], df["Education"], width=width, label="Education")
    ax.bar([i + width*1.5 for i in x], df["Weighted Score"], width=width, label="Weighted Score")
    
    # Add labels and legend
    ax.set_ylabel("Score (0-10)")
    ax.set_title("CV Evaluation Scores by Category")
    ax.set_xticks(x)
    ax.set_xticklabels(df["Filename"], rotation=45, ha="right")
    ax.legend()
    
    plt.tight_layout()
    
    # Display the chart
    st.pyplot(fig)

def export_results(results: List[Dict[str, Any]]):
    """Create export options for the results"""
    st.subheader("Export Results")
    
    # Create a simplified version of the results for CSV export
    csv_data = []
    for r in results:
        if "error" in r:
            row = {
                "Rank": r.get("rank", "-"),
                "Filename": r.get("filename", "Unknown"),
                "Weighted Score": 0,
                "Skills Score": 0,
                "Experience Score": 0,
                "Education Score": 0,
                "Overall Score": 0,
                "Status": "Failed",
                "Error": r.get("error", "Unknown error")
            }
        else:
            eval_data = r.get("evaluation", {})
            row = {
                "Rank": r.get("rank", "-"),
                "Filename": r.get("filename", "Unknown"),
                "Weighted Score": r.get("score", 0),
                "Skills Score": eval_data.get("skills", {}).get("score", 0),
                "Experience Score": eval_data.get("experience", {}).get("score", 0),
                "Education Score": eval_data.get("education", {}).get("score", 0),
                "Overall Score": eval_data.get("overall", {}).get("score", 0),
                "Status": "Success",
                "Error": ""
            }
        csv_data.append(row)
    
    # Convert to DataFrame for CSV export
    csv_df = pd.DataFrame(csv_data)
    
    # Create a download button for CSV
    csv = csv_df.to_csv(index=False)
    st.download_button(
        label="Download as CSV",
        data=csv,
        file_name="cv_rankings.csv",
        mime="text/csv"
    )
    
    # Create a download button for JSON (full data)
    json_data = json.dumps([{
        "rank": r.get("rank", 0),
        "filename": r.get("filename", "Unknown"),
        "score": r.get("score", 0),
        "evaluation": r.get("evaluation", {}),
        "error": r.get("error", "") if "error" in r else ""
    } for r in results], indent=2)
    
    st.download_button(
        label="Download Full Results as JSON",
        data=json_data,
        file_name="cv_rankings_detailed.json",
        mime="application/json"
    )