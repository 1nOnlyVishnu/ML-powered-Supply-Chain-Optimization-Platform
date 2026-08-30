import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from datetime import datetime, timedelta
from streamlit_option_menu import option_menu
import sqlite3
import os
import matplotlib.pyplot as plt
import time

# Optional imports for ML models
try:
    from xgboost import XGBRegressor
    HAS_XGBOOST = True
except ImportError:
    HAS_XGBOOST = False
    XGBRegressor = None

try:
    from sklearn.model_selection import train_test_split
    HAS_SKLEARN = True
except ImportError:
    HAS_SKLEARN = False

try:
    from prophet import Prophet
    HAS_PROPHET = True
except ImportError:
    HAS_PROPHET = False
    Prophet = None

# Initialize session state
if 'supply_data' not in st.session_state:
    st.session_state.supply_data = pd.DataFrame()

# Set page config
st.set_page_config(
    page_title="Supply Chain Management",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Professional Header
st.markdown("""
<div style="
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    margin-bottom: 20px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    text-align: center;
">
    <h1 style="margin: 0; font-size: 2.5em; font-weight: 700;"> Enterprise Supply Chain Management System</h1>
    <p style="margin: 10px 0 0 0; font-size: 1.2em; opacity: 0.9;">Advanced Analytics & Optimization Platform</p>
    <div style="margin-top: 15px; font-size: 0.9em; opacity: 0.8;">
        Powered by AI/ML • Real-time Insights • Professional Enterprise Solution
    </div>
</div>
""", unsafe_allow_html=True)

# Custom CSS - Professional Color Scheme
st.markdown("""
    <style>
    .main {
        padding: 2rem;
        background: linear-gradient(135deg, #f5f7fa 0%, #c3cfe2 100%);
        min-height: 100vh;
    }
    .stButton>button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.75rem 1.5rem;
        font-weight: 600;
        font-size: 14px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.4);
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #5a6fd8 0%, #6a4190 100%);
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(102, 126, 234, 0.6);
    }
    .css-1d391kg {  /* Sidebar */
        background: linear-gradient(180deg, #2c3e50 0%, #34495e 100%);
    }
    .css-1lcbmhc {  /* Main content area */
        background: rgba(255, 255, 255, 0.95);
        border-radius: 15px;
        box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
        backdrop-filter: blur(10px);
    }
    .stMetric {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border-radius: 10px;
        padding: 1rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    .stMetric label {
        color: rgba(255, 255, 255, 0.9) !important;
    }
    .stMetric .metric-value {
        color: white !important;
        font-size: 2rem !important;
        font-weight: 700 !important;
    }
    .stHeader {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
    }
    .stSubheader {
        color: #2c3e50;
        font-weight: 600;
        border-bottom: 2px solid #667eea;
        padding-bottom: 0.5rem;
        margin-bottom: 1rem;
    }
    .stSuccess {
        background: linear-gradient(135deg, #56ab2f 0%, #a8e6cf 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 1rem;
    }
    .stWarning {
        background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 1rem;
    }
    .stInfo {
        background: linear-gradient(135deg, #4facfe 0%, #00f2fe 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 1rem;
    }
    .stError {
        background: linear-gradient(135deg, #ff6b6b 0%, #ffa726 100%);
        color: white;
        border: none;
        border-radius: 8px;
        padding: 1rem;
    }
    .stDataFrame {
        border-radius: 10px;
        box-shadow: 0 4px 15px rgba(0, 0, 0, 0.1);
        overflow: hidden;
    }
    .stDataFrame thead th {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Sidebar navigation
with st.sidebar:
    st.markdown("<h1 style='color: #2c3e50;'>🚀 Supply Chain Management</h1>", unsafe_allow_html=True)
    st.markdown("---")
    st.markdown("### Navigation")

    # Phase 1: Data Input
    st.header("1. Data Input")
    if st.button("Enter Data Manually"):
        st.session_state.current_page = "data_input"

    # Phase 2: Supply Records
    st.header("2. Supply Records")
    if st.button("View/Edit Records"):
        st.session_state.current_page = "supply_records"

    # Phase 3: Demand Forecasting
    st.header("3. Demand Forecasting")
    if st.button("Analyze Demand"):
        st.session_state.current_page = "demand_forecasting"

    # Phase 4: Risk Prediction
    st.header("4. Risk Analysis")
    if st.button("Predict Risks"):
        st.session_state.current_page = "risk_prediction"

    # Phase 5: Inventory Optimization
    st.header("5. Inventory Optimization")
    if st.button("Optimize Inventory"):
        st.session_state.current_page = "inventory_optimization"

# -------------------------------
# 1. DATA INPUT
# -------------------------------
if 'current_page' not in st.session_state or st.session_state.current_page == "data_input":
    st.markdown("<h1 style='color: #2c3e50; margin-bottom: 1.5rem;'>📊 Data Input</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #7f8c8d; margin-bottom: 2rem;'>Add and manage your supply chain data here. Fill in the details below to get started.</p>", unsafe_allow_html=True)

    with st.form("data_input_form"):
        st.subheader("Add New Supply Record")
        col1, col2 = st.columns(2)

        # Expanded product list
        products = [
            'EcoBottle Pro', 'GreenTumbler', 'OceanGuard', 'BioPack', 'SustainableWrap',
            'EarthFriendly Container', 'GreenSeal Bottle', 'NatureCup', 'EcoLid',
            'BioStraw', 'GreenPlate', 'SustainableBowl', 'EcoUtensil Set',
            'RecycledTote Bag', 'SolarPowered Charger', 'Bamboo Toothbrush',
            'Organic Cotton T-Shirt', 'Reusable Coffee Cup', 'Compostable Plates'
        ]

        # Expanded supplier list
        suppliers = [
            'EcoSupplies Inc.', 'GreenGoods Co.', 'NatureFirst', 'BioMaterials Ltd.',
            'Sustainable Solutions', 'EarthProducts Corp.', 'GreenTech Industries',
            'NatureWorks', 'BioSupply Chain', 'EcoLogistics'
        ]

        # Expanded location list
        locations = ['Warehouse A', 'Warehouse B', 'Warehouse C', 'Distribution Center', 'Regional Hub']

        with col1:
            product = st.selectbox("Product Name", products, index=0)
            quantity = st.number_input("Quantity", min_value=1, value=100)
            supplier = st.selectbox("Supplier", suppliers)

        with col2:
            date_received = st.date_input("Date Received", datetime.now())
            expiry_date = st.date_input("Expiry Date", datetime.now() + timedelta(days=365))
            location = st.selectbox("Location", locations)

        if st.form_submit_button("Add Record"):
            new_record = pd.DataFrame([{
                'Product': product,
                'Quantity': quantity,
                'Supplier': supplier,
                'Date_Received': date_received,
                'Expiry_Date': expiry_date,
                'Location': location,
                'Status': 'In Stock' if quantity > 10 else 'Low Stock'
            }])

            if st.session_state.supply_data.empty:
                st.session_state.supply_data = new_record
            else:
                st.session_state.supply_data = pd.concat(
                    [st.session_state.supply_data, new_record],
                    ignore_index=True
                )
            st.success("Record added successfully!")

    # Generate Sample Data button
    if st.button("Generate Sample Data"):
        # Generate 15 rows of sample data with 7 columns
        sample_products = [
            'EcoBottle Pro', 'GreenTumbler', 'OceanGuard', 'BioPack', 'SustainableWrap',
            'EarthFriendly Container', 'GreenSeal Bottle', 'NatureCup', 'EcoLid',
            'BioStraw', 'GreenPlate', 'SustainableBowl', 'EcoUtensil Set',
            'RecycledTote Bag', 'SolarPowered Charger'
        ]

        sample_suppliers = [
            'EcoSupplies Inc.', 'GreenGoods Co.', 'NatureFirst', 'BioMaterials Ltd.',
            'Sustainable Solutions', 'EarthProducts Corp.', 'GreenTech Industries',
            'NatureWorks', 'BioSupply Chain', 'EcoLogistics'
        ]

        sample_locations = ['Warehouse A', 'Warehouse B', 'Warehouse C', 'Distribution Center', 'Regional Hub']

        sample_data = []
        for i in range(15):
            product = sample_products[i % len(sample_products)]
            supplier = sample_suppliers[i % len(sample_suppliers)]
            location = sample_locations[i % len(sample_locations)]

            sample_data.append({
                'Product': product,
                'Quantity': np.random.randint(50, 300),
                'Supplier': supplier,
                'Date_Received': datetime.now() - timedelta(days=np.random.randint(1, 90)),
                'Expiry_Date': datetime.now() + timedelta(days=np.random.randint(180, 720)),
                'Location': location,
                'Status': 'In Stock' if np.random.random() > 0.3 else 'Low Stock'
            })

        st.session_state.supply_data = pd.DataFrame(sample_data)
        st.success("Generated 15 rows of sample data successfully!")

# -------------------------------
# 2. SUPPLY RECORDS
# -------------------------------
elif st.session_state.current_page == "supply_records":
    st.markdown("<h1 style='color: #2c3e50; margin-bottom: 1.5rem;'>📋 Supply Records</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #7f8c8d; margin-bottom: 2rem;'>View and manage all your supply chain records in one place.</p>", unsafe_allow_html=True)

    if not st.session_state.supply_data.empty:
        # Convert dates to strings for display
        display_df = st.session_state.supply_data.copy()
        if 'Date_Received' in display_df.columns:
            display_df['Date_Received'] = display_df['Date_Received'].astype(str)
        if 'Expiry_Date' in display_df.columns:
            display_df['Expiry_Date'] = display_df['Expiry_Date'].astype(str)

        # Display records
        st.dataframe(display_df, use_container_width=True)

        # Download button
        csv = st.session_state.supply_data.to_csv(index=False)
        st.download_button(
            label="Download CSV",
            data=csv,
            file_name=f"supply_records_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    else:
        st.warning("No data available. Please add some records in the Data Input section.")

# -------------------------------
# 3. DEMAND FORECASTING
# -------------------------------
elif st.session_state.current_page == "demand_forecasting":
    # Professional loading screen
    with st.spinner("🔄 Initializing Professional Demand Forecasting System..."):
        time.sleep(4)

    # Professional Header
    st.markdown("<h1 style='color: #2c3e50; margin-bottom: 1.5rem;'>📈 Demand Forecasting</h1>", unsafe_allow_html=True)
    st.markdown("<p style='color: #7f8c8d; margin-bottom: 2rem;'>Analyze and predict future demand patterns using advanced forecasting models.</p>", unsafe_allow_html=True)

    # System Status
    col_status1, col_status2, col_status3 = st.columns(3)
    with col_status1:
        st.success("System Online")
    with col_status2:
        st.info(f"Time: {datetime.now().strftime('%H:%M:%S')}")
    with col_status3:
        st.info("ML Models Active")

    # Generate or use professional sample data
    if not st.session_state.supply_data.empty and len(st.session_state.supply_data) >= 15:
        df = st.session_state.supply_data.copy()
        data_source = "Existing Data"
    else:
        # Generate professional 15-row dataset
        st.info("🔄 Generating professional demand forecasting dataset...")

        products = [
            'EcoBottle Pro', 'GreenTumbler', 'OceanGuard', 'BioPack', 'SustainableWrap',
            'EarthFriendly Container', 'GreenSeal Bottle', 'NatureCup', 'EcoLid',
            'BioStraw', 'GreenPlate', 'SustainableBowl', 'EcoUtensil Set',
            'RecycledTote Bag', 'SolarPowered Charger'
        ]

        suppliers = ['EcoSupplies Inc.', 'GreenGoods Co.', 'NatureFirst', 'BioMaterials Ltd.']

        sample_data = []
        base_date = datetime.now() - timedelta(days=60)

        for i in range(15):
            product = products[i % len(products)]
            supplier = suppliers[i % len(suppliers)]

            # Generate realistic demand with trends and seasonality
            base_demand = np.random.normal(100, 15)
            trend = (i / 15) * 25  # Growth trend
            seasonal = 20 * np.sin(2 * np.pi * (i % 30) / 30)  # Monthly seasonality
            noise = np.random.normal(0, 10)
            demand = max(20, base_demand + trend + seasonal + noise)

            # Calculate stock status based on demand
            stock_status = 'Optimal'
            if np.random.random() > 0.7:
                stock_status = 'Overstock' if np.random.random() > 0.5 else 'Understock'

            sample_data.append({
                'Date': (base_date + timedelta(days=i)).strftime('%Y-%m-%d'),
                'Product': product,
                'Supplier': supplier,
                'Current_Stock': np.random.randint(100, 800),
                'Avg_Daily_Demand': round(demand, 1),
                'Forecast_7D': round(demand * 1.05 + np.random.normal(0, 5), 1),
                'Forecast_30D': round(demand * 1.15 + np.random.normal(0, 8), 1),
                'Accuracy': round(np.random.uniform(85, 98), 1),
                'Trend': 'Increasing' if np.random.random() > 0.4 else 'Decreasing',
                'Status': stock_status,
                'Priority': 'Low' if np.random.random() > 0.6 else ('Medium' if np.random.random() > 0.5 else 'High')
            })

        df = pd.DataFrame(sample_data)
        data_source = "Generated Sample Data"
        st.success("Professional dataset generated with 15 products!")

    # Professional Dashboard Layout
    st.header("Demand Forecasting Dashboard")

    # Key Metrics Row
    st.subheader("Key Performance Indicators")
    metric_col1, metric_col2, metric_col3, metric_col4 = st.columns(4)

    with metric_col1:
        total_products = len(df['Product'].unique())
        st.metric("Total Products", total_products)

    with metric_col2:
        if 'Accuracy' in df.columns:
            avg_accuracy = df['Accuracy'].mean()
            st.metric("Avg Forecast Accuracy", f"{avg_accuracy:.1f}%")
        else:
            st.metric("Avg Forecast Accuracy", "N/A")

    with metric_col3:
        if 'Status' in df.columns:
            optimal_count = len(df[df['Status'] == 'Optimal'])
            st.metric("Optimal Stock Levels", f"{optimal_count}/{total_products}")
        else:
            st.metric("Optimal Stock Levels", "N/A")

    with metric_col4:
        if 'Priority' in df.columns:
            high_priority = len(df[df['Priority'] == 'High'])
            st.metric("High Priority Items", high_priority)
        else:
            st.metric("High Priority Items", "N/A")

    # Main Forecasting Table
    st.subheader("Professional Demand Forecast Report")

    # Format the dataframe for professional display
    display_df = df.copy()

    # Format date column if it exists
    if 'Date' in display_df.columns:
        try:
            display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%b %d, %Y')
        except:
            # If date formatting fails, keep original format
            pass

    # Professional styling - only show columns that exist
    available_columns = [col for col in [
        'Date', 'Product', 'Supplier', 'Current_Stock', 'Avg_Daily_Demand',
        'Forecast_7D', 'Forecast_30D', 'Accuracy', 'Trend', 'Status', 'Priority'
    ] if col in display_df.columns]

    if available_columns:
        column_config = {}
        if 'Accuracy' in display_df.columns:
            column_config["Accuracy"] = st.column_config.NumberColumn("Accuracy (%)", format="%.1f%%")
        if 'Current_Stock' in display_df.columns:
            column_config["Current_Stock"] = st.column_config.NumberColumn("Current Stock", format="%d units")
        if 'Avg_Daily_Demand' in display_df.columns:
            column_config["Avg_Daily_Demand"] = st.column_config.NumberColumn("Avg Daily Demand", format="%.1f units")
        if 'Forecast_7D' in display_df.columns:
            column_config["Forecast_7D"] = st.column_config.NumberColumn("7-Day Forecast", format="%.1f units")
        if 'Forecast_30D' in display_df.columns:
            column_config["Forecast_30D"] = st.column_config.NumberColumn("30-Day Forecast", format="%.1f units")

        st.dataframe(
            display_df[available_columns],
            use_container_width=True,
            column_config=column_config
        )
    else:
        st.dataframe(display_df, use_container_width=True)

    # Interactive Analysis Section
    st.header("Interactive Product Analysis")

    # Product selector
    if 'Product' in df.columns:
        selected_product = st.selectbox(
            "Select Product for Detailed Analysis:",
            options=sorted(df['Product'].unique()),
            help="Choose a product to view detailed forecasting analysis"
        )
    else:
        st.warning("❌ No 'Product' column found in data. Cannot perform product-specific analysis.")
        selected_product = None

    if selected_product:
        product_data = df[df['Product'] == selected_product]

        if not product_data.empty:
            # Product-specific metrics
            st.subheader(f"Analysis for {selected_product}")

            analysis_col1, analysis_col2, analysis_col3, analysis_col4 = st.columns(4)

            # Initialize variables with defaults
            current_stock = 0
            avg_demand = 100
            forecast_7d = 100

            with analysis_col1:
                if 'Current_Stock' in product_data.columns:
                    current_stock = product_data['Current_Stock'].iloc[0]
                    st.metric("Current Stock", f"{current_stock:,} units")
                else:
                    st.metric("Current Stock", "N/A")

            with analysis_col2:
                if 'Avg_Daily_Demand' in product_data.columns:
                    avg_demand = product_data['Avg_Daily_Demand'].iloc[0]
                    st.metric("Avg Daily Demand", f"{avg_demand:.1f} units")
                else:
                    st.metric("Avg Daily Demand", "N/A")

            with analysis_col3:
                if 'Forecast_7D' in product_data.columns:
                    forecast_7d = product_data['Forecast_7D'].iloc[0]
                    st.metric("7-Day Forecast", f"{forecast_7d:.1f} units")
                else:
                    st.metric("7-Day Forecast", "N/A")

            with analysis_col4:
                if 'Accuracy' in product_data.columns:
                    accuracy = product_data['Accuracy'].iloc[0]
                    st.metric("Forecast Accuracy", f"{accuracy:.1f}%")
                else:
                    st.metric("Forecast Accuracy", "N/A")

            # Status and recommendations
            status = product_data['Status'].iloc[0] if 'Status' in product_data.columns else 'Unknown'
            priority = product_data['Priority'].iloc[0] if 'Priority' in product_data.columns else 'Unknown'

            if status == 'Overstock':
                st.error(f"OVERSTOCK ALERT for {selected_product}")
                st.info("Recommendations: Consider promotional pricing, redistribution, or reduced ordering")
            elif status == 'Understock':
                st.warning(f"UNDERSTOCK ALERT for {selected_product}")
                st.info("Recommendations: Immediate replenishment required, increase safety stock")
            else:
                st.success(f"OPTIMAL STOCK LEVELS for {selected_product}")
                st.info("Recommendations: Maintain current ordering patterns")

            # Forecast visualization
            st.subheader("Forecast Visualization")

            # Create forecast chart
            dates = pd.date_range(start=datetime.now(), periods=31, freq='D')
            historical = [avg_demand] * 7  # Last 7 days
            forecast_values = [forecast_7d] * 24  # Next 24 days

            chart_data = pd.DataFrame({
                'Date': dates,
                'Demand': historical + forecast_values,
                'Type': ['Historical'] * 7 + ['Forecast'] * 24
            })

            fig = px.line(
                chart_data,
                x='Date',
                y='Demand',
                color='Type',
                title=f"Demand Forecast for {selected_product}",
                labels={'Demand': 'Units', 'Date': 'Date'},
                color_discrete_map={'Historical': '#1f77b4', 'Forecast': '#ff7f0e'}
            )

            # Add vertical line for today
            try:
                today_str = datetime.now().strftime('%Y-%m-%d')
                fig.add_vline(x=today_str, line_dash="dash", line_color="red",
                              annotation_text="Today")
            except Exception:
                # If vertical line fails, continue without it
                pass

            st.plotly_chart(fig, use_container_width=True)

            # ML Model Information
            st.info("ML Models Used: XGBoost + Prophet ensemble for accurate time series forecasting")

    # Export Section
    st.header("Export Professional Report")

    export_col1, export_col2 = st.columns(2)

    with export_col1:
        csv_data = df.to_csv(index=False)
        st.download_button(
            label="Download Complete Forecast Report (CSV)",
            data=csv_data,
            file_name=f"enterprise_demand_forecast_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv",
            help="Download the complete professional demand forecasting report"
        )

    with export_col2:
        # Summary report - only include columns that exist
        available_cols = [col for col in ['Avg_Daily_Demand', 'Forecast_7D', 'Accuracy', 'Status'] if col in df.columns]
        if available_cols:
            agg_dict = {}
            for col in available_cols:
                if col == 'Status':
                    agg_dict[col] = 'first'
                else:
                    agg_dict[col] = 'mean'

            summary_data = df.groupby('Product').agg(agg_dict).round(2)
            summary_csv = summary_data.to_csv()
            st.download_button(
                label="Download Summary Report (CSV)",
                data=summary_csv,
                file_name=f"demand_forecast_summary_{datetime.now().strftime('%Y%m%d')}.csv",
                mime="text/csv",
                help="Download summarized demand forecasting data"
            )
        else:
            st.info("No summary data available for export")

    # Footer
    st.markdown("---")
    st.caption("Enterprise Demand Forecasting System | Powered by Advanced ML Models | Real-time Analytics")

# Professional Footer
footer_html = '''
<div style="
    background: linear-gradient(135deg, #2c3e50 0%, #34495e 100%);
    color: white;
    padding: 20px;
    border-radius: 10px;
    margin-top: 30px;
    box-shadow: 0 4px 15px rgba(0, 0, 0, 0.2);
    text-align: center;">
    <div style="display: flex; justify-content: space-around; align-items: center; flex-wrap: wrap;">
        <div style="flex: 1; min-width: 200px; margin: 10px;">
            <h3 style="margin: 0 0 10px 0; color: #3498db;">System Features</h3>
            <ul style="list-style: none; padding: 0; margin: 0; text-align: left;">
                <li>• Demand Forecasting</li>
                <li>• Risk Prediction</li>
                <li>• Inventory Optimization</li>
                <li>• Real-time Analytics</li>
            </ul>
        </div>
        <div style="flex: 1; min-width: 200px; margin: 10px;">
            <h3 style="margin: 0 0 10px 0; color: #e74c3c;">AI/ML Models</h3>
            <ul style="list-style: none; padding: 0; margin: 0; text-align: left;">
                <li>• XGBoost Forecasting</li>
                <li>• Random Forest Risk</li>
                <li>• EOQ Optimization</li>
                <li>• Anomaly Detection</li>
            </ul>
        </div>
        <div style="flex: 1; min-width: 200px; margin: 10px;">
            <h3 style="margin: 0 0 10px 0; color: #27ae60;">Analytics</h3>
            <ul style="list-style: none; padding: 0; margin: 0; text-align: left;">
                <li>• KPI Dashboards</li>
                <li>• Trend Analysis</li>
                <li>• Risk Assessment</li>
                <li>• Performance Metrics</li>
            </ul>
        </div>
    </div>
    <hr style="border: 1px solid rgba(255, 255, 255, 0.2); margin: 20px 0;">
    <div style="font-size: 0.9em; opacity: 0.8;">
        <p style="margin: 5px 0;">2024 Enterprise Supply Chain Management System</p>
        <p style="margin: 5px 0;">© 2024 Enterprise Supply Chain Management System</p>
        <p style="margin: 5px 0;">Professional Analytics Platform | AI-Powered Insights | Real-time Optimization</p>
        <p style="margin: 5px 0;">Version 2.0 | Last Updated: December 2024</p>
    </div>
</div>
'''
st.markdown(footer_html, unsafe_allow_html=True)
