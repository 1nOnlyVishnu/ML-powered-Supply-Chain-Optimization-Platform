import React, { useState } from 'react';
import { Link } from 'react-router-dom';
import './Auth.css';

const Signup = ({ onLogin }) => {
  const [formData, setFormData] = useState({
    username: '',
    email: '',
    password: '',
    confirmPassword: '',
    company: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const [success, setSuccess] = useState(false);

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

    // Validation
    if (formData.password !== formData.confirmPassword) {
      setError('Passwords do not match');
      setLoading(false);
      return;
    }

    if (formData.password.length < 6) {
      setError('Password must be at least 6 characters long');
      setLoading(false);
      return;
    }

    try {
      // Mock registration - replace with real API call
      await new Promise(resolve => setTimeout(resolve, 1500));

      // Mock successful registration and auto-login
      const userData = {
        id: Date.now(),
        username: formData.username,
        email: formData.email,
        company: formData.company,
        role: 'user'
      };
      const token = 'mock-jwt-token-' + Date.now();

      setSuccess(true);
      setTimeout(() => {
        onLogin(userData, token);
      }, 1000);

    } catch (err) {
      setError('Registration failed. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  if (success) {
    return (
      <div className="auth-container">
        <div className="auth-card success-card">
          <div className="success-icon">
            <i className="fas fa-check-circle"></i>
          </div>
          <h2>Registration Successful!</h2>
          <p>Welcome to Supply Chain Management System</p>
          <p>Redirecting to dashboard...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="auth-container">
      <div className="auth-card">
        <div className="auth-header">
          <h1><i className="fas fa-cogs"></i> Supply Chain Management</h1>
          <p>Join thousands of businesses optimizing their supply chains</p>
        </div>

        <form onSubmit={handleSubmit} className="auth-form">
          <h2>Create Account</h2>

          {error && (
            <div className="error-message">
              <i className="fas fa-exclamation-triangle"></i>
              {error}
            </div>
          )}

          <div className="form-row">
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
                placeholder="Choose a username"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="email">
                <i className="fas fa-envelope"></i> Email
              </label>
              <input
                type="email"
                id="email"
                name="email"
                value={formData.email}
                onChange={handleChange}
                placeholder="Enter your email"
                required
              />
            </div>
          </div>

          <div className="form-group">
            <label htmlFor="company">
              <i className="fas fa-building"></i> Company (Optional)
            </label>
            <input
              type="text"
              id="company"
              name="company"
              value={formData.company}
              onChange={handleChange}
              placeholder="Your company name"
            />
          </div>

          <div className="form-row">
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
                placeholder="Create a password"
                required
              />
            </div>

            <div className="form-group">
              <label htmlFor="confirmPassword">
                <i className="fas fa-lock"></i> Confirm Password
              </label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                value={formData.confirmPassword}
                onChange={handleChange}
                placeholder="Confirm your password"
                required
              />
            </div>
          </div>

          <button
            type="submit"
            className="auth-btn"
            disabled={loading}
          >
            {loading ? (
              <>
                <i className="fas fa-spinner fa-spin"></i>
                Creating Account...
              </>
            ) : (
              <>
                <i className="fas fa-user-plus"></i>
                Create Account
              </>
            )}
          </button>
        </form>

        <div className="auth-footer">
          <p>
            Already have an account?
            <Link to="/login" className="auth-link"> Sign in here</Link>
          </p>
        </div>
      </div>

      <div className="auth-benefits">
        <h3>Why Choose Our Platform?</h3>
        <div className="benefits-list">
          <div className="benefit">
            <i className="fas fa-brain"></i>
            <span>AI-Powered Analytics</span>
          </div>
          <div className="benefit">
            <i className="fas fa-shield-alt"></i>
            <span>Enterprise Security</span>
          </div>
          <div className="benefit">
            <i className="fas fa-chart-line"></i>
            <span>Real-time Insights</span>
          </div>
          <div className="benefit">
            <i className="fas fa-users"></i>
            <span>24/7 Support</span>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Signup;