# Supply Chain Management System

## 🚀 Advanced AI-Powered Supply Chain Optimization Platform

A comprehensive, enterprise-grade supply chain management system that leverages cutting-edge machine learning algorithms to optimize demand forecasting, inventory management, and risk assessment.

![Supply Chain Management](https://img.shields.io/badge/Supply%20Chain-AI--Powered-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3.8+-green?style=for-the-badge)
![React](https://img.shields.io/badge/React-18+-blue?style=for-the-badge)
![FastAPI](https://img.shields.io/badge/FastAPI-Modern-orange?style=for-the-badge)

## 📋 Table of Contents

- [Features](#-features)
- [Technology Stack](#-technology-stack)
- [Installation](#-installation)
- [Usage](#-usage)
- [API Documentation](#-api-documentation)
- [Machine Learning Models](#-machine-learning-models)
- [Data Format](#-data-format)
- [Contributing](#-contributing)
- [License](#-license)

## ✨ Features

### 🎯 Core Capabilities

- **Demand Forecasting**: Advanced time series analysis using XGBoost and Prophet
- **Inventory Optimization**: EOQ calculations, safety stock recommendations, reorder point analysis
- **Risk Assessment**: ML-powered risk prediction using Random Forest and Logistic Regression
- **Real-time Analytics**: Interactive dashboards with comprehensive KPIs
- **Data Integration**: Seamless CSV upload and processing
- **Export Functionality**: Professional reporting with CSV/PDF export capabilities

### 🔧 Advanced Features

- **Multi-Model Ensemble**: Combines multiple ML algorithms for superior accuracy
- **Automated Alerts**: Real-time monitoring with drift detection
- **Interactive Visualizations**: Beautiful charts powered by Plotly
- **Responsive Design**: Works perfectly on desktop, tablet, and mobile
- **Enterprise Security**: JWT-based authentication and authorization
- **Scalable Architecture**: Built with FastAPI and React for high performance

## 🛠 Technology Stack

### Backend
- **Python 3.8+**
- **FastAPI**: High-performance async web framework
- **SQLAlchemy**: Database ORM
- **SQLite**: Database (easily configurable for PostgreSQL/MySQL)

### Machine Learning
- **XGBoost**: Gradient boosting for demand forecasting
- **Prophet**: Time series forecasting by Meta
- **Random Forest**: Ensemble learning for risk assessment
- **Logistic Regression**: Interpretable risk modeling
- **Scikit-learn**: Machine learning utilities
- **MLflow**: Experiment tracking and model management

### Frontend
- **React 18**: Modern JavaScript library
- **React Router**: Client-side routing
- **Plotly.js**: Interactive data visualizations
- **Axios**: HTTP client for API calls
- **CSS3**: Modern styling with responsive design

### DevOps & Tools
- **Docker**: Containerization
- **Git**: Version control
- **ESLint**: Code linting
- **Prettier**: Code formatting

## 📦 Installation

### Prerequisites

- Python 3.8 or higher
- Node.js 16 or higher
- npm or yarn package manager

### Backend Setup

1. **Clone the repository**
   ```bash
   git clone https://github.com/your-org/supply-chain-management.git
   cd supply-chain-management
   ```

2. **Create virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Python dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Initialize database**
   ```bash
   python -c "from backend.app.db import init_db; init_db()"
   ```

### Frontend Setup

1. **Navigate to frontend directory**
   ```bash
   cd frontend
   ```

2. **Install Node.js dependencies**
   ```bash
   npm install
   ```

3. **Start development server**
   ```bash
   npm run dev
   ```

### Running the Application

1. **Start the backend server**
   ```bash
   cd backend
   uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

2. **Start the frontend (in another terminal)**
   ```bash
   cd frontend
   npm run dev
   ```

3. **Access the application**
   - Frontend: http://localhost:5173
   - Backend API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs

## 🎯 Usage

### Getting Started

1. **Sign Up/Login**: Create an account or login with existing credentials
2. **Upload Data**: Upload your supply chain data in CSV format
3. **Run Analysis**: Choose from demand forecasting, inventory optimization, or risk assessment
4. **View Results**: Explore interactive dashboards and detailed analytics
5. **Export Reports**: Download comprehensive reports for business decisions

### Sample Data

The system includes sample datasets for testing:
- `data/sample_supply_chain_data.csv`: 900 rows of sample supply chain data
- `data/professional_supply_chain_data.csv`: 9,491 rows of comprehensive data

## 📊 Machine Learning Models

### Demand Forecasting Models

#### XGBoost
- **Use Case**: Complex pattern recognition in demand data
- **Features**: Handles non-linear relationships, feature importance analysis
- **Accuracy**: Typically 85-95% depending on data quality

#### Prophet
- **Use Case**: Time series forecasting with seasonality
- **Features**: Automatic seasonality detection, holiday effects
- **Accuracy**: Excellent for seasonal and trend-based demand

#### Ensemble Model
- **Use Case**: Best of both worlds approach
- **Features**: Combines XGBoost and Prophet predictions
- **Accuracy**: Generally highest accuracy among all models

### Risk Assessment Models

#### Random Forest
- **Use Case**: Complex risk factor analysis
- **Features**: Handles non-linear relationships, feature importance
- **Output**: Risk probability scores with confidence intervals

#### Logistic Regression
- **Use Case**: Interpretable risk assessment
- **Features**: Clear coefficient interpretation, fast training
- **Output**: Binary risk classification with probability scores

## 📋 Data Format

### Required CSV Format

```csv
Date,Product,Supplier,Location,Quantity_Sold,Unit_Cost,Lead_Time_Days,Current_Stock,Defect_Rate,On_Time_Rate,Distance_KM,Return_Rate,Price_Variance,Expiry_Date,Status,Risk_Label
2024-01-01,EcoBottle Pro,EcoSupplies Inc.,Warehouse A,109,12.02,16,120,0.0429,0.9675,643,0.0061,0.0226,2024-12-03,Critical,1
```

### Column Descriptions

| Column | Type | Description | Required |
|--------|------|-------------|----------|
| Date | Date | Transaction date | Yes |
| Product | String | Product name | Yes |
| Supplier | String | Supplier name | No |
| Location | String | Storage location | No |
| Quantity_Sold | Number | Units sold/demanded | Yes* |
| Unit_Cost | Number | Cost per unit | No |
| Lead_Time_Days | Number | Supplier lead time | No |
| Current_Stock | Number | Current inventory level | No |
| Defect_Rate | Number | Product defect rate (0-1) | No |
| On_Time_Rate | Number | Supplier on-time delivery rate | No |
| Distance_KM | Number | Distance to supplier | No |
| Return_Rate | Number | Product return rate | No |
| Price_Variance | Number | Price fluctuation rate | No |
| Expiry_Date | Date | Product expiry date | No |
| Status | String | Stock status | No |
| Risk_Label | Number | Risk indicator (0=Low, 1=High) | No |

*Either `Quantity_Sold`, `Sales`, `Quantity`, `Qty`, or `Demand` column is required

## 🔌 API Documentation

### Authentication Endpoints

```http
POST /api/auth/login
POST /api/auth/register
POST /api/auth/refresh
```

### ML Endpoints

```http
POST /api/forecast          # Demand forecasting
POST /api/forecast_explain  # Model explanations
POST /api/risk             # Risk assessment
POST /api/inventory        # Inventory optimization
```

### Dashboard Endpoints

```http
GET /api/dashboard/summary  # Dashboard metrics
GET /api/dashboard/alerts   # System alerts
```

## 🤝 Contributing

We welcome contributions! Please follow these steps:

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Guidelines

- Follow PEP 8 for Python code
- Use ESLint configuration for JavaScript/React
- Write comprehensive tests for new features
- Update documentation for API changes
- Ensure responsive design for all new components

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **Meta** for Prophet library
- **Microsoft** for LightGBM
- **University of Washington** for XGBoost
- **React Team** for React framework
- **FastAPI Team** for FastAPI framework

## 📞 Support

For support and questions:
- 📧 Email: support@supplychainmgmt.com
- 📖 Documentation: [docs.supplychainmgmt.com](https://docs.supplychainmgmt.com)
- 🐛 Bug Reports: [GitHub Issues](https://github.com/your-org/supply-chain-management/issues)

---

**Built with ❤️ for optimizing global supply chains**

[![GitHub stars](https://img.shields.io/github/stars/your-org/supply-chain-management?style=social)](https://github.com/your-org/supply-chain-management)
[![GitHub forks](https://img.shields.io/github/forks/your-org/supply-chain-management?style=social)](https://github.com/your-org/supply-chain-management)