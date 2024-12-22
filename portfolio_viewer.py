import streamlit as st
import pandas as pd
import yfinance as yf
import matplotlib.pyplot as plt

# TODO: Stock splits handled properly?


# CSV Builder Page
def portfolio_viewer():
    # Header for the date selection, styled to stand out
    st.markdown("""
        <h1 style="text-align: center; color: #4CAF50;">Upload transactions .csv</h1>
    """, unsafe_allow_html=True)

    # Upload transactions CSV file
    uploaded_file = st.file_uploader("Upload your transactions CSV file", type=["csv"])

    if uploaded_file:
        # Read CSV file
        df = pd.read_csv(uploaded_file, parse_dates=["date"])
        st.write("Uploaded Transactions:", df)

        # Validate required columns
        required_columns = {"ticker", "date", "price", "volume", "type"}
        if not required_columns.issubset(df.columns):
            st.error(f"CSV file must contain the following columns: {required_columns}")
        else:
            # Fetch historical stock prices for all tickers
            unique_tickers = df["ticker"].unique()

            # Header for the date selection, styled to stand out
            st.markdown("""
                <h1 style="text-align: center; color: #4CAF50;">(Optional) Select a Start Date</h1>
            """, unsafe_allow_html=True)

            # Highlight the date input with a larger font or background color (using Markdown or HTML)
            start_date = st.date_input(
                "Choose the start date for your portfolio analysis:",
                value=df["date"].min(),
                help="Select a date from which you want to view the yield of your portfolio, by default this is the date of the first recorded transaction."
            )

            stock_data = {}
            for ticker in unique_tickers:
                # st.write(f"Fetching data for {ticker}...")
                data = yf.download(ticker, start=start_date, progress=False)
                stock_data[ticker] = data["Close"][ticker]

            # Merge stock prices into a single DataFrame
            all_prices = pd.DataFrame(stock_data)
            all_prices = all_prices.fillna(method="ffill")  # Forward fill missing data

            # Fetch historical data for the indices
            # st.write("Fetching S&P 500, Nasdaq, MSCI and AEX data...")
            sp500 = yf.download("^GSPC", start=all_prices.index.min(), end=all_prices.index.max(), progress=False)
            nasdaq = yf.download("^IXIC", start=all_prices.index.min(), end=all_prices.index.max(), progress=False)
            msci = yf.download("XWD.TO", start=all_prices.index.min(), end=all_prices.index.max(), progress=False)
            aex = yf.download("^AEX", start=all_prices.index.min(), end=all_prices.index.max(), progress=False)

            # Normalize indices to start at 100
            sp500_normalized = sp500["Close"] / sp500["Close"].iloc[0] * 100
            nasdaq_normalized = nasdaq["Close"] / nasdaq["Close"].iloc[0] * 100
            msci_normalized = msci["Close"] / msci["Close"].iloc[0] * 100
            aex_normalized = aex["Close"] / aex["Close"].iloc[0] * 100

            # st.write("Historical Prices:", all_prices)

            # Calculate daily portfolio value
            portfolio_value = pd.DataFrame(index=all_prices.index)
            portfolio_value["Value"] = 0

            # Iterate over transactions
            for _, row in df.iterrows():
                ticker = row["ticker"]
                transaction_date = row["date"]  # Assuming your dataframe has a 'date' column
                volume = row["volume"]
                transaction_type = row["type"]  # Assuming your dataframe has a 'type' column: "Buy" or "Sell"

                # Add or subtract stock value based on transaction type
                if transaction_type == "Buy":
                    portfolio_value.loc[transaction_date:, "Value"] += volume * all_prices[ticker]
                elif transaction_type == "Sell":
                    portfolio_value.loc[transaction_date:, "Value"] -= volume * all_prices[ticker]

            # Header for the date selection, styled to stand out
            st.markdown("""
                <h1 style="text-align: center; color: #4CAF50;">Beautiful little plots</h1>
            """, unsafe_allow_html=True)

            # Plot portfolio value over time
            st.write("Portfolio Value Over Time:")
            plt.figure(figsize=(10, 6))
            plt.plot(portfolio_value.index, portfolio_value["Value"], label="Portfolio Value", color="blue")
            plt.title("Portfolio Value Over Time")
            plt.xlabel("Date")
            plt.ylabel("Total Value")
            plt.grid()
            plt.legend()
            st.pyplot(plt)

            # Track total invested capital and portfolio value over time, including dividends
            total_invested_capital = 0
            portfolio_value = pd.Series(0, index=all_prices.index)

            for _, row in df.iterrows():
                ticker = row["ticker"]
                mutation_date = row["date"]
                mutation_price = row["price"]
                mutation_type = row["type"]
                volume = row["volume"]

                # TODO: Add support for rebalancing on sale
                if mutation_type == "Sell":
                    continue

                # Calculate the value of the mutation
                mutation_value = mutation_price * volume
                # if mutation_value == "Buy":
                total_invested_capital += mutation_value
                # else:
                #     pass
                    # total_invested_capital -= mutation_value

                # Fetch stock data including dividends
                stock_data = yf.Ticker(ticker).history(start=all_prices.index.min(), end=all_prices.index.max(),
                                                       actions=True)
                dividends = stock_data["Dividends"]

                # Calculate stock's growth over time relative to its purchase price
                stock_change = all_prices[ticker] / mutation_price
                stock_change.loc[:mutation_date] = 1  # Ignore values before purchase date

                # Add stock's contribution to portfolio value dynamically
                # if mutation_type == "Buy":
                portfolio_value += stock_change * (volume * mutation_price)
                # else:
                #     pass
                    # portfolio_value -= stock_change * (volume * mutation_price)

                # Add cumulative dividends to portfolio value
                dividend_cumulative = dividends.cumsum() * volume

                # Ensure both indices are timezone-naive
                portfolio_value.index = portfolio_value.index.tz_localize(None)
                dividend_cumulative.index = dividend_cumulative.index.tz_localize(None)

                # Align dividend index with portfolio_value index
                dividend_cumulative = dividend_cumulative.reindex(portfolio_value.index, method='pad', fill_value=0)

                # Add aligned dividends to portfolio value
                portfolio_value += dividend_cumulative

            # Calculate portfolio yield as the ratio of portfolio value to total invested capital
            portfolio_yield = (portfolio_value / total_invested_capital) * 100

            # Normalize yield to start at 100
            normalized_yield = portfolio_yield / portfolio_yield.iloc[0] * 100

            # Plot corrected yield
            plt.figure(figsize=(10, 6))
            plt.plot(normalized_yield.index, normalized_yield, label="Portfolio Yield", color="purple")
            plt.plot(sp500_normalized.index, sp500_normalized, label="S&P 500", color="blue")
            plt.plot(nasdaq_normalized.index, nasdaq_normalized, label="Nasdaq", color="green")
            plt.plot(msci_normalized.index, msci_normalized, label="MSCI", color="red")
            plt.plot(aex_normalized.index, aex_normalized, label="AEX", color="grey")
            plt.title("Portfolio Yield Over Time")
            plt.xlabel("Date")
            plt.ylabel("Normalized Yield")
            plt.grid()
            plt.legend()
            st.pyplot(plt)
