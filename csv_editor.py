import streamlit as st
import pandas as pd
from io import BytesIO


# CSV Builder Page (Editable Table)
def build_csv_page():
    st.title("Build or Edit Transactions .csv")

    # Step 1: Upload Existing CSV
    uploaded_file = st.file_uploader("Upload an existing CSV file", type=["csv"])

    if uploaded_file:
        # Load the uploaded CSV into a DataFrame
        df = pd.read_csv(uploaded_file, parse_dates=["date"])
        st.write("Uploaded Transactions:", df)

        # Validate required columns
        required_columns = {"ticker", "date", "price", "volume", "type"}
        if not required_columns.issubset(df.columns):
            st.error(f"The CSV must contain these columns: {required_columns}")
        else:
            # Step 2: Editable Table (Allow User to Edit the Data)
            st.write("Edit the table below to update your transactions CSV:")
            edited_df = st.data_editor(
                df,
                num_rows="dynamic",  # Allow users to add rows dynamically
            )

            # Step 3: Validate the edited table
            if not required_columns.issubset(edited_df.columns):
                st.error(f"The table must contain these columns: {required_columns}")
            else:
                st.success("The table is valid!")

                # Show the updated table
                st.write("Updated Transactions:", edited_df)

                # Step 4: Download the edited CSV
                def convert_df_to_csv(df):
                    output = BytesIO()
                    df.to_csv(output, index=False)
                    return output.getvalue()

                csv = convert_df_to_csv(edited_df)
                st.download_button(
                    label="Download Updated CSV",
                    data=csv,
                    file_name="updated_transactions.csv",
                    mime="text/csv",
                )
    else:
        # Provide the option to manually build the CSV if no file is uploaded
        st.write("Alternatively, you can build your CSV from scratch.")
        build_new_csv()


# Manual CSV Builder (for when no file is uploaded)
def build_new_csv():
    st.write("Create a new CSV from scratch by filling in the table below:")

    # Start with an empty or example DataFrame
    default_data = {
        "ticker": ["ASML.AS", "AAPL"],
        "date": ["2021-01-15", "2021-03-10"],
        "price": [10.5, 11.2],
        "volume": [10, 5],
        "type": ["Buy", "Sell"]
    }
    initial_df = pd.DataFrame(default_data)

    # Editable table
    edited_df = st.data_editor(
        initial_df,
        num_rows="dynamic",  # Allow users to add rows dynamically
    )

    # Validate and update
    required_columns = {"ticker", "date", "price", "volume", "type"}
    if not required_columns.issubset(edited_df.columns):
        st.error(f"The table must contain these columns: {required_columns}")
    else:
        st.success("The table is valid!")

        # Show the updated table
        st.write("Updated Transactions:", edited_df)

        # Download CSV button
        def convert_df_to_csv(df):
            output = BytesIO()
            df.to_csv(output, index=False)
            return output.getvalue()

        csv = convert_df_to_csv(edited_df)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name="transactions.csv",
            mime="text/csv",
        )
