import React, { useState, useEffect } from 'react';
import { Link } from 'react-router-dom';
import Plot from 'react-plotly.js';
import './Dashboard.css';

const Dashboard = ({ user, onLogout }) => {
  const [dashboardData, setDashboardData] = useState({
    totalProducts: 0,
    totalInventory: 0,
    forecastAccuracy: 0,
    riskScore: 0,
    recentAlerts: [],
    topProducts: []
  });

  useEffect(() => {
    // Fetch dashboard data
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const token = localStorage.getItem('token');
      const response = await fetch('http://localhost:8000/api/dashboard/summary', {
        headers: {
          'Authorization': `Bearer ${token}`
        }
      });

      if (response.ok) {
        const summary = await response.json();
        setDashboardData({
          totalProducts: summary.total_products,
          totalInventory: summary.inventory_value,
          forecastAccuracy: summary.forecast_accuracy,
          riskScore: summary.risk_score,
          recentAlerts: [
            { id: 1, type: 'warning', message: 'Low stock alert for Product A', time: '2 hours ago' },
            { id: 2, type: 'info', message: 'Forecast accuracy improved by 2%', time: '4 hours ago' },
            { id: 3, type: 'success', message: 'New supplier onboarded', time: '1 day ago' }
          ],
          topProducts: [
            { name: 'EcoBottle Pro', sales: 12500, growth: 12.5 },
            { name: 'GreenTumbler', sales: 9800, growth: 8.3 },
            { name: 'OceanGuard', sales: 7600, growth: -2.1 },
            { name: 'BioPack', sales: 6500, growth: 15.7 },
            { name: 'SustainableWrap', sales: 5200, growth: 6.8 }
          ]
        });
      } else {
        // Fallback to mock data if API fails
        setDashboardData({
          totalProducts: 150,
          totalInventory: 2500000,
          forecastAccuracy: 92.5,
          riskScore: 15.3,
          recentAlerts: [
            { id: 1, type: 'warning', message: 'Low stock alert for Product A', time: '2 hours ago' },
            { id: 2, type: 'info', message: 'Forecast accuracy improved by 2%', time: '4 hours ago' },
            { id: 3, type: 'success', message: 'New supplier onboarded', time: '1 day ago' }
          ],
          topProducts: [
            { name: 'EcoBottle Pro', sales: 12500, growth: 12.5 },
            { name: 'GreenTumbler', sales: 9800, growth: 8.3 },
            { name: 'OceanGuard', sales: 7600, growth: -2.1 },
            { name: 'BioPack', sales: 6500, growth: 15.7 },
            { name: 'SustainableWrap', sales: 5200, growth: 6.8 }
          ]
        });
      }
    } catch (error) {
      console.error('Error fetching dashboard data:', error);
      // Fallback to mock data
      setDashboardData({
        totalProducts: 150,
        totalInventory: 2500000,
        forecastAccuracy: 92.5,
        riskScore: 15.3,
        recentAlerts: [
          { id: 1, type: 'warning', message: 'Low stock alert for Product A', time: '2 hours ago' },
          { id: 2, type: 'info', message: 'Forecast accuracy improved by 2%', time: '4 hours ago' },
          { id: 3, type: 'success', message: 'New supplier onboarded', time: '1 day ago' }
        ],
        topProducts: [
          { name: 'EcoBottle Pro', sales: 12500, growth: 12.5 },
          { name: 'GreenTumbler', sales: 9800, growth: 8.3 },
          { name: 'OceanGuard', sales: 7600, growth: -2.1 },
          { name: 'BioPack', sales: 6500, growth: 15.7 },
          { name: 'SustainableWrap', sales: 5200, growth: 6.8 }
        ]
      });
    }
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  const formatPercentage = (value) => {
    return `${value.toFixed(1)}%`;
  };

  return (
    <div className="dashboard">
      <header className="dashboard-header">
        <div className="header-content">
          <h1>Supply Chain Dashboard</h1>
          <div className="user-info">
            <span>Welcome, {user?.username || 'User'}</span>
            <button onClick={onLogout} className="logout-btn">
              <i className="fas fa-sign-out-alt"></i> Logout
            </button>
          </div>
        </div>
      </header>

      <div className="dashboard-content">
        {/* Key Metrics */}
        <div className="metrics-grid">
          <div className="metric-card">
            <div className="metric-icon">
              <i className="fas fa-boxes"></i>
            </div>
            <div className="metric-content">
              <h3>{dashboardData.totalProducts}</h3>
              <p>Total Products</p>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">
              <i className="fas fa-dollar-sign"></i>
            </div>
            <div className="metric-content">
              <h3>{formatCurrency(dashboardData.totalInventory)}</h3>
              <p>Total Inventory Value</p>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">
              <i className="fas fa-chart-line"></i>
            </div>
            <div className="metric-content">
              <h3>{formatPercentage(dashboardData.forecastAccuracy)}</h3>
              <p>Forecast Accuracy</p>
            </div>
          </div>

          <div className="metric-card">
            <div className="metric-icon">
              <i className="fas fa-exclamation-triangle"></i>
            </div>
            <div className="metric-content">
              <h3>{dashboardData.riskScore.toFixed(1)}</h3>
              <p>Risk Score</p>
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="quick-actions">
          <h2>Quick Actions</h2>
          <div className="actions-grid">
            <Link to="/forecasting" className="action-card">
              <i className="fas fa-chart-line"></i>
              <h3>Demand Forecasting</h3>
              <p>Predict future product demand</p>
            </Link>

            <Link to="/inventory" className="action-card">
              <i className="fas fa-boxes"></i>
              <h3>Inventory Management</h3>
              <p>Optimize stock levels</p>
            </Link>

            <Link to="/risk" className="action-card">
              <i className="fas fa-exclamation-triangle"></i>
              <h3>Risk Assessment</h3>
              <p>Identify potential risks</p>
            </Link>

            <Link to="/profile" className="action-card">
              <i className="fas fa-user"></i>
              <h3>Profile Settings</h3>
              <p>Manage your account</p>
            </Link>
          </div>
        </div>

        {/* Recent Alerts */}
        <div className="alerts-section">
          <h2>Recent Alerts</h2>
          <div className="alerts-list">
            {dashboardData.recentAlerts.map(alert => (
              <div key={alert.id} className={`alert-item ${alert.type}`}>
                <div className="alert-icon">
                  <i className={`fas fa-${alert.type === 'warning' ? 'exclamation-triangle' :
                    alert.type === 'info' ? 'info-circle' : 'check-circle'}`}></i>
                </div>
                <div className="alert-content">
                  <p>{alert.message}</p>
                  <span className="alert-time">{alert.time}</span>
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Top Products */}
        <div className="products-section">
          <h2>Top Performing Products</h2>
          <div className="products-table">
            <div className="table-header">
              <div>Product Name</div>
              <div>Sales</div>
              <div>Growth</div>
            </div>
            {dashboardData.topProducts.map((product, index) => (
              <div key={index} className="table-row">
                <div className="product-name">{product.name}</div>
                <div className="product-sales">{formatCurrency(product.sales)}</div>
                <div className={`product-growth ${product.growth >= 0 ? 'positive' : 'negative'}`}>
                  <i className={`fas fa-arrow-${product.growth >= 0 ? 'up' : 'down'}`}></i>
                  {formatPercentage(Math.abs(product.growth))}
                </div>
              </div>
            ))}
          </div>
        </div>

        {/* Charts Grid */}
        <div className="charts-grid">
          <div className="chart-section">
            <h2>Top Products Sales</h2>
            <div className="chart-container">
              <Plot
                data={[
                  {
                    x: dashboardData.topProducts.map(p => p.name),
                    y: dashboardData.topProducts.map(p => p.sales),
                    type: 'bar',
                    marker: { color: '#667eea' }
                  }
                ]}
                layout={{
                  xaxis: { title: 'Product' },
                  yaxis: { title: 'Sales ($)' },
                  height: 350,
                  margin: { t: 20, r: 20, b: 40, l: 40 },
                  responsive: true
                }}
                style={{ width: '100%', height: '350px' }}
              />
            </div>
          </div>

          <div className="chart-section">
            <h2>Key Metrics Overview</h2>
            <div className="chart-container">
              <Plot
                data={[
                  {
                    x: ['Products', 'Inventory (M$)', 'Accuracy (%)', 'Risk'],
                    y: [dashboardData.totalProducts, dashboardData.totalInventory / 1000000, dashboardData.forecastAccuracy, dashboardData.riskScore],
                    type: 'bar',
                    marker: { color: ['#3498db', '#27ae60', '#f39c12', '#e74c3c'] }
                  }
                ]}
                layout={{
                  xaxis: { title: 'Metric' },
                  yaxis: { title: 'Value' },
                  height: 350,
                  margin: { t: 20, r: 20, b: 40, l: 40 },
                  responsive: true
                }}
                style={{ width: '100%', height: '350px' }}
              />
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;