import React, { useState } from 'react';
import './Profile.css';

const Profile = ({ user, onLogout }) => {
  const [isEditing, setIsEditing] = useState(false);
  const [formData, setFormData] = useState({
    username: user?.username || '',
    email: user?.email || '',
    company: user?.company || '',
    currentPassword: '',
    newPassword: '',
    confirmPassword: ''
  });

  const handleChange = (e) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();

    if (formData.newPassword && formData.newPassword !== formData.confirmPassword) {
      alert('New passwords do not match');
      return;
    }

    try {
      // Mock API call for profile update
      await new Promise(resolve => setTimeout(resolve, 1000));

      alert('Profile updated successfully!');
      setIsEditing(false);
    } catch (error) {
      alert('Error updating profile. Please try again.');
    }
  };

  const handleLogout = () => {
    if (window.confirm('Are you sure you want to logout?')) {
      onLogout();
    }
  };

  return (
    <div className="profile-page">
      <header className="page-header">
        <h1><i className="fas fa-user"></i> User Profile</h1>
        <p>Manage your account settings and preferences</p>
      </header>

      <div className="profile-content">
        {/* Profile Overview */}
        <div className="profile-overview">
          <div className="profile-avatar">
            <i className="fas fa-user-circle"></i>
          </div>
          <div className="profile-info">
            <h2>{user?.username}</h2>
            <p>{user?.email}</p>
            <span className="role-badge">{user?.role || 'User'}</span>
          </div>
          <div className="profile-actions">
            <button
              onClick={() => setIsEditing(!isEditing)}
              className="edit-btn"
            >
              <i className="fas fa-edit"></i>
              {isEditing ? 'Cancel' : 'Edit Profile'}
            </button>
            <button onClick={handleLogout} className="logout-btn">
              <i className="fas fa-sign-out-alt"></i>
              Logout
            </button>
          </div>
        </div>

        {/* Profile Form */}
        <div className="profile-form-container">
          <form onSubmit={handleSubmit} className="profile-form">
            <h3>Account Information</h3>

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
                  disabled={!isEditing}
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
                  disabled={!isEditing}
                  required
                />
              </div>
            </div>

            <div className="form-group">
              <label htmlFor="company">
                <i className="fas fa-building"></i> Company
              </label>
              <input
                type="text"
                id="company"
                name="company"
                value={formData.company}
                onChange={handleChange}
                disabled={!isEditing}
                placeholder="Your company name"
              />
            </div>

            {isEditing && (
              <>
                <h3>Change Password</h3>
                <div className="form-group">
                  <label htmlFor="currentPassword">
                    <i className="fas fa-lock"></i> Current Password
                  </label>
                  <input
                    type="password"
                    id="currentPassword"
                    name="currentPassword"
                    value={formData.currentPassword}
                    onChange={handleChange}
                    placeholder="Enter current password"
                  />
                </div>

                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="newPassword">
                      <i className="fas fa-key"></i> New Password
                    </label>
                    <input
                      type="password"
                      id="newPassword"
                      name="newPassword"
                      value={formData.newPassword}
                      onChange={handleChange}
                      placeholder="Enter new password"
                    />
                  </div>

                  <div className="form-group">
                    <label htmlFor="confirmPassword">
                      <i className="fas fa-key"></i> Confirm Password
                    </label>
                    <input
                      type="password"
                      id="confirmPassword"
                      name="confirmPassword"
                      value={formData.confirmPassword}
                      onChange={handleChange}
                      placeholder="Confirm new password"
                    />
                  </div>
                </div>
              </>
            )}

            {isEditing && (
              <div className="form-actions">
                <button type="submit" className="save-btn">
                  <i className="fas fa-save"></i>
                  Save Changes
                </button>
                <button
                  type="button"
                  onClick={() => setIsEditing(false)}
                  className="cancel-btn"
                >
                  <i className="fas fa-times"></i>
                  Cancel
                </button>
              </div>
            )}
          </form>
        </div>

        {/* Account Statistics */}
        <div className="account-stats">
          <h3>Account Statistics</h3>
          <div className="stats-grid">
            <div className="stat-card">
              <div className="stat-icon">
                <i className="fas fa-chart-line"></i>
              </div>
              <div className="stat-content">
                <h4>Forecasts Run</h4>
                <span className="stat-value">24</span>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">
                <i className="fas fa-boxes"></i>
              </div>
              <div className="stat-content">
                <h4>Inventory Analyses</h4>
                <span className="stat-value">18</span>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">
                <i className="fas fa-exclamation-triangle"></i>
              </div>
              <div className="stat-content">
                <h4>Risk Assessments</h4>
                <span className="stat-value">12</span>
              </div>
            </div>

            <div className="stat-card">
              <div className="stat-icon">
                <i className="fas fa-calendar-alt"></i>
              </div>
              <div className="stat-content">
                <h4>Member Since</h4>
                <span className="stat-value">Jan 2024</span>
              </div>
            </div>
          </div>
        </div>

        {/* Recent Activity */}
        <div className="recent-activity">
          <h3>Recent Activity</h3>
          <div className="activity-list">
            <div className="activity-item">
              <div className="activity-icon">
                <i className="fas fa-chart-line"></i>
              </div>
              <div className="activity-content">
                <p>Ran demand forecast for EcoBottle Pro</p>
                <span className="activity-time">2 hours ago</span>
              </div>
            </div>

            <div className="activity-item">
              <div className="activity-icon">
                <i className="fas fa-boxes"></i>
              </div>
              <div className="activity-content">
                <p>Optimized inventory levels</p>
                <span className="activity-time">1 day ago</span>
              </div>
            </div>

            <div className="activity-item">
              <div className="activity-icon">
                <i className="fas fa-exclamation-triangle"></i>
              </div>
              <div className="activity-content">
                <p>Completed risk assessment</p>
                <span className="activity-time">3 days ago</span>
              </div>
            </div>

            <div className="activity-item">
              <div className="activity-icon">
                <i className="fas fa-user"></i>
              </div>
              <div className="activity-content">
                <p>Updated profile information</p>
                <span className="activity-time">1 week ago</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Profile;