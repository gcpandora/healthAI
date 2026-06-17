import { useEffect, useState } from "react";
import { getUsers } from "../services/api";
import Table from "../components/Table";
import Loader from "../components/Loader";
import ExportDialog from "../components/ExportDialog";
import styles from "./Users.module.css";

export default function Users() {

  const [users, setUsers] = useState(null);
  const [showExportDialog, setShowExportDialog] = useState(false);

  useEffect(() => {
    getUsers()
      .then(res => {
        // Handle paginated response: extract items array
        const data = res.data?.items || res.data || [];
        setUsers(Array.isArray(data) ? data : []);
      })
      .catch(() => setUsers([]));
  }, []);

  if (!users) return <Loader />;

  return (
    <div className={styles.container}>
      <div className={styles.header}>
        <h1>Users</h1>
        <button
          className={styles.exportBtn}
          onClick={() => setShowExportDialog(true)}
          title="Export users data"
          aria-label="Export users data as JSON or CSV"
        >
          📥 Export
        </button>
      </div>
      
      {showExportDialog && (
        <ExportDialog
          data={users}
          tableName="Users"
          columns={['id', 'email', 'username', 'age', 'gender', 'goal', 'plan', 'role', 'created_at']}
          onClose={() => setShowExportDialog(false)}
        />
      )}
      
      <Table data={users} />
    </div>
  );
}