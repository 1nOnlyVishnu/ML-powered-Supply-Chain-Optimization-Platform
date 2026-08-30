import React, { useState, useEffect } from 'react';
import Plot from 'react-plotly.js';
import './InventoryPage.css';

const InventoryPage = ({ user }) => {
  const [inventoryData, setInventoryData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [serviceLevel, setServiceLevel] = useState(95);
  const [leadTime, setLeadTime] = useState(14);
  const [holdingCost, setHoldingCost] = useState(2.0);
  const [orderingCost, setOrderingCost] = useState(50.0);

  useEffect(() => {
    // Load sample inventory data
    loadSampleData();
  }, []);

  const loadSampleData = () => {
    const sampleData = [
      {
        sku: 'ECO001',
        product: 'EcoBottle Pro',
        avg_daily_demand: 85,
        std_daily_demand: 15,
        current_stock: 1200,
        unit_cost: 12.50
      },
      {
        sku: 'GRE001',
        product: 'GreenTumbler',
        avg_daily_demand: 65,
        std_daily_demand: 12,
        current_stock: 800,
        unit_cost: 18.75
      },
      {
        sku: 'OCE001',
        product: 'OceanGuard',
        avg_daily_demand: 45,
        std_daily_demand: 10,
        current_stock: 600,
        unit_cost: 25.00
      },
      {
        sku: 'BIO001',
        product: 'BioPack',
        avg_daily_demand: 35,
        std_daily_demand: 8,
        current_stock: 400,
        unit_cost: 15.50
      },
      {
        sku: 'SUS001',
        product: 'SustainableWrap',
        avg_daily_demand: 55,
        std_daily_demand: 11,
        current_stock: 750,
        unit_cost: 8.25
      }
    ];
    setInventoryData(sampleData);
  };

  const calculateEOQ = (demand, orderingCost, holdingCost) => {
    if (demand <= 0 || orderingCost <= 0 || holdingCost <= 0) return 0;
    return Math.sqrt((2 * demand * orderingCost) / holdingCost);
  };

  const calculateSafetyStock = (stdDemand, leadTime, serviceLevel) => {
    const z = serviceLevel === 95 ? 1.645 : serviceLevel === 99 ? 2.326 : 1.281;
    return z * stdDemand * Math.sqrt(leadTime);
  };

  const calculateReorderPoint = (avgDemand, leadTime, safetyStock) => {
    return avgDemand * leadTime + safetyStock;
  };

  const optimizeInventory = () => {
    if (!inventoryData) return;

    setLoading(true);

    const optimized = inventoryData.map(item => {
      const annualDemand = item.avg_daily_demand * 365;
      const eoq = calculateEOQ(annualDemand, orderingCost, holdingCost);
      const safetyStock = calculateSafetyStock(item.std_daily_demand, leadTime, serviceLevel);
      const reorderPoint = calculateReorderPoint(item.avg_daily_demand, leadTime, safetyStock);

      const daysOfInventory = item.current_stock / item.avg_daily_demand;
      const stockStatus = daysOfInventory < 7 ? 'Critical' :
                         daysOfInventory < 14 ? 'Low' :
                         daysOfInventory > 60 ? 'Overstock' : 'Optimal';

      return {
        ...item,
        eoq: Math.round(eoq),
        safetyStock: Math.round(safetyStock),
        reorderPoint: Math.round(reorderPoint),
        daysOfInventory: Math.round(daysOfInventory),
        stockStatus,
        suggestedOrder: Math.max(0, Math.round(reorderPoint - item.current_stock))
      };
    });

    setTimeout(() => {
      setInventoryData(optimized);
      setLoading(false);
    }, 1000);
  };

  const exportResults = () => {
    if (!inventoryData) return;

    const csvContent = [
      'SKU,Product,Avg_Daily_Demand,Current_Stock,EOQ,Safety_Stock,Reorder_Point,Days_of_Inventory,Stock_Status,Suggested_Order',
      ...inventoryData.map(item => [
        item.sku,
        item.product,
        item.avg_daily_demand,
        item.current_stock,
        item.eoq || '',
        item.safetyStock || '',
        item.reorderPoint || '',
        item.daysOfInventory || '',
        item.stockStatus || '',
        item.suggestedOrder || ''
      ].join(','))
    ].join('\n');

    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `inventory_optimization_${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    window.URL.revokeObjectURL(url);
  };

  const getStatusColor = (status) => {
    switch (status) {
      case 'Critical': return '#e74c3c';
      case 'Low': return '#f39c12';
      case 'Optimal': return '#27ae60';
      case 'Overstock': return '#8e44ad';
      default: return '#95a5a6';
    }
  };

  return (
    <div className="inventory-page">
      <header className="page-header">
        <h1><i className="fas fa-boxes"></i> Inventory Optimization</h1>
        <p>Smart inventory management with EOQ, safety stock, and reorder point calculations</p>
      </header>

      <div className="inventory-content">
        {/* Configuration Panel */}
        <div className="config-panel">
          <h2><i className="fas fa-sliders-h"></i> Optimization Parameters</h2>
          <div className="config-grid">
            <div className="config-item">
              <label>Service Level (%)</label>
              <select
                value={serviceLevel}
                onChange={(e) => setServiceLevel(Number(e.target.value))}
              >
                <option value={90}>90%</option>
                <option value={95}>95%</option>
                <option value={99}>99%</option>
              </select>
            </div>

            <div className="config-item">
              <label>Lead Time (Days)</label>
              <input
                type="number"
                min="1"
                max="90"
                value={leadTime}
                onChange={(e) => setLeadTime(Number(e.target.value))}
              />
            </div>

            <div className="config-item">
              <label>Holding Cost (% of unit cost)</label>
              <input
                type="number"
                min="0.1"
                max="10"
                step="0.1"
                value={holdingCost}
                onChange={(e) => setHoldingCost(Number(e.target.value))}
              />
            </div>

            <div className="config-item">
              <label>Ordering Cost ($)</label>
              <input
                type="number"
                min="1"
                max="500"
                value={orderingCost}
                onChange={(e) => setOrderingCost(Number(e.target.value))}
              />
            </div>
          </div>

          <div className="action-buttons">
            <button onClick={optimizeInventory} disabled={loading} className="optimize-btn">
              {loading ? (
                <>
                  <i className="fas fa-spinner fa-spin"></i>
                  Optimizing...
                </>
              ) : (
                <>
                  <i className="fas fa-calculator"></i>
                  Run Optimization
                </>
              )}
            </button>

            <button onClick={exportResults} className="export-btn">
              <i className="fas fa-download"></i>
              Export Results
            </button>
          </div>
        </div>

        {/* Results Section */}
        {inventoryData && (
          <div className="results-section">
            {/* Summary Cards */}
            <div className="summary-cards">
              <div className="summary-card">
                <h4>Total Products</h4>
                <span className="summary-value">{inventoryData.length}</span>
              </div>

              <div className="summary-card">
                <h4>Critical Stock</h4>
                <span className="summary-value critical">
                  {inventoryData.filter(item => item.stockStatus === 'Critical').length}
                </span>
              </div>

              <div className="summary-card">
                <h4>Low Stock</h4>
                <span className="summary-value warning">
                  {inventoryData.filter(item => item.stockStatus === 'Low').length}
                </span>
              </div>

              <div className="summary-card">
                <h4>Optimal Stock</h4>
                <span className="summary-value success">
                  {inventoryData.filter(item => item.stockStatus === 'Optimal').length}
                </span>
              </div>
            </div>

            {/* Inventory Status Chart */}
            <div className="chart-container">
              <Plot
                data={[{
                  type: 'pie',
                  labels: ['Critical', 'Low', 'Optimal', 'Overstock'],
                  values: [
                    inventoryData.filter(item => item.stockStatus === 'Critical').length,
                    inventoryData.filter(item => item.stockStatus === 'Low').length,
                    inventoryData.filter(item => item.stockStatus === 'Optimal').length,
                    inventoryData.filter(item => item.stockStatus === 'Overstock').length
                  ],
                  marker: {
                    colors: ['#e74c3c', '#f39c12', '#27ae60', '#8e44ad']
                  }
                }]}
                layout={{
                  title: 'Inventory Status Distribution',
                  height: 400,
                  margin: { t: 50, r: 50, b: 50, l: 50 }
                }}
                style={{ width: '100%', height: '400px' }}
              />
            </div>

            {/* Inventory Table */}
            <div className="inventory-table">
              <h3>Inventory Optimization Results</h3>
              <div className="table-container">
                <table>
                  <thead>
                    <tr>
                      <th>SKU</th>
                      <th>Product</th>
                      <th>Current Stock</th>
                      <th>Daily Demand</th>
                      <th>EOQ</th>
                      <th>Safety Stock</th>
                      <th>Reorder Point</th>
                      <th>Days of Inventory</th>
                      <th>Status</th>
                      <th>Suggested Order</th>
                    </tr>
                  </thead>
                  <tbody>
                    {inventoryData.map((item, index) => (
                      <tr key={index}>
                        <td>{item.sku}</td>
                        <td>{item.product}</td>
                        <td>{item.current_stock}</td>
                        <td>{item.avg_daily_demand}</td>
                        <td>{item.eoq || '-'}</td>
                        <td>{item.safetyStock || '-'}</td>
                        <td>{item.reorderPoint || '-'}</td>
                        <td>{item.daysOfInventory || '-'}</td>
                        <td>
                          <span
                            className="status-badge"
                            style={{ backgroundColor: getStatusColor(item.stockStatus) }}
                          >
                            {item.stockStatus || 'Not Calculated'}
                          </span>
                        </td>
                        <td>{item.suggestedOrder || '-'}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>

            {/* Recommendations */}
            <div className="recommendations">
              <h3><i className="fas fa-lightbulb"></i> Recommendations</h3>
              <div className="recommendations-list">
                {inventoryData.filter(item => item.stockStatus === 'Critical').length > 0 && (
                  <div className="recommendation critical">
                    <i className="fas fa-exclamation-triangle"></i>
                    <span>URGENT: {inventoryData.filter(item => item.stockStatus === 'Critical').length} products are critically low. Order immediately.</span>
                  </div>
                )}

                {inventoryData.filter(item => item.stockStatus === 'Low').length > 0 && (
                  <div className="recommendation warning">
                    <i className="fas fa-exclamation-circle"></i>
                    <span>WARNING: {inventoryData.filter(item => item.stockStatus === 'Low').length} products are running low. Plan reordering.</span>
                  </div>
                )}

                {inventoryData.filter(item => item.stockStatus === 'Overstock').length > 0 && (
                  <div className="recommendation info">
                    <i className="fas fa-info-circle"></i>
                    <span>INFO: {inventoryData.filter(item => item.stockStatus === 'Overstock').length} products are overstocked. Consider promotions or redistribution.</span>
                  </div>
                )}

                <div className="recommendation success">
                  <i className="fas fa-check-circle"></i>
                  <span>SUCCESS: {inventoryData.filter(item => item.stockStatus === 'Optimal').length} products are optimally stocked.</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default InventoryPage;