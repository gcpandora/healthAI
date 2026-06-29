import { useState } from 'react';
import {
  View, Text, TextInput, TouchableOpacity,
  ActivityIndicator, StyleSheet, Alert,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../../src/hooks/useAuth';
import { createPost } from '../../src/api/posts';

export default function CreateScreen() {
  const { token } = useAuth();
  const router = useRouter();
  const [content, setContent] = useState('');
  const [loading, setLoading] = useState(false);

  const handlePublish = async () => {
    if (!content.trim() || !token) return;
    setLoading(true);
    try {
      await createPost(token, content.trim());
      setContent('');
      Alert.alert('Publié !', 'Votre publication est en ligne.', [
        { text: 'Voir le feed', onPress: () => router.replace('/(tabs)/') },
      ]);
    } catch {
      Alert.alert('Erreur', 'Impossible de publier. Réessayez.');
    } finally {
      setLoading(false);
    }
  };

  return (
    <View style={styles.container}>
      <Text style={styles.title}>Nouvelle publication</Text>

      <TextInput
        style={styles.input}
        placeholder="Partagez votre progression, un conseil, une victoire…"
        placeholderTextColor="#94a3b8"
        multiline
        numberOfLines={6}
        value={content}
        onChangeText={setContent}
        editable={!loading}
      />

      <Text style={styles.counter}>{content.length} / 500</Text>

      <TouchableOpacity
        style={[styles.btn, (!content.trim() || loading) && styles.btnDisabled]}
        onPress={handlePublish}
        disabled={!content.trim() || loading}
      >
        {loading
          ? <ActivityIndicator color="white" />
          : <Text style={styles.btnText}>Publier</Text>
        }
      </TouchableOpacity>
    </View>
  );
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#fff', padding: 24, paddingTop: 48 },
  title: { fontSize: 22, fontWeight: '800', color: '#1e293b', marginBottom: 24 },
  input: {
    borderWidth: 1.5, borderColor: '#e2e8f0', borderRadius: 12,
    padding: 16, fontSize: 15, color: '#1e293b',
    textAlignVertical: 'top', minHeight: 140,
    backgroundColor: '#f8fafc',
  },
  counter: { textAlign: 'right', color: '#94a3b8', fontSize: 12, marginTop: 6, marginBottom: 24 },
  btn: {
    backgroundColor: '#3498db', borderRadius: 12,
    paddingVertical: 16, alignItems: 'center',
  },
  btnDisabled: { backgroundColor: '#cbd5e1' },
  btnText: { color: 'white', fontWeight: '700', fontSize: 16 },
});
