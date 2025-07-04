import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import pandas as pd
from app.database import db
from app.models.purchase import PurchaseSchema

# Page configuration
st.set_page_config(
    page_title="Purchase Tracker Dashboard",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

def load_data():
    """Load purchase data from database."""
    try:
        purchases = db.fetchall(PurchaseSchema.SELECT_ALL)
        if not purchases:
            return pd.DataFrame()
        
        # Convert to DataFrame
        columns = ['id', 'sn', 'date', 'tracking_number', 'company_name', 
                  'item_name', 'quantity', 'item_price', 'item_price_sgd', 
                  'cny_to_sgd_rate', 'export_status', 'order_id', 'created_at']
        df = pd.DataFrame(purchases, columns=columns)
        
        # Convert date column to datetime
        df['date'] = pd.to_datetime(df['date'])
        
        # Ensure numeric columns are proper types
        df['quantity'] = pd.to_numeric(df['quantity'], errors='coerce').fillna(0)
        df['item_price'] = pd.to_numeric(df['item_price'], errors='coerce').fillna(0.0)
        df['item_price_sgd'] = pd.to_numeric(df['item_price_sgd'], errors='coerce').fillna(0.0)
        df['total_price_cny'] = df['quantity'] * df['item_price']
        df['total_price_sgd'] = df['quantity'] * df['item_price_sgd']
        
        return df
        
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return pd.DataFrame()

def create_summary_table(df, currency="SGD"):
    """Create summary statistics table."""
    try:
        amount_col = 'total_price_sgd' if currency == "SGD" else 'total_price_cny'
        currency_symbol = "S$" if currency == "SGD" else "¥"
        
        # Calculate summary statistics
        total_purchases = len(df)
        total_amount = pd.to_numeric(df[amount_col], errors='coerce').sum()
        avg_amount = pd.to_numeric(df[amount_col], errors='coerce').mean()
        total_items = pd.to_numeric(df['quantity'], errors='coerce').sum()
        
        # Date range
        date_range = f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}"
        
        # Top category (most expensive item)
        top_item_idx = pd.to_numeric(df[amount_col], errors='coerce').idxmax()
        top_item = df.loc[top_item_idx, 'item_name'][:30] + "..." if len(df.loc[top_item_idx, 'item_name']) > 30 else df.loc[top_item_idx, 'item_name']
        
        summary_data = {
            "Metric": [
                "📅 Date Range",
                "🛒 Total Purchases", 
                f"💰 Total Amount ({currency})",
                f"📊 Average Amount ({currency})",
                "📦 Total Items",
                "🏆 Most Expensive Item"
            ],
            "Value": [
                date_range,
                f"{total_purchases:,}",
                f"{currency_symbol}{total_amount:,.2f}",
                f"{currency_symbol}{avg_amount:,.2f}",
                f"{int(total_items):,}",
                top_item
            ]
        }
        
        return pd.DataFrame(summary_data)
    
    except Exception as e:
        st.error(f"Error creating summary table: {e}")
        return pd.DataFrame()

