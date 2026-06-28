import { View, Text, TouchableOpacity, StyleSheet } from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../../src/hooks/useAuth';

function decodeJwtPayload(token: string): Record<string, unknown> {
  try {
    const base64 = token.split('.')[1].replace(/-/g, '+').replace(/_/g, '/');
    const padded = base64 + '==='.slice((base64.length + 3) % 4);
    return JSON.parse(atob(padded)) as Record<string, unknown>;
  } catch {
    return {};
  }
}

export default function ProfileScreen() {
  const { token, logout } = useAuth();
  const router = useRouter();

  const payload = token ? decodeJwtPayload(token) : {};
  const subject = typeof payload.sub === 'string' ? payload.sub : 'Inconnu';

  const handleLogout = async () => {
    await logout();
    router.replace('/(auth)/login');
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Mon Profil</Text>

      <View style={styles.card}>
        <Text style={styles.label}>Identifiant utilisateur</Text>
        <Text style={styles.value} numberOfLines={1}>
          {subject}
        </Text>
      </View>

      <TouchableOpacity
        style={styles.logoutButton}
        onPress={handleLogout}
        accessibilityRole="button"
        accessibilityLabel="Se déconnecter"
      >
        <Text style={styles.logoutText}>Se déconnecter</Text>
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#fff',
    paddingHorizontal: 24,
    paddingTop: 64,
  },
  title: {
    fontSize: 26,
    fontWeight: '700',
    color: '#222',
    marginBottom: 32,
  },
  card: {
    backgroundColor: '#f5f5f5',
    borderRadius: 12,
    padding: 16,
    marginBottom: 16,
  },
  label: {
    fontSize: 12,
    color: '#888',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
    marginBottom: 4,
  },
  value: {
    fontSize: 16,
    color: '#222',
    fontWeight: '500',
  },
  logoutButton: {
    marginTop: 32,
    borderWidth: 1.5,
    borderColor: '#e53935',
    borderRadius: 8,
    paddingVertical: 14,
    alignItems: 'center',
  },
  logoutText: {
    color: '#e53935',
    fontSize: 16,
    fontWeight: '600',
  },
});
