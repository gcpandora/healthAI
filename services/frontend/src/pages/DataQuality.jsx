/*import { useState, useEffect } from 'react';
import { getUsers, nutritionAPI, exercisesAPI } from '../services/api';
import DataValidator from '../components/DataValidator';
import Loader from '../components/Loader';
import Card from '../components/Card';
import styles from './DataQuality.module.css';

export default function DataQuality() {
  const [selectedTable, setSelectedTable] = useState('users');
  const [tableData, setTableData] = useState(null);
  const [loading, setLoading] = useState(false);

  // Load table data based on selected table
  useEffect(() => {
    loadTableData();
  }, [selectedTable]);

  const loadTableData = async () => {
    setLoading(true);
    try {
      let data = [];
      
      switch (selectedTable) {
        case 'users':
          const usersRes = await getUsers();
          data = usersRes.data || [];
          break;
        case 'nutrition':
          const nutritionRes = await nutritionAPI.getNutritionItems();
          data = nutritionRes.data || [];
          break;
        case 'exercises':
          const exercisesRes = await exercisesAPI.getExercises();
          data = exercisesRes.data || [];
          break;
        default:
          data = [];
      }
      
      setTableData(data);
    } catch (error) {
      console.error(`Error loading ${selectedTable}:`, error);
      setTableData([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Data Quality Checker</h1>
      
      <div className={styles.info}>
        <p>Detect and correct data anomalies: missing values, outliers, duplicates, and invalid formats.</p>
      </div>

      {/* Table Selection *//*
      <Card>
        <div className={styles.tableSelector}>
          <label htmlFor="table-select" className={styles.label}>
            Select Table to Validate:
          </label>
          <select
            id="table-select"
            value={selectedTable}
            onChange={(e) => setSelectedTable(e.target.value)}
            className={styles.select}
            aria-label="Select table for data validation"
          >
            <option value="users">👥 Users ({tableData?.length || 0} records)</option>
            <option value="nutrition">🍎 Nutrition Items ({tableData?.length || 0} records)</option>
            <option value="exercises">💪 Exercises ({tableData?.length || 0} records)</option>
          </select>
        </div>
      </Card>

      {/* Data Validator Component *//*
      {loading ? (
        <Loader />
      ) : tableData && tableData.length > 0 ? (
        <DataValidator data={tableData} tableName={selectedTable} />
      ) : (
        <Card>
          <div className={styles.empty}>
            <p>No data available for {selectedTable} table. Please import data first.</p>
            <button
              className={styles.importBtn}
              onClick={() => window.location.href = '/'}
              aria-label="Go to home page to import data"
            >
              Go to Dashboard
            </button>
          </div>
        </Card>
      )}

      {/* Stats Summary *//*
      {tableData && tableData.length > 0 && (
        <Card>
          <div className={styles.stats}>
            <h2>Table Statistics</h2>
            <div className={styles.statsGrid}>
              <div className={styles.statItem}>
                <span className={styles.label}>Total Records</span>
                <span className={styles.value}>{tableData.length}</span>
              </div>
              <div className={styles.statItem}>
                <span className={styles.label}>Columns</span>
                <span className={styles.value}>{Object.keys(tableData[0] || {}).length}</span>
              </div>
              <div className={styles.statItem}>
                <span className={styles.label}>Last Updated</span>
                <span className={styles.value}>{new Date().toLocaleDateString('fr-FR')}</span>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}*/
//tojo: j'ai mis à jour le fichier dataQuality pour modifier le select car il y avais un bug
import { useState, useEffect } from 'react';
import { getUsers, nutritionAPI, exercisesAPI } from '../services/api';
import DataValidator from '../components/DataValidator';
import Loader from '../components/Loader';
import Card from '../components/Card';
import styles from './DataQuality.module.css';

