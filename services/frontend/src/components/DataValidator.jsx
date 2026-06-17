import React, { useState, useMemo } from 'react';
import styles from './DataValidator.module.css';

/**
 * DataValidator Component
 * Identifies and allows correction of data anomalies
 * Supports: missing values, outliers, duplicates, invalid formats
 * 
 * WCAG 2.1 AA Accessibility:
 * - ARIA live regions for status updates
 * - Keyboard navigation throughout
 * - Proper form semantics
 * - High contrast colors (4.5:1 minimum)
 */
const DataValidator = ({ data = [], columns = [], onSave = () => {} }) => {
  const [anomalies, setAnomalies] = useState([]);
  const [currentAnomalyIdx, setCurrentAnomalyIdx] = useState(0);
  const [corrections, setCorrections] = useState({});
  const [status, setStatus] = useState('idle'); // idle, detecting, correcting, saved
  const [message, setMessage] = useState('');

  /**
   * Detect various types of anomalies
   */
  const detectAnomalies = React.useCallback(() => {
    setStatus('detecting');
    setMessage('Scanning data...');
    const foundAnomalies = [];
    const anomalyMap = {};

    data.forEach((row, rowIdx) => {
      columns.forEach(col => {
        const value = row[col];
        const recordId = row.id || row._id || rowIdx;
        const key = `${recordId}-${col}`;

        // 1. Missing values (NULL, undefined, empty string)
        if (value === null || value === undefined || value === '') {
          if (!anomalyMap[key]) {
            foundAnomalies.push({
              id: key,
              type: 'MISSING',
              row: rowIdx,
              recordId,
              column: col,
              value,
              severity: 'high',
              suggestion: `Add value for ${col}`
            });
            anomalyMap[key] = true;
          }
        }

        // 2. Outliers (numeric fields > 2 std deviations from mean)
        if (typeof value === 'number' && col !== 'id') {
          const numericValues = data
            .map(r => r[col])
            .filter(v => typeof v === 'number');
          
          if (numericValues.length > 0) {
            const mean = numericValues.reduce((a, b) => a + b, 0) / numericValues.length;
            const stdDev = Math.sqrt(
              numericValues.reduce((sq, n) => sq + Math.pow(n - mean, 2), 0) / numericValues.length
            );

            if (Math.abs(value - mean) > 2 * stdDev && !anomalyMap[key]) {
              foundAnomalies.push({
                id: key,
                type: 'OUTLIER',
                row: rowIdx,
                recordId,
                column: col,
                value,
                severity: 'medium',
                mean: Math.round(mean * 100) / 100,
                suggestion: `Value ${value} is unusual (avg: ${Math.round(mean * 100) / 100})`
              });
              anomalyMap[key] = true;
            }
          }
        }

        // 3. Invalid formats (email, phone, etc.)
        if (typeof value === 'string') {
          if (col.toLowerCase().includes('email') && !isValidEmail(value)) {
            if (!anomalyMap[key]) {
              foundAnomalies.push({
                id: key,
                type: 'INVALID_FORMAT',
                row: rowIdx,
                recordId,
                column: col,
                value,
                severity: 'high',
                suggestion: 'Invalid email format'
              });
              anomalyMap[key] = true;
            }
          }
        }
      });
    });

    // 4. Duplicates
    const seen = {};
    data.forEach((row, rowIdx) => {
      const uniqueKey = columns.slice(0, 2).map(c => row[c]).join('|');
      if (seen[uniqueKey]) {
        const key = `dup-${rowIdx}`;
        foundAnomalies.push({
          id: key,
          type: 'DUPLICATE',
          row: rowIdx,
          recordId: row.id || row._id || rowIdx,
          column: columns[0],
          value: row[columns[0]],
          severity: 'medium',
          suggestion: `Possible duplicate (similar to row ${seen[uniqueKey]})`
        });
      } else {
        seen[uniqueKey] = rowIdx;
      }
    });

    setAnomalies(foundAnomalies);
    setStatus('idle');
    setMessage(`Found ${foundAnomalies.length} anomalies`);
    setCurrentAnomalyIdx(0);
  }, [data, columns]);

  React.useEffect(() => {
    if (data.length > 0) {
      detectAnomalies();
    }
  }, [data, detectAnomalies]);

  const isValidEmail = (email) => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
  };

  const currentAnomaly = anomalies[currentAnomalyIdx];
  const correctionKey = currentAnomaly?.id || '';

  const handleCorrection = (newValue) => {
    setCorrections(prev => ({
      ...prev,
      [correctionKey]: newValue
    }));
  };

  const handleApprove = () => {
    if (currentAnomalyIdx < anomalies.length - 1) {
      setCurrentAnomalyIdx(currentAnomalyIdx + 1);
    } else {
      finalizeSave();
    }
  };

  const handleSkip = () => {
    if (currentAnomalyIdx < anomalies.length - 1) {
      setCurrentAnomalyIdx(currentAnomalyIdx + 1);
    } else {
      finalizeSave();
    }
  };

  const finalizeSave = () => {
    setStatus('correcting');
    setMessage('Applying corrections...');

    setTimeout(() => {
      const correctedData = data.map(row => {
        const correctedRow = { ...row };
        Object.entries(corrections).forEach(([key, newValue]) => {
          const [recordId, column] = key.split('-');
          if ((row.id === recordId || row._id === recordId) && correctedRow[column] !== undefined) {
            correctedRow[column] = newValue;
          }
        });
        return correctedRow;
      });

      onSave(correctedData, corrections);
      setStatus('saved');
      setMessage('✅ Corrections saved!');
    }, 500);
  };

  if (anomalies.length === 0 && status === 'idle') {
    return (
      <div className={styles.container} role="region" aria-label="Data validation">
        <div className={styles.empty}>
          <p>✅ All data looks good!</p>
          <p className={styles.subtext}>No anomalies detected.</p>
        </div>
      </div>
    );
  }

  const progress = ((currentAnomalyIdx + 1) / anomalies.length) * 100;

  return (
    <div 
      className={styles.container} 
      role="region" 
      aria-label="Data validation corrections"
    >
      {/* Status Bar */}
      <div className={styles.statusBar} role="status" aria-live="polite">
        <div className={styles.progressBar}>
          <div 
            className={styles.progressFill} 
            style={{ width: `${progress}%` }}
            aria-valuenow={Math.round(progress)}
            aria-valuemin="0"
            aria-valuemax="100"
          />
        </div>
        <p className={styles.statusText}>
          {status === 'detecting' && '🔍 Detecting anomalies...'}
          {status === 'idle' && `Anomaly ${currentAnomalyIdx + 1} of ${anomalies.length}`}
          {status === 'correcting' && '⏳ Saving corrections...'}
          {status === 'saved' && '✅ All corrections saved!'}
        </p>
      </div>

      {/* Current Anomaly */}
      {currentAnomaly && (
        <div className={`${styles.anomalyCard} ${styles[`severity-${currentAnomaly.severity}`]}`}>
          <div className={styles.anomalyHeader}>
            <span className={styles.badge}>
              {currentAnomaly.type}
            </span>
            <span className={styles.severity}>
              {currentAnomaly.severity === 'high' ? '🔴 High' : '🟡 Medium'}
            </span>
          </div>

          <div className={styles.anomalyDetails}>
            <p>
              <strong>Row:</strong> {currentAnomaly.row + 1}
            </p>
            <p>
              <strong>Column:</strong> {currentAnomaly.column}
            </p>
            <p>
              <strong>Current Value:</strong> 
              <code className={styles.code}>
                {currentAnomaly.value === null ? 'NULL' : JSON.stringify(currentAnomaly.value)}
              </code>
            </p>
            {currentAnomaly.mean && (
              <p>
                <strong>Statistics:</strong> Average: {currentAnomaly.mean}
              </p>
            )}
            <p className={styles.suggestion}>
              💡 {currentAnomaly.suggestion}
            </p>
          </div>

          {/* Correction Form */}
          <form className={styles.correctionForm}>
            <label htmlFor={`correction-input-${currentAnomalyIdx}`}>
              {currentAnomaly.type === 'MISSING' ? 'Enter missing value:' : 'Enter corrected value:'}
            </label>
            <input
              id={`correction-input-${currentAnomalyIdx}`}
              type="text"
              value={corrections[correctionKey] || ''}
              onChange={(e) => handleCorrection(e.target.value)}
              placeholder={`Suggested: ${currentAnomaly.suggestion}`}
              className={styles.input}
              autoFocus
              aria-label={`Correction input for ${currentAnomaly.column}`}
            />
          </form>

          {/* Action Buttons */}
          <div className={styles.actions}>
            <button
              onClick={handleSkip}
              className={styles.btnSkip}
              aria-label="Skip this anomaly"
            >
              Skip
            </button>
            <button
              onClick={handleApprove}
              className={styles.btnApprove}
              disabled={status !== 'idle'}
              aria-label={currentAnomalyIdx === anomalies.length - 1 ? 'Save all corrections' : 'Continue to next anomaly'}
            >
              {currentAnomalyIdx === anomalies.length - 1 ? '✅ Save All' : 'Next'}
            </button>
          </div>
        </div>
      )}

      {/* Message Alerts */}
      <div 
        className={styles.message}
        role="alert"
        aria-live="assertive"
      >
        {message}
      </div>
    </div>
  );
};

export default DataValidator;
