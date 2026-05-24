"""
GCTU WiFi Security Dashboard
Streamlit application for visualizing anomaly detection results
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import joblib
import numpy as np
import sys
import os

# Add src to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..'))

# Import anomaly detector
from src.anomaly_detector import AnomalyDetector

# Page configuration
st.set_page_config(
    page_title="GCTU WiFi Security Framework",
    page_icon="🛡️",
    layout="wide"
)

# Custom CSS for GCTU colors
st.markdown("""
<style>
    .stApp {
        background-color: #f5f5f5;
    }
    .metric-card {
        background-color: #ffffff;
        border-radius: 10px;
        padding: 15px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    .alert-critical {
        background-color: #ffebee;
        border-left: 4px solid #dc3545;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
    }
    .alert-high {
        background-color: #fff3e0;
        border-left: 4px solid #ff9800;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
    }
    .alert-medium {
        background-color: #fff9c4;
        border-left: 4px solid #ffc107;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
    }
    .alert-low {
        background-color: #e8f5e9;
        border-left: 4px solid #4caf50;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
    }
</style>
""", unsafe_allow_html=True)

# Title
st.title("🛡️ GCTU WiFi Security Framework")
st.markdown("*AI-Based Campus WiFi Security Assessment and Anomaly Detection*")
st.markdown("---")

# Sidebar
with st.sidebar:
    st.header("⚙️ Configuration")

    # File upload
    uploaded_file = st.file_uploader("Upload Network Data (CSV)", type=["csv"])

    # Model selection
    model_type = st.selectbox(
        "Detection Model",
        ["Isolation Forest", "One-Class SVM", "Ensemble"]
    )

    # Threshold and contamination
    threshold = st.slider("Anomaly Threshold", 0.0, 1.0, 0.7, 0.05)
    contamination = st.slider("Expected Anomaly Rate", 0.01, 0.30, 0.10, 0.01)

    st.markdown("---")
    st.caption("GCTU - Cybersecurity Option Final Year Project")
    st.caption("Version 1.0")

# Main content
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    st.success(f"✅ Loaded {len(df):,} records from {uploaded_file.name}")

    # Display data preview
    with st.expander("📋 Data Preview"):
        st.dataframe(df.head(10), use_container_width=True)
        st.caption(f"Columns: {', '.join(df.columns.tolist())}")

    # Check if required columns exist
    required_cols = ['timestamp', 'signal_rssi', 'data_up_mb', 'data_down_mb', 'duration_sec']
    missing_cols = [col for col in required_cols if col not in df.columns]

    if missing_cols:
        st.error(f"❌ Missing required columns: {missing_cols}")
        st.info("Please ensure your CSV has: timestamp, signal_rssi, data_up_mb, data_down_mb, duration_sec")
    else:
        # Run detection button
        if st.button("🚀 Run Anomaly Detection", type="primary", use_container_width=True):
            with st.spinner("Training AI model and detecting anomalies..."):
                # Initialize detector
                detector = AnomalyDetector(contamination=contamination, random_state=42)

                # Train on the data (unsupervised)
                detector.train(df)

                # Predict anomalies
                results = detector.predict(df)

                # Store in session state
                st.session_state['results'] = results
                st.session_state['detector'] = detector

            st.success("✅ Anomaly detection complete!")
            st.balloons()

        # Display results if available
        if 'results' in st.session_state:
            results = st.session_state['results']

            # Calculate metrics from predictions
            total_records = len(results)
            anomaly_count = results['is_predicted_anomaly'].sum()
            anomaly_percentage = (anomaly_count / total_records) * 100
            security_score = max(0, 100 - (anomaly_percentage * 2))

            # Determine risk level
            if security_score >= 80:
                risk_level = "🟢 Low Risk"
            elif security_score >= 60:
                risk_level = "🟡 Medium Risk"
            else:
                risk_level = "🔴 High Risk"

            # Row 1: Key Metrics
            st.subheader("📊 Security Dashboard")

            col1, col2, col3, col4 = st.columns(4)

            with col1:
                st.metric("Total Records", f"{total_records:,}")
            with col2:
                st.metric("Anomalies Detected", f"{anomaly_count:,}", delta=f"{anomaly_percentage:.1f}%")
            with col3:
                st.metric("Security Score", f"{security_score:.0f}/100")
            with col4:
                st.metric("Risk Level", risk_level)

            # Row 2: Security Gauge and Distribution
            col1, col2 = st.columns(2)

            with col1:
                # Security Gauge
                fig_gauge = go.Figure(go.Indicator(
                    mode="gauge+number",
                    value=security_score,
                    title={"text": "Security Assessment"},
                    domain={"x": [0, 1], "y": [0, 1]},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "#003366"},
                        "steps": [
                            {"range": [0, 50], "color": "#dc3545"},
                            {"range": [50, 75], "color": "#ffc107"},
                            {"range": [75, 100], "color": "#28a745"}
                        ]
                    }
                ))
                fig_gauge.update_layout(height=300)
                st.plotly_chart(fig_gauge, use_container_width=True)

            with col2:
                # Distribution Pie Chart
                dist_data = results['is_predicted_anomaly'].value_counts()
                fig_pie = go.Figure(data=[go.Pie(
                    labels=['Normal Traffic', 'Anomalies'],
                    values=[dist_data.get(0, 0), dist_data.get(1, 0)],
                    hole=0.4,
                    marker_colors=['#28a745', '#dc3545'],
                    textinfo='label+percent'
                )])
                fig_pie.update_layout(title="Traffic Distribution", height=300)
                st.plotly_chart(fig_pie, use_container_width=True)

            # Row 3: Anomaly Timeline
            st.subheader("📈 Anomaly Detection Timeline")

            if 'timestamp' in results.columns:
                results['timestamp'] = pd.to_datetime(results['timestamp'])
                timeline_df = results.set_index('timestamp').resample('1h').agg({
                    'is_predicted_anomaly': 'sum'
                }).reset_index()

                fig_timeline = go.Figure()
                fig_timeline.add_trace(go.Scatter(
                    x=timeline_df['timestamp'],
                    y=timeline_df['is_predicted_anomaly'],
                    mode='lines+markers',
                    name='Anomalies',
                    line=dict(color='#dc3545', width=2),
                    marker=dict(size=4, color='#dc3545')
                ))

                # Add threshold line
                threshold_val = timeline_df['is_predicted_anomaly'].mean() * 1.5
                fig_timeline.add_hline(
                    y=threshold_val,
                    line_dash="dash",
                    line_color="red",
                    annotation_text="Alert Threshold"
                )

                fig_timeline.update_layout(
                    title="Anomaly Count Over Time",
                    xaxis_title="Time",
                    yaxis_title="Number of Anomalies",
                    height=400
                )
                st.plotly_chart(fig_timeline, use_container_width=True)

            # Row 4: Alerts Table with ALL SEVERITY LEVELS (Including GREEN/LOW)
            st.subheader("🚨 Anomaly Alerts")

            alerts = results[results['is_predicted_anomaly'] == 1].copy()

            if len(alerts) > 0:
                # Define severity based on anomaly score - NOW INCLUDES LOW (GREEN)
                def get_severity(score):
                    if score < -0.6:
                        return "🔴 CRITICAL"      # Red
                    elif score < -0.4:
                        return "🟡 HIGH"          # Yellow
                    elif score < -0.2:
                        return "🟠 MEDIUM"        # Orange
                    else:
                        return "🟢 LOW"           # GREEN - Normal/Low risk

                alerts['severity'] = alerts['anomaly_score'].apply(get_severity)

                # Display alerts with severity counts
                severity_counts = alerts['severity'].value_counts()
                st.caption(f"Alert Summary: {dict(severity_counts)}")

                # Display alerts table
                display_cols = ['timestamp', 'device_id', 'ap_id', 'anomaly_score', 'severity']
                available_cols = [col for col in display_cols if col in alerts.columns]

                st.dataframe(alerts[available_cols].head(20), use_container_width=True, height=300)

                # Download button
                csv = alerts.to_csv(index=False)
                st.download_button(
                    label="📥 Download Alerts (CSV)",
                    data=csv,
                    file_name="anomaly_alerts.csv",
                    mime="text/csv"
                )
            else:
                st.info("✅ No anomalies detected in the processed data.")

            # Row 5: Model Evaluation (if ground truth available)
            if 'is_anomaly' in results.columns:
                st.subheader("📊 Model Performance Evaluation")

                y_true = results['is_anomaly']
                y_pred = results['is_predicted_anomaly']

                # Calculate metrics
                tp = ((y_true == 1) & (y_pred == 1)).sum()
                tn = ((y_true == 0) & (y_pred == 0)).sum()
                fp = ((y_true == 0) & (y_pred == 1)).sum()
                fn = ((y_true == 1) & (y_pred == 0)).sum()

                accuracy = (tp + tn) / (tp + tn + fp + fn) if (tp + tn + fp + fn) > 0 else 0
                precision = tp / (tp + fp) if (tp + fp) > 0 else 0
                recall = tp / (tp + fn) if (tp + fn) > 0 else 0
                f1 = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0

                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Accuracy", f"{accuracy:.2%}")
                with col2:
                    st.metric("Precision", f"{precision:.2%}")
                with col3:
                    st.metric("Recall", f"{recall:.2%}")
                with col4:
                    st.metric("F1-Score", f"{f1:.2%}")

                # Confusion Matrix
                cm = np.array([[tn, fp], [fn, tp]])
                fig_cm = px.imshow(
                    cm,
                    text_auto=True,
                    labels=dict(x="Predicted", y="Actual", color="Count"),
                    x=["Normal", "Anomaly"],
                    y=["Normal", "Anomaly"],
                    color_continuous_scale="Blues"
                )
                fig_cm.update_layout(height=400, title="Confusion Matrix")
                st.plotly_chart(fig_cm, use_container_width=True)

else:
    # Show placeholder when no data uploaded
    st.info("👈 Please upload a CSV file to begin analysis")

    # Sample preview
    st.subheader("Expected Data Format")
    sample_df = pd.DataFrame({
        'timestamp': ['2024-03-15 08:00:00', '2024-03-15 08:05:00'],
        'device_id': ['DEV_0001', 'DEV_0002'],
        'ap_id': ['AP_01', 'AP_02'],
        'signal_rssi': [-55, -62],
        'data_up_mb': [45.2, 128.7],
        'data_down_mb': [234.5, 512.3],
        'duration_sec': [320, 180]
    })
    st.dataframe(sample_df)
    st.caption("Required columns: timestamp, signal_rssi, data_up_mb, data_down_mb, duration_sec")

st.markdown("---")
st.caption("© 2024-2026 GCTU - AI-Based WiFi Security Framework")
