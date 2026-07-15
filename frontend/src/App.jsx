import React, { useState, useRef } from 'react';
import { 
  UploadCloud, 
  FileSpreadsheet, 
  CheckCircle2, 
  Settings, 
  Database, 
  ArrowUpDown, 
  Download, 
  CloudLightning, 
  Loader2, 
  Plus, 
  Trash2, 
  Save, 
  Info,
  Edit2,
  RefreshCw,
  FileCode
} from 'lucide-react';

const API_BASE = '';

function App() {
  // File Upload States
  const [file, setFile] = useState(null);
  const [dragActive, setDragActive] = useState(false);
  const [parsing, setParsing] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  
  // Parsed Statement Data
  const [parsedData, setParsedData] = useState(null);
  const [clientName, setClientName] = useState('');
  const [bankName, setBankName] = useState('');
  const [accountSuffix, setAccountSuffix] = useState('');
  const [isEditingMetadata, setIsEditingMetadata] = useState(false);
  
  // Mapping States
  const [columnMapping, setColumnMapping] = useState({
    date: 'Date',
    description: 'Description',
    debit: 'Debit',
    credit: 'Credit',
    amount: 'Signed Amount'
  });
  
  const [columnSequence, setColumnSequence] = useState([
    'Date', 'Description', 'Debit', 'Credit'
  ]);
  
  const [autoApplied, setAutoApplied] = useState(false);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const [savingConfig, setSavingConfig] = useState(false);
  
  // Export/Sync States
  const [exportingExcel, setExportingExcel] = useState(false);
  const [exportingIIF, setExportingIIF] = useState(false);
  const [syncingERP, setSyncingERP] = useState(false);
  const [erpSystem, setErpSystem] = useState('qbo'); // qbo, netsuite, xero, zoho
  const [erpStatus, setErpStatus] = useState(null);
  const [erpSuccess, setErpSuccess] = useState(false);
  
  const [targetAccounts, setTargetAccounts] = useState({
    bank_account: '1010 Cash in Bank',
    suspense_account: '6000 Uncategorized Transactions'
  });

  const fileInputRef = useRef(null);

  // Drag and drop handlers
  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFile(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      processFile(e.target.files[0]);
    }
  };

  const processFile = async (selectedFile) => {
    setFile(selectedFile);
    setParsing(true);
    setErrorMessage('');
    setParsedData(null);
    setAutoApplied(false);
    setErpStatus(null);
    
    const formData = new FormData();
    formData.append('file', selectedFile);
    
    try {
      const response = await fetch(`${API_BASE}/api/upload`, {
        method: 'POST',
        body: formData,
      });
      
      const result = await response.json();
      
      if (result.success) {
        setParsedData(result);
        setClientName(result.client_name);
        setBankName(result.bank_name);
        setAccountSuffix(result.account_number_suffix);
        
        // Auto-apply saved configuration if it exists
        if (result.saved_config) {
          setColumnMapping(result.saved_config.column_mapping);
          setColumnSequence(result.saved_config.column_sequence);
          setAutoApplied(true);
        } else {
          // Default configs
          const defaultMapping = {
            date: 'Date',
            description: 'Description',
            debit: 'Debit',
            credit: 'Credit',
            amount: 'Signed Amount'
          };
          setColumnMapping(defaultMapping);
          setColumnSequence(['Date', 'Description', 'Debit', 'Credit']);
        }
      } else {
        setErrorMessage(result.message || result.detail || 'Error parsing statement');
      }
    } catch (err) {
      setErrorMessage('Could not connect to the backend server. Make sure FastAPI is running on port 8000.');
      console.error(err);
    } finally {
      setParsing(false);
    }
  };

  // Columns Mapping Helpers
  const handleMapChange = (key, value) => {
    const oldVal = columnMapping[key];
    const newMapping = { ...columnMapping, [key]: value };
    setColumnMapping(newMapping);
    
    // Update column sequence by replacing old custom header with new one
    let newSeq = [...columnSequence];
    if (oldVal && newSeq.includes(oldVal)) {
      newSeq = newSeq.map(col => col === oldVal ? value : col);
    } else if (value && !newSeq.includes(value)) {
      newSeq.push(value);
    }
    // Remove blank mapping entries from sequence
    setColumnSequence(newSeq.filter(col => col !== ''));
  };

  const handleToggleColumn = (key) => {
    const customHeader = columnMapping[key];
    if (!customHeader) return;
    
    if (columnSequence.includes(customHeader)) {
      setColumnSequence(columnSequence.filter(col => col !== customHeader));
    } else {
      setColumnSequence([...columnSequence, customHeader]);
    }
  };

  const moveColumn = (index, direction) => {
    const newSeq = [...columnSequence];
    const targetIndex = index + direction;
    if (targetIndex < 0 || targetIndex >= newSeq.length) return;
    
    // Swap
    const temp = newSeq[index];
    newSeq[index] = newSeq[targetIndex];
    newSeq[targetIndex] = temp;
    setColumnSequence(newSeq);
  };

  // Save Config Trigger
  const saveMappingConfig = async () => {
    setSavingConfig(true);
    setSaveSuccess(false);
    try {
      const response = await fetch(`${API_BASE}/api/save-config`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          client_name: clientName,
          bank_name: bankName,
          account_number_suffix: accountSuffix,
          column_mapping: columnMapping,
          column_sequence: columnSequence
        })
      });
      const res = await response.json();
      if (res.success) {
        setSaveSuccess(true);
        setTimeout(() => setSaveSuccess(false), 3000);
      }
    } catch (err) {
      console.error("Failed to save config", err);
    } finally {
      setSavingConfig(false);
    }
  };

  // Exports Triggers
  const exportExcel = async () => {
    if (!parsedData) return;
    setExportingExcel(true);
    try {
      const response = await fetch(`${API_BASE}/api/export-excel`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transactions: parsedData.transactions,
          column_mapping: columnMapping,
          column_sequence: columnSequence
        })
      });
      
      if (!response.ok) {
        const errorText = await response.text();
        alert(`Failed to export Excel: ${errorText}`);
        return;
      }
      
      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `${clientName.replace(/\s+/g, '_')}_${bankName}_Converted.xlsx`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      console.error(err);
      alert(`Error exporting Excel: ${err.message}`);
    } finally {
      setExportingExcel(false);
    }
  };

  const exportIIF = async () => {
    if (!parsedData) return;
    setExportingIIF(true);
    try {
      const response = await fetch(`${API_BASE}/api/export-iif`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          transactions: parsedData.transactions,
          bank_account_name: targetAccounts.bank_account,
          offset_account_name: targetAccounts.suspense_account
        })
      });
      
      const text = await response.text();
      const blob = new Blob([text], { type: 'text/plain' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = `QB_Desktop_Import_${accountSuffix}.iif`;
      document.body.appendChild(a);
      a.click();
      a.remove();
    } catch (err) {
      console.error(err);
    } finally {
      setExportingIIF(false);
    }
  };

  // ERP Sync Trigger
  const syncERP = async () => {
    if (!parsedData) return;
    setSyncingERP(true);
    setErpStatus(null);
    try {
      const response = await fetch(`${API_BASE}/api/sync-erp`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          system_name: erpSystem,
          transactions: parsedData.transactions,
          target_accounts: {
            bank_account: targetAccounts.bank_account,
            suspense_account: targetAccounts.suspense_account
          }
        })
      });
      const res = await response.json();
      setErpSuccess(res.success);
      if (res.success) {
        setErpStatus(res.message + (res.simulated ? " (SIMULATED)" : ""));
      } else {
        setErpStatus("Error syncing transactions: " + res.message);
      }
    } catch (err) {
      setErpSuccess(false);
      setErpStatus("Failed to make request to the backend integration handler.");
      console.error(err);
    } finally {
      setSyncingERP(false);
    }
  };

  return (
    <div className="workspace-layout">
      {/* Left Sidebar */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <Database size={22} style={{ color: 'var(--primary)' }} />
          <span>StatementFlow</span>
        </div>
        
        <nav className="sidebar-nav">
          <div className="sidebar-link active">
            <UploadCloud size={18} />
            <span>Converter Workspace</span>
          </div>
          <div className="sidebar-link" style={{ opacity: 0.5, cursor: 'not-allowed' }} title="Coming soon">
            <Settings size={18} />
            <span>Connection Settings</span>
          </div>
        </nav>
        
        <div className="sidebar-footer">
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'flex', flexDirection: 'column', gap: '4px' }}>
            <span style={{ fontWeight: 500 }}>Active Extraction Engine</span>
            <div style={{ display: 'flex', alignItems: 'center', gap: '6px', fontWeight: 600, color: 'var(--secondary)', marginTop: '2px' }}>
              <span style={{ width: '6px', height: '6px', borderRadius: '50%', background: '#10b981', display: 'inline-block' }}></span>
              {parsedData?.is_mock ? 'Mock Fallback Mode' : 'Local Extraction Active'}
            </div>
          </div>
        </div>
      </aside>

      {/* Main Panel */}
      <main className="main-content">
        <header className="top-bar">
          <h2>Bank & Card Statement Converter</h2>
          <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
            <span className="badge badge-primary">Enterprise Portal</span>
          </div>
        </header>

        <div className="app-container fade-in">
          <div style={{ display: 'grid', gridTemplateColumns: '1.1fr 2fr', gap: '32px', alignItems: 'start' }}>
            
            {/* Left Column Controls */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
              
              {/* File Upload Panel */}
              <div className="card-panel" style={{ padding: '24px' }}>
                <h3 style={{ fontFamily: 'var(--font-display)', marginBottom: '16px', fontSize: '1rem', fontWeight: 600, color: 'var(--secondary)' }}>
                  1. Upload Statement
                </h3>
                
                <div 
                  className={`drag-area ${dragActive ? 'active' : ''}`}
                  onDragEnter={handleDrag}
                  onDragLeave={handleDrag}
                  onDragOver={handleDrag}
                  onDrop={handleDrop}
                  onClick={() => fileInputRef.current.click()}
                >
                  <input 
                    ref={fileInputRef}
                    type="file"
                    onChange={handleFileChange}
                    accept=".pdf,.png,.jpg,.jpeg,.webp"
                    style={{ display: 'none' }}
                  />
                  <UploadCloud size={40} style={{ color: 'var(--primary)' }} />
                  <div>
                    <p style={{ fontWeight: 600, fontSize: '0.875rem', color: 'var(--secondary)' }}>Drag & drop statement file here</p>
                    <p style={{ color: 'var(--text-muted)', fontSize: '0.75rem', marginTop: '4px' }}>Supports PDF, PNG/JPG or WEBP images</p>
                  </div>
                  <button type="button" className="btn btn-secondary" style={{ padding: '6px 12px', fontSize: '0.8rem' }}>
                    Browse Files
                  </button>
                </div>
                
                {file && (
                  <div style={{ marginTop: '16px', display: 'flex', alignItems: 'center', gap: '8px', fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                    <span style={{ color: 'var(--success)' }}>✔</span>
                    <span>Active file: <strong style={{ color: 'var(--secondary)' }}>{file.name}</strong></span>
                  </div>
                )}
                
                {parsing && (
                  <div style={{ marginTop: '20px', display: 'flex', alignItems: 'center', gap: '10px', color: 'var(--primary)', justifyContent: 'center' }}>
                    <Loader2 className="spinner" size={18} />
                    <span style={{ fontSize: '0.85rem', fontWeight: 500 }}>Running local statement parser...</span>
                  </div>
                )}
                
                {errorMessage && (
                  <div className="alert-card alert-danger" style={{ marginTop: '16px' }}>
                    <Info size={16} style={{ flexShrink: 0 }} />
                    <div>{errorMessage}</div>
                  </div>
                )}
              </div>

              {/* Statement Metadata & Custom Mappings */}
              {parsedData && (
                <div className="card-panel" style={{ padding: '24px' }}>
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                    <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1rem', fontWeight: 600, color: 'var(--secondary)' }}>
                      2. Customize Layout
                    </h3>
                    {autoApplied && (
                      <span className="badge badge-success" style={{ display: 'inline-flex', gap: '4px', fontSize: '0.7rem' }}>
                        <CheckCircle2 size={12} /> Mapping Auto-Applied
                      </span>
                    )}
                  </div>
                  
                  {/* Account Metadata Badges */}
                  <div style={{ background: 'rgba(255, 255, 255, 0.02)', padding: '16px', borderRadius: '6px', border: '1px solid var(--border-color)', marginBottom: '20px', fontSize: '0.85rem' }}>
                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '10px' }}>
                      <span style={{ color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', fontSize: '0.75rem', letterSpacing: '0.05em' }}>Statement Details</span>
                      <button 
                        type="button" 
                        onClick={() => setIsEditingMetadata(!isEditingMetadata)}
                        style={{ background: 'none', border: 'none', color: 'var(--primary)', cursor: 'pointer', display: 'flex', alignItems: 'center', gap: '4px', fontSize: '0.8rem', fontWeight: 600 }}
                      >
                        <Edit2 size={12} /> {isEditingMetadata ? 'Done' : 'Edit'}
                      </button>
                    </div>
                    
                    {isEditingMetadata ? (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        <div>
                          <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px', fontWeight: 500 }}>Client Name</label>
                          <input type="text" className="input-field" value={clientName} onChange={(e) => setClientName(e.target.value)} />
                        </div>
                        <div>
                          <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px', fontWeight: 500 }}>Bank Name</label>
                          <input type="text" className="input-field" value={bankName} onChange={(e) => setBankName(e.target.value)} />
                        </div>
                        <div>
                          <label style={{ fontSize: '0.75rem', color: 'var(--text-muted)', display: 'block', marginBottom: '4px', fontWeight: 500 }}>Account Suffix (Last 4 digits)</label>
                          <input type="text" className="input-field" value={accountSuffix} onChange={(e) => setAccountSuffix(e.target.value)} />
                        </div>
                      </div>
                    ) : (
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                        <div>Client: <strong style={{ color: 'var(--secondary)' }}>{clientName}</strong></div>
                        <div>Bank Name: <strong style={{ color: 'var(--secondary)' }}>{bankName}</strong></div>
                        <div>Card/Account Suffix: <strong style={{ color: 'var(--secondary)' }}>{accountSuffix}</strong></div>
                      </div>
                    )}
                  </div>

                  {/* Column Mapping Fields */}
                  <div style={{ display: 'flex', flexDirection: 'column', gap: '12px', marginBottom: '24px' }}>
                    <h4 style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em' }}>Map Statement Fields</h4>
                    
                    {Object.keys(columnMapping).map((stdKey) => (
                      <div key={stdKey} style={{ display: 'grid', gridTemplateColumns: '1fr 1.2fr auto', gap: '10px', alignItems: 'center' }}>
                        <span style={{ fontSize: '0.8rem', textTransform: 'capitalize', color: 'var(--secondary)', fontWeight: 500 }}>{stdKey} Column</span>
                        <input 
                          type="text" 
                          className="input-field" 
                          style={{ padding: '6px 10px', fontSize: '0.8rem' }}
                          value={columnMapping[stdKey]} 
                          onChange={(e) => handleMapChange(stdKey, e.target.value)}
                        />
                        <input 
                          type="checkbox" 
                          style={{ width: '16px', height: '16px', cursor: 'pointer', accentColor: 'var(--primary)' }}
                          checked={columnSequence.includes(columnMapping[stdKey])}
                          onChange={() => handleToggleColumn(stdKey)}
                          title="Include in output Excel"
                        />
                      </div>
                    ))}
                  </div>

                  {/* Column Sequence Order List */}
                  <div style={{ marginBottom: '24px' }}>
                    <h4 style={{ fontSize: '0.8rem', color: 'var(--text-muted)', fontWeight: 600, textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '10px' }}>Arrange Sequence Order</h4>
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
                      {columnSequence.map((customHeader, index) => (
                        <div key={customHeader} style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', padding: '6px 12px', background: 'rgba(255, 255, 255, 0.02)', borderRadius: '6px', border: '1px solid var(--border-color)', fontSize: '0.8rem' }}>
                          <span style={{ fontWeight: 500, color: 'var(--secondary)' }}>{index + 1}. {customHeader}</span>
                          <div style={{ display: 'flex', gap: '4px' }}>
                            <button 
                              type="button" 
                              disabled={index === 0} 
                              onClick={() => moveColumn(index, -1)}
                              style={{ padding: '2px 6px', background: 'rgba(255, 255, 255, 0.04)', border: '1px solid var(--border-color)', color: 'var(--text-main)', borderRadius: '4px', cursor: 'pointer', opacity: index === 0 ? 0.3 : 1 }}
                            >
                              ▲
                            </button>
                            <button 
                              type="button" 
                              disabled={index === columnSequence.length - 1} 
                              onClick={() => moveColumn(index, 1)}
                              style={{ padding: '2px 6px', background: 'rgba(255, 255, 255, 0.04)', border: '1px solid var(--border-color)', color: 'var(--text-main)', borderRadius: '4px', cursor: 'pointer', opacity: index === columnSequence.length - 1 ? 0.3 : 1 }}
                            >
                              ▼
                            </button>
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Save Settings Trigger */}
                  <button 
                    type="button" 
                    className="btn btn-secondary" 
                    onClick={saveMappingConfig}
                    disabled={savingConfig}
                    style={{ width: '100%', display: 'flex', gap: '8px', justifyContent: 'center' }}
                  >
                    {savingConfig ? <Loader2 className="spinner" size={16} /> : <Save size={16} />}
                    {saveSuccess ? 'Configuration Saved!' : 'Save Mapping Configuration'}
                  </button>
                </div>
              )}
            </div>

            {/* Right Column: Transaction Table & Deliveries */}
            <div style={{ display: 'flex', flexDirection: 'column', gap: '32px' }}>
              
              {/* Main Transaction Review Table */}
              <div className="card-panel" style={{ padding: '24px', minHeight: '400px' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
                  <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1.05rem', fontWeight: 600, color: 'var(--secondary)' }}>
                    Transaction Review
                  </h3>
                  {parsedData && (
                    <span style={{ fontSize: '0.8rem', color: 'var(--text-muted)' }}>
                      Total Extracted: <strong style={{ color: 'var(--secondary)' }}>{parsedData.transactions.length}</strong> items
                    </span>
                  )}
                </div>

                {!parsedData ? (
                  <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', justifyContent: 'center', height: '300px', color: 'var(--text-muted)', gap: '12px' }}>
                    <FileSpreadsheet size={40} style={{ opacity: 0.3 }} />
                    <p style={{ fontSize: '0.9rem' }}>Upload a statement to view and edit transactions</p>
                  </div>
                ) : (
                  <div>
                    {parsedData.is_mock && (
                      <div className="alert-card alert-warning" style={{ marginBottom: '20px' }}>
                        <span style={{ fontSize: '1.2rem' }}>⚠️</span>
                        <div style={{ flex: 1 }}>
                          <h4 style={{ fontWeight: 600, marginBottom: '2px' }}>Mock Data Fallback Active</h4>
                          <p style={{ fontSize: '0.8rem', lineHeight: '1.4' }}>
                            The live parser could not connect to the Gemini/Local LLM or encountered a rate/quota limit. 
                            The system fell back to mock data for <strong>{parsedData.bank_name}</strong> (suffix: <strong>{parsedData.account_number_suffix}</strong>).
                          </p>
                          {parsedData.mock_error && (
                            <div style={{ marginTop: '8px', padding: '8px', background: 'rgba(0,0,0,0.03)', border: '1px solid rgba(0,0,0,0.05)', borderRadius: '4px', fontSize: '0.75rem', fontFamily: 'monospace', color: '#92400e', wordBreak: 'break-all' }}>
                              <strong>Error details:</strong> {parsedData.mock_error}
                            </div>
                          )}
                        </div>
                      </div>
                    )}
                    
                    <div className="table-container">
                      <table className="custom-table">
                        <thead>
                          <tr>
                            <th>Date</th>
                            <th>Description</th>
                            <th style={{ textAlign: 'right' }}>Amount</th>
                            <th style={{ textAlign: 'center' }}>Type</th>
                          </tr>
                        </thead>
                        <tbody>
                          {parsedData.transactions.map((tx, idx) => {
                            const isDebit = tx.type === 'debit';
                            return (
                              <tr key={idx}>
                                <td style={{ color: 'var(--text-muted)', width: '15%' }}>{tx.date}</td>
                                <td style={{ fontWeight: 500, color: 'var(--secondary)' }}>{tx.description}</td>
                                <td style={{ textAlign: 'right', fontFamily: 'monospace', fontWeight: 600, color: 'var(--secondary)', width: '20%' }}>
                                  ${tx.amount !== null && tx.amount !== undefined ? tx.amount.toFixed(2) : '0.00'}
                                </td>
                                <td style={{ textAlign: 'center', width: '15%' }}>
                                  <span className={`badge ${isDebit ? 'badge-primary' : 'badge-success'}`}>
                                    {tx.type}
                                  </span>
                                </td>
                              </tr>
                            );
                          })}
                        </tbody>
                      </table>
                    </div>
                  </div>
                )}
              </div>

              {/* Delivery & Integrations Panel */}
              {parsedData && (
                <div className="card-panel" style={{ padding: '24px' }}>
                  <h3 style={{ fontFamily: 'var(--font-display)', fontSize: '1.05rem', fontWeight: 600, color: 'var(--secondary)', marginBottom: '20px' }}>
                    3. Deliver Results
                  </h3>
                  
                  <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '32px' }}>
                    
                    {/* File Export Block */}
                    <div>
                      <h4 style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>
                        Generate Files
                      </h4>
                      
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        <button 
                          type="button" 
                          className="btn btn-primary" 
                          onClick={exportExcel}
                          disabled={exportingExcel}
                          style={{ padding: '10px 16px' }}
                        >
                          {exportingExcel ? <Loader2 className="spinner" size={16} /> : <Download size={16} />}
                          Export Styled Excel File
                        </button>
                        
                        <button 
                          type="button" 
                          className="btn btn-secondary" 
                          onClick={exportIIF}
                          disabled={exportingIIF}
                          style={{ padding: '10px 16px' }}
                        >
                          {exportingIIF ? <Loader2 className="spinner" size={16} /> : <FileCode size={16} />}
                          Export QB Desktop (IIF)
                        </button>
                      </div>
                    </div>

                    {/* Cloud ERP Integrations Block */}
                    <div>
                      <h4 style={{ fontSize: '0.8rem', fontWeight: 600, color: 'var(--text-muted)', textTransform: 'uppercase', letterSpacing: '0.05em', marginBottom: '12px' }}>
                        Direct Sync to Accounting ERP
                      </h4>
                      
                      <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '6px' }}>
                          <select 
                            className="input-field" 
                            value={erpSystem} 
                            onChange={(e) => setErpSystem(e.target.value)}
                            style={{ padding: '8px', fontSize: '0.8rem' }}
                          >
                            <option value="qbo">QuickBooks Online</option>
                            <option value="netsuite">NetSuite REST</option>
                            <option value="xero">Xero API</option>
                            <option value="zoho">Zoho Books</option>
                          </select>
                          
                          <button 
                            type="button" 
                            className="btn btn-success" 
                            onClick={syncERP}
                            disabled={syncingERP}
                            style={{ padding: '8px', fontSize: '0.8rem' }}
                          >
                            {syncingERP ? <Loader2 className="spinner" size={14} /> : <CloudLightning size={14} />}
                            Sync Transactions
                          </button>
                        </div>

                        {/* Sync Target Account Setup */}
                        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '8px', marginTop: '4px' }}>
                          <div>
                            <label style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: '2px', fontWeight: 500 }}>Bank Ledger</label>
                            <input 
                              type="text" 
                              className="input-field" 
                              style={{ padding: '6px', fontSize: '0.75rem' }}
                              value={targetAccounts.bank_account} 
                              onChange={(e) => setTargetAccounts({...targetAccounts, bank_account: e.target.value})} 
                            />
                          </div>
                          <div>
                            <label style={{ fontSize: '0.7rem', color: 'var(--text-muted)', display: 'block', marginBottom: '2px', fontWeight: 500 }}>Offset Ledger</label>
                            <input 
                              type="text" 
                              className="input-field" 
                              style={{ padding: '6px', fontSize: '0.75rem' }}
                              value={targetAccounts.suspense_account} 
                              onChange={(e) => setTargetAccounts({...targetAccounts, suspense_account: e.target.value})} 
                            />
                          </div>
                        </div>
                      </div>
                    </div>

                  </div>

                  {/* Sync Feedback Message */}
                  {erpStatus && (
                    <div 
                      style={{ 
                        marginTop: '20px', 
                        padding: '12px 16px', 
                        borderRadius: '6px', 
                        fontSize: '0.85rem',
                        background: erpSuccess ? '#ecfdf5' : '#fef2f2',
                        border: erpSuccess ? '1px solid #a7f3d0' : '1px solid #fca5a5',
                        color: erpSuccess ? '#065f46' : '#991b1b',
                        display: 'flex',
                        alignItems: 'center',
                        gap: '8px'
                      }}
                    >
                      <Info size={16} style={{ flexShrink: 0 }} />
                      <div>{erpStatus}</div>
                    </div>
                  )}
                </div>
              )}
              
            </div>
          </div>
        </div>
      </main>
    </div>
  );
}

export default App;
