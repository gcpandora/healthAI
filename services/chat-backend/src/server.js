const express   = require('express');
const http      = require('http');
const { Server } = require('socket.io');
const cors      = require('cors');
const rateLimit = require('express-rate-limit');
const dotenv    = require('dotenv');
const jwt       = require('jsonwebtoken');
const jwksRsa   = require('jwks-rsa');

dotenv.config();

const { initDb, Channel, Message, User } = require('./models');
const usersRouter = require('./routes/users.routes');
const postsRouter = require('./routes/posts.routes');
const { verifyToken, getKey, normalizeUser, HS256_SECRET } = require('./middleware/auth.middleware');
const { errorMiddleware } = require('./middleware/error.middleware');

const app    = express();
const server = http.createServer(app);

/* ─── CORS ─────────────────────────────────────────────────────────────── */
const ALLOWED_ORIGINS = (process.env.ALLOWED_ORIGINS || 'http://localhost:5173').split(',');

const corsOptions = {
  origin: (origin, callback) => {
    // Allow requests with no origin (e.g. mobile apps, Postman, same-origin)
    if (!origin || ALLOWED_ORIGINS.includes(origin)) {
      callback(null, true);
    } else {
      callback(new Error(`CORS: origin ${origin} non autorisée.`));
    }
  },
  methods: ['GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'OPTIONS'],
  allowedHeaders: ['Content-Type', 'Authorization'],
  credentials: true
};

app.use(cors(corsOptions));
app.use(express.json());

/* ─── RATE LIMITING ─────────────────────────────────────────────────────── */
// Limite globale : 100 requêtes / 15 min
const globalLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 100,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Trop de requêtes, veuillez réessayer dans quelques minutes.' }
});

// Limite stricte pour l'auth : 10 requêtes / 15 min
const authLimiter = rateLimit({
  windowMs: 15 * 60 * 1000,
  max: 10,
  standardHeaders: true,
  legacyHeaders: false,
  message: { error: 'Trop de tentatives, veuillez patienter.' }
});

app.use(globalLimiter);

/* ─── ROUTES ────────────────────────────────────────────────────────────── */
app.use('/api/users',    authLimiter, usersRouter);
app.use('/api/posts',    postsRouter);

// Channels CRUD
app.get('/api/channels', verifyToken, async (req, res, next) => {
  try {
    const channels = await Channel.findAll({ order: [['id', 'ASC']] });
    res.json(channels);
  } catch (err) { next(err); }
});

app.post('/api/channels', verifyToken, async (req, res, next) => {
  const { name, description } = req.body;
  if (!name) return res.status(400).json({ message: 'Le nom du channel est obligatoire.' });
  try {
    const normalized = name.trim().toLowerCase().replace(/\s+/g, '-');
    const existing = await Channel.findOne({ where: { name: normalized } });
    if (existing) return res.status(400).json({ message: 'Un channel avec ce nom existe déjà.' });
    const channel = await Channel.create({ name: normalized, description });
    io.emit('channel_created', channel);
    res.status(201).json(channel);
  } catch (err) { next(err); }
});

// Health check
app.get('/api/health', (req, res) => res.json({ status: 'ok', timestamp: new Date() }));

/* ─── SOCKET.IO ─────────────────────────────────────────────────────────── */
const io = new Server(server, {
  cors: {
    origin: ALLOWED_ORIGINS,
    methods: ['GET', 'POST']
  }
});

// Auth middleware for sockets (Keycloak JWT)
const jwksClientSocket = jwksRsa({
  jwksUri: `${process.env.KEYCLOAK_SERVER_URL || 'http://keycloak:8080'}/realms/${process.env.KEYCLOAK_REALM || 'social-network'}/protocol/openid-connect/certs`,
  cache: true,
  rateLimit: true,
  jwksRequestsPerMinute: 10,
  timeout: 30000
});

function getSocketKey(header, callback) {
  jwksClientSocket.getSigningKey(header.kid, (err, key) => {
    if (err) return callback(err);
    callback(null, key.getPublicKey() || key.rsaPublicKey);
  });
}

io.use((socket, next) => {
  const token = socket.handshake.auth.token || socket.handshake.query.token;
  const hintUsername = socket.handshake.auth.username || null;

  if (!token) return next(new Error('Auth token missing'));

  // Attempt 1 : HS256 (HealthAI JWT)
  jwt.verify(token, HS256_SECRET, { algorithms: ['HS256'] }, (err, decoded) => {
    if (!err && decoded) {
      const u = normalizeUser(decoded);
      socket.user = {
        keycloakId: u.keycloakId,
        username:   u.username !== 'Utilisateur' ? u.username : (hintUsername || u.username),
        email:      u.email,
      };
      return next();
    }

    // Fallback : RS256 via Keycloak JWKS
    jwt.verify(token, getSocketKey, {}, (err2, decoded2) => {
      if (err2) return next(new Error('Auth token invalid'));
      socket.user = {
        keycloakId: decoded2.sub,
        username:   decoded2.preferred_username || hintUsername || 'Utilisateur',
        email:      decoded2.email || '',
      };
      next();
    });
  });
});

