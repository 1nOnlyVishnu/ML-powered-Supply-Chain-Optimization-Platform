import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Auth.css';

const Login = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');

    try {
      const response = await fetch('http://localhost:8000/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          username: formData.username,
          password: formData.password
        })
      });

      if (response.ok) {
        const data = await response.json();
        onLogin(data.user, data.access_token);
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Login failed. Please try again.');
      }
    } catch (err) {
      setError('Network error. Please check your connection.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1><i className="fas fa-cogs"></i> Supply Chain Management</h1>
          <p>Advanced AI-powered platform for supply chain optimization</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <h2>Sign In</h2>

          {error && (
            <div className="error-message">
              <i className="fas fa-exclamation-triangle"></i>
              {error}
            </div>
          )}

          <div className="form-group">
            <label htmlFor="username">
              <i className="fas fa-user"></i> Username
            </label>
            <input
              type="text"
              id="username"
              name="username"
              value={formData.username}
              onChange={handleChange}
              placeholder="Enter your username"
              required
            />
          </div>

          <div className="form-group">
            <label htmlFor="password">
              <i className="fas fa-lock"></i> Password
            </label>
            <input
              type="password"
              id="password"
              name="password"
              value={formData.password}
              onChange={handleChange}
              placeholder="Enter your password"
              required
            />
          </div>

          <button
            type="submit"
            className="auth-btn"
            disabled={loading}
          >
            {loading ? (
              <>
                <i className="fas fa-spinner fa-spin"></i>
                Signing In...
              </>
            ) : (
              <>
                <i className="fas fa-sign-in-alt"></i>
                Sign In
              </>
            )}
          </button>
        </form>

        <div className="auth-footer">
          <p>Demo Credentials:</p>
          <div className="demo-credentials">
            <div><strong>Admin:</strong> admin / admin123</div>
            <div><strong>User:</strong> user / user123</div>
          </div>

          <p>
            Don't have an account?
            <Link to="/signup" className="auth-link"> Sign up here</Link>
          </p>
        </div>
      </div>

      <div className="auth-features">
        <div className="feature">
          <i className="fas fa-chart-line"></i>
          <h3>Demand Forecasting</h3>
          <p>AI-powered demand prediction using XGBoost and Prophet</p>
        </div>
        <div className="feature">
          <i className="fas fa-boxes"></i>
          <h3>Inventory Optimization</h3>
          <p>Smart inventory management with EOQ and safety stock</p>
        </div>
        <div className="feature">
          <i className="fas fa-exclamation-triangle"></i>
          <h3>Risk Assessment</h3>
          <p>Advanced risk prediction with machine learning models</p>
        </div>
      </div>
    </div>
  );
};

export default Login;