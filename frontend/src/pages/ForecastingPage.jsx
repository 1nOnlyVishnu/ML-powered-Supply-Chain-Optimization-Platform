import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import './ForecastingPage.css';

const ForecastingPage = ({ user }) => {
  const [uploadedFile, setUploadedFile] = useState(null);
  const [forecastData, setForecastData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [selectedModel, setSelectedModel] = useState('xgboost');
  const [forecastPeriod, setForecastPeriod] = useState(30);
  const [selectedProduct, setSelectedProduct] = useState('');
  const [products, setProducts] = useState([]);

  const handleFileUpload = (event) => {
    const file = event.target.files[0];
    if (file && file.type === 'text/csv') {
      setUploadedFile(file);
      // Parse CSV to get product list
      const reader = new FileReader();
      reader.onload = (e) => {
        const csv = e.target.result;
        const lines = csv.split('\n');
        if (lines.length > 1) {
          const headers = lines[0].split(',');
          const productIndex = headers.findIndex(h => h.toLowerCase().includes('product'));
          if (productIndex !== -1) {
            const uniqueProducts = [...new Set(
              lines.slice(1)
                .filter(line => line.trim())
                .map(line => line.split(',')[productIndex])
                .filter(product => product && product.trim())
            )];
            setProducts(uniqueProducts);
          }
        }
      };
      reader.readAsText(file);
    }
  };

  const runForecast = async () => {
    if (!uploadedFile) {
      alert('Please upload a CSV file first');
      return;
    }

    setLoading(true);
    try {
      const formData = new FormData();
      formData.append('file', uploadedFile);
      if (selectedProduct) {
        formData.append('product', selectedProduct);
      }
      formData.append('periods', forecastPeriod.toString());

      const response = await fetch('http://localhost:8000/api/forecast', {
        method: 'POST',
        body: formData,
        headers: {
          'Authorization': `Bearer ${localStorage.getItem('token')}`
        }
      });

      if (response.ok) {
        const data = await response.json();
        setForecastData(data);
      } else {
        const errorData = await response.json();
        alert(`Error: ${errorData.detail || 'Error running forecast. Please try again.'}`);
      }
    } catch (error) {
      console.error('Forecast error:', error);
      alert('Error running forecast. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const exportResults = () => {
    if (!forecastData) return;

    const csvContent = [
      'Date,P10,P50,P90',
      ...forecastData.dates.map((date, i) => [
        date,
        forecastData.p10[i],
        forecastData.p50[i],
        forecastData.p90[i]
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `forecast_results_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="forecasting-page">
      <header className="page-header">
        <h1><i className="fas fa-chart-line"></i> Demand Forecasting</h1>
        <p>Advanced AI-powered demand prediction using XGBoost and Prophet models</p>
      </header>

      <div className="forecasting-content">
        {/* File Upload Section */}
        <div className="upload-section">
          <h2><i className="fas fa-cloud-upload-alt"></i> Upload Data</h2>
          <div className="upload-area">
            <input
              type="file"
              accept=".csv"
              onChange={handleFileUpload}
              id="file-upload"
              className="file-input"
            />
            <label htmlFor="file-upload" className="upload-label">
              <i className="fas fa-file-csv"></i>
              <span>{uploadedFile ? uploadedFile.name : 'Choose CSV file'}</span>
            </label>
            {uploadedFile && (
              <div className="file-info">
                <i className="fas fa-check-circle"></i>
                <span>{uploadedFile.name} ({(uploadedFile.size / 1024).toFixed(1)} KB)</span>
              </div>
            )}
          </div>
        </div>

        {/* Configuration Section */}
        <div className="config-section">
          <h2><i className="fas fa-cogs"></i> Configuration</h2>
          <div className="config-grid">
            <div className="config-item">
              <label>ML Model</label>
              <select
                value={selectedModel}
                onChange={(e) => setSelectedModel(e.target.value)}
                className="model-select"
              >
                <option value="xgboost">XGBoost</option>
                <option value="prophet">Prophet</option>
                <option value="ensemble">Ensemble (XGBoost + Prophet)</option>
              </select>
            </div>

            <div className="config-item">
              <label>Forecast Period (Days)</label>
              <input
                type="number"
                min="7"
                max="90"
                value={forecastPeriod}
                onChange={(e) => setForecastPeriod(parseInt(e.target.value))}
                className="period-input"
              />
            </div>

            {products.length > 0 && (
              <div className="config-item">
                <label>Product Filter (Optional)</label>
                <select
                  value={selectedProduct}
                  onChange={(e) => setSelectedProduct(e.target.value)}
                  className="product-select"
                >
                  <option value="">All Products</option>
                  {products.map(product => (
                    <option key={product} value={product}>{product}</option>
                  ))}
                </select>
              </div>
            )}
          </div>

          <button
            onClick={runForecast}
            disabled={!uploadedFile || loading}
            className="forecast-btn"
          >
            {loading ? (
              <>
                <i className="fas fa-spinner fa-spin"></i>
                Running Forecast...
              </>
            ) : (
              <>
                <i className="fas fa-play"></i>
                Run Forecast
              </>
            )}
          </button>
        </div>

        {/* Results Section */}
        {forecastData && (
          <div className="results-section">
            <div className="results-header">
              <h2><i className="fas fa-chart-bar"></i> Forecast Results</h2>
              <button onClick={exportResults} className="export-btn">
                <i className="fas fa-download"></i>
                Export CSV
              </button>
            </div>

            {/* Key Metrics */}
            <div className="metrics-grid">
              <div className="metric-card">
                <h4>Forecast Period</h4>
                <span className="metric-value">{forecastData.dates.length} days</span>
              </div>
              <div className="metric-card">
                <h4>Average Demand</h4>
                <span className="metric-value">
                  {forecastData.p50.reduce((a, b) => a + b, 0) / forecastData.p50.length}
                </span>
              </div>
              <div className="metric-card">
                <h4>Peak Demand</h4>
                <span className="metric-value">{Math.max(...forecastData.p50)}</span>
              </div>
              <div className="metric-card">
                <h4>Model Used</h4>
                <span className="metric-value">{forecastData.meta?.baseline_model || selectedModel}</span>
              </div>
            </div>

            {/* Forecast Chart */}
            <div className="chart-container">
              <Plot
                data={[
                  {
                    x: forecastData.dates,
                    y: forecastData.p10,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'P10 (10th percentile)',
                    line: { color: '#e74c3c', dash: 'dot' }
                  },
                  {
                    x: forecastData.dates,
                    y: forecastData.p50,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'P50 (Median)',
                    line: { color: '#3498db', width: 3 }
                  },
                  {
                    x: forecastData.dates,
                    y: forecastData.p90,
                    type: 'scatter',
                    mode: 'lines',
                    name: 'P90 (90th percentile)',
                    line: { color: '#e74c3c', dash: 'dot' }
                  }
                ]}
                layout={{
                  title: 'Demand Forecast with Confidence Intervals',
                  xaxis: { title: 'Date' },
                  yaxis: { title: 'Demand Quantity' },
                  showlegend: true,
                  height: 500,
                  margin: { t: 50, r: 50, b: 50, l: 50 }
                }}
                style={{ width: '100%', height: '500px' }}
              />
            </div>

            {/* Forecast Table */}
            <div className="forecast-table">
              <h3>Forecast Details</h3>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>Date</th>
                      <th>P10</th>
                      <th>P50 (Median)</th>
                      <th>P90</th>
                      <th>Range</th>
                    </tr>
                  </thead>
                  <tbody>
                    {forecastData.dates.slice(0, 10).map((date, i) => (
                      <tr key={i}>
                        <td>{date}</td>
                        <td>{forecastData.p10[i].toFixed(1)}</td>
                        <td>{forecastData.p50[i].toFixed(1)}</td>
                        <td>{forecastData.p90[i].toFixed(1)}</td>
                        <td>{(forecastData.p90[i] - forecastData.p10[i]).toFixed(1)}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
                {forecastData.dates.length > 10 && (
                  <p className="table-note">
                    Showing first 10 days. Export full results for complete data.
                  </p>
                )}
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ForecastingPage;