/* ─── Online users map ──────────────────────────────────────────────────── */
const onlineUsers = new Map(); // socketId → { username, keycloakId, activeChannelId }

const getOnlineUsersList = () => {
  const seen = new Set();
  const list = [];
  for (const user of onlineUsers.values()) {
    if (!seen.has(user.keycloakId)) {
      seen.add(user.keycloakId);
      list.push({ username: user.username, keycloakId: user.keycloakId, activeChannelId: user.activeChannelId });
    }
  }
  return list;
};

/* ─── Typing state map ──────────────────────────────────────────────────── */
// channelId → Set of usernames currently typing
const typingUsers = new Map();

io.on('connection', (socket) => {
  console.log(`[WS] Connected: ${socket.user.username} (${socket.id})`);

  onlineUsers.set(socket.id, {
    username:        socket.user.username,
    keycloakId:      socket.user.keycloakId,
    activeChannelId: null
  });
  io.emit('online_users', getOnlineUsersList());

  /* ── Join a channel room ─────────────────────────────────────────────── */
  socket.on('join_channel', async ({ channelId }) => {
    const currentUser = onlineUsers.get(socket.id);

    // Leave previous room & remove from its typing set
    if (currentUser?.activeChannelId) {
      const prevChannel = currentUser.activeChannelId;
      socket.leave(`channel_${prevChannel}`);
      const typingSet = typingUsers.get(prevChannel);
      if (typingSet) {
        typingSet.delete(socket.user.username);
        io.to(`channel_${prevChannel}`).emit('typing_users', Array.from(typingSet));
      }
    }

    socket.join(`channel_${channelId}`);
    console.log(`[WS] ${socket.user.username} joined room channel_${channelId}`);

    if (currentUser) {
      currentUser.activeChannelId = channelId;
      onlineUsers.set(socket.id, currentUser);
    }
    io.emit('online_users', getOnlineUsersList());

    // Send history
    try {
      const messages = await Message.findAll({
        where: { channelId },
        order: [['createdAt', 'ASC']],
        limit: 100
      });
      socket.emit('channel_history', { channelId, messages });
    } catch (err) {
      console.error('[WS] Error fetching history:', err.message);
    }
  });

  /* ── Send message ────────────────────────────────────────────────────── */
  socket.on('send_message', async ({ channelId, content }) => {
    if (!content?.trim()) return;

    // Clear typing status on message send
    const typingSet = typingUsers.get(channelId);
    if (typingSet) {
      typingSet.delete(socket.user.username);
      io.to(`channel_${channelId}`).emit('typing_users', Array.from(typingSet));
    }

    try {
      const localUser = await User.findOne({ where: { keycloakId: socket.user.keycloakId } });
      const msg = await Message.create({
        content:        content.trim(),
        senderUsername: socket.user.username,
        channelId,
        userId:         localUser?.id || null
      });
      io.to(`channel_${channelId}`).emit('new_message', msg);
    } catch (err) {
      console.error('[WS] Error saving message:', err.message);
      socket.emit('error', { message: "Impossible d'envoyer le message." });
    }
  });

  /* ── Typing indicator ────────────────────────────────────────────────── */
  socket.on('typing_start', ({ channelId }) => {
    if (!typingUsers.has(channelId)) typingUsers.set(channelId, new Set());
    typingUsers.get(channelId).add(socket.user.username);
    // Broadcast to others in the room (not the sender)
    socket.to(`channel_${channelId}`).emit('typing_users', Array.from(typingUsers.get(channelId)));
  });

  socket.on('typing_stop', ({ channelId }) => {
    const typingSet = typingUsers.get(channelId);
    if (typingSet) {
      typingSet.delete(socket.user.username);
      socket.to(`channel_${channelId}`).emit('typing_users', Array.from(typingSet));
    }
  });

  /* ── Disconnect ──────────────────────────────────────────────────────── */
  socket.on('disconnect', () => {
    console.log(`[WS] Disconnected: ${socket.user.username} (${socket.id})`);
    const user = onlineUsers.get(socket.id);

    // Remove from any typing set
    if (user?.activeChannelId) {
      const typingSet = typingUsers.get(user.activeChannelId);
      if (typingSet) {
        typingSet.delete(socket.user.username);
        io.to(`channel_${user.activeChannelId}`).emit('typing_users', Array.from(typingSet));
      }
    }
    onlineUsers.delete(socket.id);
    io.emit('online_users', getOnlineUsersList());
  });
});

/* ─── ERROR HANDLER ─────────────────────────────────────────────────────── */
app.use(errorMiddleware);

/* ─── START ─────────────────────────────────────────────────────────────── */
const PORT = process.env.PORT || 3000;

initDb().then(() => {
  server.listen(PORT, () => {
    console.log(`Social Place backend listening on port ${PORT}`);
    console.log(`CORS allowed origins: ${ALLOWED_ORIGINS.join(', ')}`);
  });
});
