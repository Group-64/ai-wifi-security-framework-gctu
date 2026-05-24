# 🛡️ AI-Based Campus WiFi Security Assessment and Anomaly Detection Framework for GCTU

## 📌 Project Overview
This project develops an AI-based framework for detecting anomalies and assessing security risks in campus WiFi networks, specifically tailored to Ghana Communication Technology University (GCTU). The system uses machine learning (Isolation Forest) to identify suspicious network activities such as brute force attacks, rogue access points, port scanning, and DDoS attempts.

## 👥 Group Members
| Name | Student ID |
|------|------------|
| Ahaja Takyi Abigail | 1722940224 |
| Grace Amoako Afua Pokuaa Ampomah | 1722678900 |
| Adu Ampomah Bright | 1723544373 |

**Supervisor:** Dr. Martin Mabeifam Ujakpa

## 🚀 Features
- ✅ Synthetic WiFi data generator (simulates GCTU campus traffic)
- ✅ Isolation Forest anomaly detection model
- ✅ Interactive Streamlit dashboard
- ✅ Real-time anomaly detection and alerting
- ✅ Security score calculation (0-100)
- ✅ Severity classification (CRITICAL, HIGH, MEDIUM, LOW)
- ✅ Performance metrics (Accuracy, Precision, Recall, F1-Score)
- ✅ CSV report export

## 📁 Project Structure
ai-wifi-security-framework-gctu/
├── src/
│ ├── anomaly_detector.py # AI model implementation
│ └── data_generator.py # Synthetic data generation
├── dashboard/
│ └── app.py # Streamlit web interface
├── data/
│ ├── raw/ # Original datasets
│ ├── processed/ # Cleaned data
│ └── synthetic/ # Generated sample data
├── models/ # Saved trained models
├── config/ # Configuration files
├── requirements.txt # Python dependencies
└── README.md # This file


## 💻 Installation & Setup

### Prerequisites
- Python 3.9 or higher
- Git
- PyCharm (recommended) or any Python IDE

### Step 1: Clone the Repository
```bash
git clone https://github.com/Group-64/ai-wifi-security-framework-gctu.git
cd ai-wifi-security-framework-gctu
