from csv_editor import build_csv_page
import streamlit as st

from portfolio_viewer import portfolio_viewer


# Main App
def main():
    # Sidebar Navigation
    st.sidebar.title("Navigation")
    page = st.sidebar.radio("Go to", ["Step 1: Build Transaction CSV", "Step 2: View Portfolio Yield"])

    if page == "Step 1: Build Transaction CSV":
        build_csv_page()
    elif page == "Step 2: View Portfolio Yield":
        portfolio_viewer()


if __name__ == "__main__":
    main()
