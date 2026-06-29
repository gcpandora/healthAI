import { useEffect, useState, useCallback } from 'react';
import {
  View, Text, FlatList, Image, TouchableOpacity,
  ActivityIndicator, RefreshControl, StyleSheet,
} from 'react-native';
import { useAuth } from '../../src/hooks/useAuth';
import { fetchPosts, toggleLike, type Post } from '../../src/api/posts';

function timeAgo(dateStr: string): string {
  const diff = Math.floor((Date.now() - new Date(dateStr).getTime()) / 1000);
  if (diff < 60) return "À l'instant";
  if (diff < 3600) return `Il y a ${Math.floor(diff / 60)} min`;
  if (diff < 86400) return `Il y a ${Math.floor(diff / 3600)} h`;
  return `Il y a ${Math.floor(diff / 86400)} j`;
}

function PostCard({ post, token }: { post: Post; token: string }) {
  const [likes, setLikes] = useState(post.likes_count);
  const [liked, setLiked] = useState(false);

  const handleLike = async () => {
    setLiked((v) => !v);
    setLikes((n) => n + (liked ? -1 : 1));
    await toggleLike(token, post.id).catch(() => {
      setLiked((v) => !v);
      setLikes((n) => n + (liked ? 1 : -1));
    });
  };

  return (
    <View style={styles.card}>
      <View style={styles.header}>
        <View style={styles.avatar}>
          <Text style={styles.avatarText}>
            {(post.author.display_name ?? 'U')[0].toUpperCase()}
          </Text>
        </View>
        <View>
          <Text style={styles.authorName}>{post.author.display_name ?? 'Utilisateur'}</Text>
          <Text style={styles.time}>{timeAgo(post.created_at)}</Text>
        </View>
      </View>

      {!!post.content && <Text style={styles.content}>{post.content}</Text>}

      {post.media_urls.length > 0 && (
        <Image source={{ uri: post.media_urls[0] }} style={styles.media} resizeMode="cover" />
      )}

      <View style={styles.actions}>
        <TouchableOpacity onPress={handleLike} style={styles.actionBtn}>
          <Text style={[styles.actionIcon, liked && styles.liked]}>{liked ? '❤️' : '🤍'}</Text>
          <Text style={styles.actionCount}>{likes}</Text>
        </TouchableOpacity>
        <View style={styles.actionBtn}>
          <Text style={styles.actionIcon}>💬</Text>
          <Text style={styles.actionCount}>{post.comments_count}</Text>
        </View>
      </View>
    </View>
  );
}

export default function FeedScreen() {
  const { token } = useAuth();
  const [posts, setPosts] = useState<Post[]>([]);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(async () => {
    if (!token) return;
    try {
      setError(null);
      const data = await fetchPosts(token);
      setPosts(data.items);
    } catch {
      setError('Impossible de charger le flux.');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  }, [token]);

  useEffect(() => { load(); }, [load]);

  if (loading) {
    return (
      <View style={styles.center}>
        <ActivityIndicator size="large" color="#3498db" />
        <Text style={styles.loadingText}>Chargement…</Text>
      </View>
    );
  }

  if (error) {
    return (
      <View style={styles.center}>
        <Text style={styles.errorText}>{error}</Text>
        <TouchableOpacity onPress={load} style={styles.retryBtn}>
          <Text style={styles.retryText}>Réessayer</Text>
        </TouchableOpacity>
      </View>
    );
  }

  return (
    <FlatList
      data={posts}
      keyExtractor={(p) => p.id}
      contentContainerStyle={styles.list}
      refreshControl={<RefreshControl refreshing={refreshing} onRefresh={() => { setRefreshing(true); load(); }} />}
      ListHeaderComponent={<Text style={styles.title}>Réseau social</Text>}
      ListEmptyComponent={
        <View style={styles.center}>
          <Text style={styles.emptyText}>Aucune publication pour l'instant.</Text>
        </View>
      }
      renderItem={({ item }) => <PostCard post={item} token={token ?? ''} />}
    />
  );
}

const styles = StyleSheet.create({
  list: { padding: 16, gap: 12 },
  title: { fontSize: 22, fontWeight: '800', color: '#1e293b', marginBottom: 12 },
  center: { flex: 1, justifyContent: 'center', alignItems: 'center', padding: 32 },
  loadingText: { marginTop: 12, color: '#94a3b8' },
  errorText: { color: '#dc2626', textAlign: 'center', marginBottom: 16 },
  retryBtn: { backgroundColor: '#3498db', paddingHorizontal: 24, paddingVertical: 10, borderRadius: 8 },
  retryText: { color: 'white', fontWeight: '600' },
  emptyText: { color: '#94a3b8', fontSize: 15 },
  card: { backgroundColor: 'white', borderRadius: 14, padding: 16, shadowColor: '#000', shadowOpacity: 0.06, shadowRadius: 8, elevation: 2 },
  header: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 10 },
  avatar: { width: 40, height: 40, borderRadius: 20, backgroundColor: '#3498db', justifyContent: 'center', alignItems: 'center' },
  avatarText: { color: 'white', fontWeight: '700', fontSize: 16 },
  authorName: { fontWeight: '700', fontSize: 14, color: '#1e293b' },
  time: { fontSize: 12, color: '#94a3b8' },
  content: { fontSize: 15, color: '#334155', lineHeight: 22, marginBottom: 10 },
  media: { width: '100%', height: 220, borderRadius: 10, marginBottom: 10 },
  actions: { flexDirection: 'row', gap: 16, paddingTop: 10, borderTopWidth: 1, borderTopColor: '#f1f5f9' },
  actionBtn: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  actionIcon: { fontSize: 18 },
  liked: { color: '#e74c3c' },
  actionCount: { fontSize: 14, color: '#64748b', fontWeight: '600' },
});
