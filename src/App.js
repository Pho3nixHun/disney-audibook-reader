import React, { useState, useEffect } from 'react';
import './App.css';

function App() {
  const [nfcSupported, setNfcSupported] = useState(false);
  const [isScanning, setIsScanning] = useState(false);
  const [nfcData, setNfcData] = useState([]);
  const [error, setError] = useState('');

  useEffect(() => {
    // Check if Web NFC is supported
    if ('NDEFReader' in window) {
      setNfcSupported(true);
    } else {
      setError('Web NFC is not supported on this device. Please use Chrome on Android.');
    }
  }, []);

  const startScanning = async () => {
    if (!nfcSupported) {
      setError('NFC not supported');
      return;
    }

    try {
      setIsScanning(true);
      setError('');

      const ndef = new window.NDEFReader();

      // Request permission first
      await ndef.scan();

      console.log('NFC scan started');

      ndef.addEventListener('reading', ({ message, serialNumber }) => {
        console.log('NFC tag detected:', { message, serialNumber });

        const tagData = {
          id: serialNumber,
          timestamp: new Date().toLocaleString(),
          records: []
        };

        for (const record of message.records) {
          const recordData = {
            recordType: record.recordType,
            mediaType: record.mediaType,
            id: record.id,
            data: null,
            text: null
          };

          // Try to decode the data
          try {
            if (record.recordType === 'text') {
              const textDecoder = new TextDecoder(record.encoding || 'utf-8');
              recordData.text = textDecoder.decode(record.data);
            } else if (record.recordType === 'url') {
              const textDecoder = new TextDecoder();
              recordData.text = textDecoder.decode(record.data);
            } else {
              // For other types, show hex representation
              const bytes = new Uint8Array(record.data);
              recordData.data = Array.from(bytes)
                .map(b => b.toString(16).padStart(2, '0'))
                .join(' ');
            }
          } catch (err) {
            console.error('Error decoding record:', err);
            // Fallback to hex
            const bytes = new Uint8Array(record.data);
            recordData.data = Array.from(bytes)
              .map(b => b.toString(16).padStart(2, '0'))
              .join(' ');
          }

          tagData.records.push(recordData);
        }

        setNfcData(prev => [tagData, ...prev.slice(0, 9)]); // Keep last 10 scans
      });

      ndef.addEventListener('readingerror', () => {
        console.error('NFC reading error');
        setError('Error reading NFC tag');
      });

    } catch (error) {
      console.error('NFC Error:', error);
      setError(`NFC Error: ${error.message}`);
      setIsScanning(false);
    }
  };

  const stopScanning = () => {
    setIsScanning(false);
    // Note: Web NFC API doesn't provide a direct way to stop scanning
    // The scan will continue until the page is closed or refreshed
  };

  const clearData = () => {
    setNfcData([]);
  };

  const formatBytes = (bytes) => {
    if (!bytes) return 'No data';
    return bytes.toUpperCase();
  };

  return (
    <div className="App">
      <header className="App-header">
        <h1>🏰 Disney NFC Reader</h1>
        <p>Scan your Disney NFC figures to see their data</p>
      </header>

      <main className="App-main">
        {!nfcSupported && (
          <div className="error-card">
            <h3>❌ NFC Not Supported</h3>
            <p>This feature requires Chrome on Android with NFC enabled.</p>
            <p>Make sure:</p>
            <ul>
              <li>You're using Chrome browser</li>
              <li>NFC is enabled in your phone settings</li>
              <li>You're accessing via HTTPS</li>
            </ul>
          </div>
        )}

        {nfcSupported && (
          <div className="controls">
            {!isScanning ? (
              <button
                className="scan-button"
                onClick={startScanning}
              >
                🔍 Start NFC Scanning
              </button>
            ) : (
              <div className="scanning-status">
                <div className="pulse-animation"></div>
                <p>📱 Ready to scan - Hold NFC tag near your phone</p>
                <button
                  className="stop-button"
                  onClick={stopScanning}
                >
                  Stop Scanning
                </button>
              </div>
            )}

            {nfcData.length > 0 && (
              <button className="clear-button" onClick={clearData}>
                Clear Data
              </button>
            )}
          </div>
        )}

        {error && (
          <div className="error-card">
            <h3>⚠️ Error</h3>
            <p>{error}</p>
          </div>
        )}

        <div className="data-section">
          <h2>Scanned Tags ({nfcData.length})</h2>

          {nfcData.length === 0 && isScanning && (
            <div className="empty-state">
              <p>No tags scanned yet. Hold a Disney figure near your phone's NFC area.</p>
            </div>
          )}

          {nfcData.map((tag, index) => (
            <div key={`${tag.id}-${tag.timestamp}`} className="tag-card">
              <div className="tag-header">
                <h3>Tag #{nfcData.length - index}</h3>
                <span className="timestamp">{tag.timestamp}</span>
              </div>

              <div className="tag-info">
                <p><strong>Serial Number:</strong> {tag.id}</p>
                <p><strong>Records:</strong> {tag.records.length}</p>
              </div>

              {tag.records.map((record, recordIndex) => (
                <div key={recordIndex} className="record-card">
                  <h4>Record {recordIndex + 1}</h4>
                  <div className="record-details">
                    <p><strong>Type:</strong> {record.recordType}</p>
                    {record.mediaType && (
                      <p><strong>Media Type:</strong> {record.mediaType}</p>
                    )}
                    {record.id && (
                      <p><strong>ID:</strong> {record.id}</p>
                    )}
                    {record.text && (
                      <div>
                        <strong>Text:</strong>
                        <pre className="data-content">{record.text}</pre>
                      </div>
                    )}
                    {record.data && (
                      <div>
                        <strong>Data (Hex):</strong>
                        <pre className="data-content hex-data">{formatBytes(record.data)}</pre>
                      </div>
                    )}
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      </main>
    </div>
  );
}

export default App;