const BASE_URL = process.env.EXPO_PUBLIC_PUB_API_URL ?? 'http://10.0.2.2:8004';

function headers(token: string) {
  return { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` };
}

export interface Author {
  user_id: string;
  display_name: string;
  avatar_url: string | null;
}

export interface Post {
  id: string;
  content: string;
  media_urls: string[];
  created_at: string;
  author: Author;
  likes_count: number;
  comments_count: number;
}

export async function fetchPosts(token: string, cursor?: string): Promise<{ items: Post[]; next_cursor: string | null }> {
  const url = cursor ? `${BASE_URL}/posts?limit=10&cursor=${cursor}` : `${BASE_URL}/posts?limit=10`;
  const res = await fetch(url, { headers: headers(token) });
  if (!res.ok) throw new Error('Impossible de charger les publications');
  return res.json();
}

export async function createPost(token: string, content: string): Promise<Post> {
  const res = await fetch(`${BASE_URL}/posts`, {
    method: 'POST',
    headers: headers(token),
    body: JSON.stringify({ content, media_urls: [] }),
  });
  if (!res.ok) throw new Error('Impossible de créer la publication');
  return res.json();
}

export async function toggleLike(token: string, postId: string): Promise<void> {
  await fetch(`${BASE_URL}/posts/${postId}/likes`, {
    method: 'POST',
    headers: headers(token),
  });
}