export default function DataQuality() {
  const [selectedTable, setSelectedTable] = useState('users');
  const [tableData, setTableData] = useState(null);
  const [loading, setLoading] = useState(false);
  const [counts, setCounts] = useState({ users: 0, nutrition: 0, exercises: 0 });

  // Charger les counts des 3 tables au montage
  useEffect(() => {
    const loadCounts = async () => {
      try {
        const [usersRes, nutritionRes, exercisesRes] = await Promise.all([
          getUsers(),
          nutritionAPI.getNutritionItems(),
          exercisesAPI.getExercises()
        ]);
        setCounts({
          users: (usersRes.data || []).length,
          nutrition: (nutritionRes.data || []).length,
          exercises: (exercisesRes.data || []).length
        });
      } catch (error) {
        console.error('Error loading counts:', error);
      }
    };
    loadCounts();
  }, []);

  // Recharger les données quand la table sélectionnée change
  useEffect(() => {
    loadTableData();
  }, [selectedTable]);

  const loadTableData = async () => {
    setLoading(true);
    try {
      let data = [];

      switch (selectedTable) {
        case 'users':
          const usersRes = await getUsers();
          data = usersRes.data || [];
          break;
        case 'nutrition':
          const nutritionRes = await nutritionAPI.getNutritionItems();
          data = nutritionRes.data || [];
          break;
        case 'exercises':
          const exercisesRes = await exercisesAPI.getExercises();
          data = exercisesRes.data || [];
          break;
        default:
          data = [];
      }

      setTableData(data);
      // Mettre à jour le count de la table courante avec les données fraîches
      setCounts(prev => ({ ...prev, [selectedTable]: data.length }));
    } catch (error) {
      console.error(`Error loading ${selectedTable}:`, error);
      setTableData([]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className={styles.container}>
      <h1 className={styles.title}>Data Quality Checker</h1>

      <div className={styles.info}>
        <p>Detect and correct data anomalies: missing values, outliers, duplicates, and invalid formats.</p>
      </div>

      {/* Table Selection */}
      <Card>
        <div className={styles.tableSelector}>
          <label htmlFor="table-select" className={styles.label}>
            Select Table to Validate:
          </label>
          <select
            id="table-select"
            value={selectedTable}
            onChange={(e) => setSelectedTable(e.target.value)}
            className={styles.select}
            aria-label="Select table for data validation"
          >
            <option value="users">👥 Users ({counts.users} records)</option>
            <option value="nutrition">🍎 Nutrition Items ({counts.nutrition} records)</option>
            <option value="exercises">💪 Exercises ({counts.exercises} records)</option>
          </select>
        </div>
      </Card>

      {/* Data Validator Component */}
      {loading ? (
        <Loader />
      ) : tableData && tableData.length > 0 ? (
        <DataValidator data={tableData} tableName={selectedTable} />
      ) : (
        <Card>
          <div className={styles.empty}>
            <p>No data available for {selectedTable} table. Please import data first.</p>
            <button
              className={styles.importBtn}
              onClick={() => window.location.href = '/'}
              aria-label="Go to home page to import data"
            >
              Go to Dashboard
            </button>
          </div>
        </Card>
      )}

      {/* Stats Summary */}
      {tableData && tableData.length > 0 && (
        <Card>
          <div className={styles.stats}>
            <h2>Table Statistics</h2>
            <div className={styles.statsGrid}>
              <div className={styles.statItem}>
                <span className={styles.label}>Total Records</span>
                <span className={styles.value}>{tableData.length}</span>
              </div>
              <div className={styles.statItem}>
                <span className={styles.label}>Columns</span>
                <span className={styles.value}>{Object.keys(tableData[0] || {}).length}</span>
              </div>
              <div className={styles.statItem}>
                <span className={styles.label}>Last Updated</span>
                <span className={styles.value}>{new Date().toLocaleDateString('fr-FR')}</span>
              </div>
            </div>
          </div>
        </Card>
      )}
    </div>
  );
}