def dashboard_page():
    """Main dashboard page with charts and analytics."""
    st.header("📊 Analytics Dashboard")
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.warning("No purchase data found. Please import CSV data first.")
        st.markdown("To import data, use: `python main.py import data/taobao-en-all.csv`")
        return
    
    # Currency selection
    currency = st.selectbox("💱 Display Currency", ["SGD", "CNY"], index=0)
    
    # Summary table
    st.subheader("📈 Summary Statistics")
    summary_df = create_summary_table(df, currency)
    if not summary_df.empty:
        st.table(summary_df)
    
    st.markdown("---")
    
    # Sidebar filters for dashboard
    st.sidebar.header("📊 Dashboard Filters")
    
    # Date range filter
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="dashboard_date"
    )
    
    # Search filter
    search_term = st.sidebar.text_input("Search Items", "", key="dashboard_search")
    
    # Filter data
    filtered_df = df.copy()
    
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['date'].dt.date >= date_range[0]) & 
            (filtered_df['date'].dt.date <= date_range[1])
        ]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['item_name'].str.contains(search_term, case=False, na=False)
        ]
    
    # Main dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Total Purchases",
            len(filtered_df),
            delta=len(filtered_df) - len(df) if len(filtered_df) != len(df) else None
        )
    
    with col2:
        if currency == "SGD":
            total_amount = pd.to_numeric(filtered_df['total_price_sgd'], errors='coerce').sum()
            currency_symbol = "S$"
            delta_amount = total_amount - pd.to_numeric(df['total_price_sgd'], errors='coerce').sum()
        else:
            total_amount = pd.to_numeric(filtered_df['total_price_cny'], errors='coerce').sum()
            currency_symbol = "¥"
            delta_amount = total_amount - pd.to_numeric(df['total_price_cny'], errors='coerce').sum()
        
        st.metric(
            f"Total Amount ({currency})",
            f"{currency_symbol}{total_amount:.2f}",
            delta=f"{currency_symbol}{delta_amount:.2f}" if len(filtered_df) != len(df) else None
        )
    
    with col3:
        if currency == "SGD":
            avg_price = pd.to_numeric(filtered_df['item_price_sgd'], errors='coerce').mean()
            currency_symbol = "S$"
        else:
            avg_price = pd.to_numeric(filtered_df['item_price'], errors='coerce').mean()
            currency_symbol = "¥"
            
        st.metric(
            f"Average Price ({currency})",
            f"{currency_symbol}{avg_price:.2f}" if not pd.isna(avg_price) else f"{currency_symbol}0.00"
        )
    
    with col4:
        total_items = pd.to_numeric(filtered_df['quantity'], errors='coerce').sum()
        st.metric(
            "Total Items",
            int(total_items) if not pd.isna(total_items) else 0
        )
    
    st.markdown("---")
    
    # Charts
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📈 Purchases Over Time")
        if not filtered_df.empty:
            amount_col = 'total_price_sgd' if currency == "SGD" else 'total_price_cny'
            currency_symbol = "S$" if currency == "SGD" else "¥"
            
            daily_purchases = filtered_df.groupby(filtered_df['date'].dt.date).agg({
                amount_col: 'sum',
                'id': 'count'
            }).reset_index()
            daily_purchases.columns = ['date', 'total_amount', 'count']
            
            fig = px.line(
                daily_purchases, 
                x='date', 
                y='total_amount',
                title=f"Daily Purchase Amount ({currency})"
            )
            fig.update_layout(yaxis_title=f"Amount ({currency_symbol})")
            st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        st.subheader("🏷️ Top Items by Value")
        if not filtered_df.empty:
            try:
                amount_col = 'total_price_sgd' if currency == "SGD" else 'total_price_cny'
                currency_symbol = "S$" if currency == "SGD" else "¥"
                
                # Ensure total_price is numeric and sort properly
                filtered_df[amount_col] = pd.to_numeric(filtered_df[amount_col], errors='coerce').fillna(0)
                top_items = filtered_df.nlargest(10, amount_col)[['item_name', amount_col]]
                
                if not top_items.empty:
                    fig = px.bar(
                        top_items,
                        x=amount_col,
                        y='item_name',
                        orientation='h',
                        title=f"Top 10 Items by Value ({currency})"
                    )
                    fig.update_layout(
                        yaxis={'categoryorder': 'total ascending'},
                        xaxis_title=f"Total Value ({currency_symbol})"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("No data available for top items chart")
            except Exception as e:
                st.error(f"Error creating top items chart: {e}")
                st.write("Debug info:")
                st.write(f"Amount column dtype: {filtered_df[amount_col].dtype}")
                st.write(f"Sample values: {filtered_df[amount_col].head()}")
    
    # Recent purchases table
    st.subheader("📋 Recent Purchases")
    
    if currency == "SGD":
        display_df = filtered_df[['date', 'item_name', 'quantity', 'item_price_sgd', 'total_price_sgd']].copy()
        display_df.columns = ['Date', 'Item Name', 'Quantity', 'Unit Price (SGD)', 'Total Price (SGD)']
    else:
        display_df = filtered_df[['date', 'item_name', 'quantity', 'item_price', 'total_price_cny']].copy()
        display_df.columns = ['Date', 'Item Name', 'Quantity', 'Unit Price (CNY)', 'Total Price (CNY)']
    
    display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
    display_df = display_df.sort_values('Date', ascending=False)
    
    st.dataframe(
        display_df.head(20),
        use_container_width=True,
        hide_index=True
    )
    
def tabular_view_page():
    """Tabular view page with detailed data table."""
    st.header("📋 Tabular View")
    
    # Load data
    df = load_data()
    
    if df.empty:
        st.warning("No purchase data found. Please import CSV data first.")
        st.markdown("To import data, use: `python main.py import data/taobao-en-all.csv`")
        return
    
    # Currency selection
    currency = st.selectbox("💱 Display Currency", ["SGD", "CNY"], index=0, key="table_currency")
    
    # Sidebar filters for tabular view
    st.sidebar.header("📋 Table Filters")
    
    # Date range filter
    min_date = df['date'].min().date()
    max_date = df['date'].max().date()
    
    date_range = st.sidebar.date_input(
        "Select Date Range",
        value=(min_date, max_date),
        min_value=min_date,
        max_value=max_date,
        key="table_date"
    )
    
    # Search filter
    search_term = st.sidebar.text_input("Search Items", "", key="table_search")
    
    # Additional filters
    st.sidebar.markdown("### Additional Filters")
    
    # Price range filter
    if currency == "SGD":
        price_col = 'item_price_sgd'
        min_price = float(df[price_col].min())
        max_price = float(df[price_col].max())
        currency_symbol = "S$"
    else:
        price_col = 'item_price'
        min_price = float(df[price_col].min())
        max_price = float(df[price_col].max())
        currency_symbol = "¥"
    
    if max_price > min_price:
        price_range = st.sidebar.slider(
            f"Price Range ({currency})",
            min_value=min_price,
            max_value=max_price,
            value=(min_price, max_price),
            format=f"{currency_symbol}%.2f"
        )
    else:
        # If all prices are the same, show a disabled input
        st.sidebar.text_input(
            f"Price (all items: {currency_symbol}{min_price:.2f})",
            value=f"{currency_symbol}{min_price:.2f}",
            disabled=True
        )
        price_range = (min_price, max_price)
    
    # Quantity filter
    min_qty = int(df['quantity'].min())
    max_qty = int(df['quantity'].max())
    
    if max_qty > min_qty:
        qty_filter = st.sidebar.slider(
            "Minimum Quantity",
            min_value=min_qty,
            max_value=max_qty,
            value=min_qty
        )
    else:
        # If all quantities are the same, show a simple number input
        qty_filter = st.sidebar.number_input(
            f"Quantity (all items have qty: {max_qty})",
            min_value=min_qty,
            max_value=max_qty,
            value=min_qty,
            disabled=True
        )
    
    # Filter data
    filtered_df = df.copy()
    
    if len(date_range) == 2:
        filtered_df = filtered_df[
            (filtered_df['date'].dt.date >= date_range[0]) & 
            (filtered_df['date'].dt.date <= date_range[1])
        ]
    
    if search_term:
        filtered_df = filtered_df[
            filtered_df['item_name'].str.contains(search_term, case=False, na=False)
        ]
    
    # Price filter
    filtered_df = filtered_df[
        (pd.to_numeric(filtered_df[price_col], errors='coerce') >= price_range[0]) &
        (pd.to_numeric(filtered_df[price_col], errors='coerce') <= price_range[1])
    ]
    
    # Quantity filter
    filtered_df = filtered_df[
        pd.to_numeric(filtered_df['quantity'], errors='coerce') >= qty_filter
    ]
    
    # Summary info
    st.info(f"📊 Showing {len(filtered_df):,} purchases out of {len(df):,} total")
    
    # Prepare display dataframe
    if currency == "SGD":
        display_df = filtered_df[['date', 'item_name', 'quantity', 'item_price_sgd', 'total_price_sgd', 'order_id']].copy()
        display_df.columns = ['Date', 'Item Name', 'Qty', 'Unit Price (SGD)', 'Total (SGD)', 'Order ID']
    else:
        display_df = filtered_df[['date', 'item_name', 'quantity', 'item_price', 'total_price_cny', 'order_id']].copy()
        display_df.columns = ['Date', 'Item Name', 'Qty', 'Unit Price (CNY)', 'Total (CNY)', 'Order ID']
    
    display_df['Date'] = display_df['Date'].dt.strftime('%Y-%m-%d')
    display_df = display_df.sort_values('Date', ascending=False)
    
    # Display options
    col1, col2, col3 = st.columns([2, 1, 1])
    
    with col1:
        items_per_page = st.selectbox("Items per page", [20, 50, 100, 200], index=0)
    
    with col2:
        show_summary = st.checkbox("Show Summary Stats", value=True)
    
    with col3:
        if st.button("📥 Download CSV"):
            csv = display_df.to_csv(index=False)
            st.download_button(
                label="Download Filtered Data",
                data=csv,
                file_name=f"purchases_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                mime="text/csv"
            )
    
    # Summary statistics
    if show_summary:
        st.subheader("📈 Filtered Data Summary")
        summary_df = create_summary_table(filtered_df, currency)
        if not summary_df.empty:
            st.table(summary_df)
        st.markdown("---")
    
    # Data table
    st.subheader("📋 Purchase Details")
    
    # Pagination
    total_items = len(display_df)
    num_pages = (total_items - 1) // items_per_page + 1 if total_items > 0 else 1
    
    if num_pages > 1:
        page = st.number_input("Page", min_value=1, max_value=num_pages, value=1) - 1
        start_idx = page * items_per_page
        end_idx = start_idx + items_per_page
        paginated_df = display_df.iloc[start_idx:end_idx]
        st.info(f"Page {page + 1} of {num_pages} (showing items {start_idx + 1}-{min(end_idx, total_items)} of {total_items})")
    else:
        paginated_df = display_df.head(items_per_page)
    
    # Display table
    st.dataframe(
        paginated_df,
        use_container_width=True,
        hide_index=True
    )

def main():
    st.title("📊 Purchase Tracker")
    
    # Sidebar navigation
    st.sidebar.title("🧭 Navigation")
    page = st.sidebar.radio(
        "Select Page",
        ["📊 Dashboard", "📋 Tabular View"],
        index=0
    )
    
    # Route to appropriate page
    if page == "📊 Dashboard":
        dashboard_page()
    elif page == "📋 Tabular View":
        tabular_view_page()
    
    # Common sidebar elements
    st.sidebar.markdown("---")
    st.sidebar.markdown("### 📊 App Info")
    st.sidebar.info("Purchase Tracker v1.0\nBuilt with Streamlit, DuckDB & Polars")

if __name__ == "__main__":
    main()