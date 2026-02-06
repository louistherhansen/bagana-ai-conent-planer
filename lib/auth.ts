/**
 * Authentication Utilities
 * Handles password hashing, token generation, and session management
 */

import crypto from 'crypto';
import { query } from './db';

export interface User {
  id: string;
  email: string;
  username: string;
  fullName?: string;
  role: string;
  isActive: boolean;
  createdAt: Date;
  lastLogin?: Date;
}

export interface Session {
  id: string;
  userId: string;
  token: string;
  expiresAt: Date;
  createdAt: Date;
}

/**
 * Hash password using bcrypt (we'll use Node.js crypto for simplicity, 
 * but in production should use bcrypt library)
 */
export async function hashPassword(password: string): Promise<string> {
  // For MVP, we'll use a simple hash. In production, use bcrypt:
  // const bcrypt = require('bcrypt');
  // return bcrypt.hash(password, 10);
  
  // Simple SHA-256 hash for MVP (NOT secure for production!)
  const hash = crypto.createHash('sha256').update(password).digest('hex');
  return hash;
}

/**
 * Verify password
 */
export async function verifyPassword(password: string, hash: string): Promise<boolean> {
  // For MVP, simple comparison. In production, use bcrypt:
  // const bcrypt = require('bcrypt');
  // return bcrypt.compare(password, hash);
  
  const passwordHash = crypto.createHash('sha256').update(password).digest('hex');
  return passwordHash === hash;
}

/**
 * Generate secure random token
 */
export function generateToken(): string {
  return crypto.randomBytes(32).toString('hex');
}

/**
 * Generate user ID
 */
export function generateUserId(): string {
  return `user_${Date.now()}_${crypto.randomBytes(8).toString('hex')}`;
}

/**
 * Get user by email
 */
export async function getUserByEmail(email: string): Promise<User | null> {
  try {
    const result = await query<{
      id: string;
      email: string;
      username: string;
      password_hash: string;
      full_name: string | null;
      role: string;
      is_active: boolean;
      created_at: Date;
      last_login: Date | null;
    }>(
      'SELECT id, email, username, password_hash, full_name, role, is_active, created_at, last_login FROM users WHERE email = $1 AND is_active = TRUE',
      [email]
    );
    
    if (result.rows.length === 0) return null;
    
    const row = result.rows[0];
    return {
      id: row.id,
      email: row.email,
      username: row.username,
      fullName: row.full_name || undefined,
      role: row.role,
      isActive: row.is_active,
      createdAt: row.created_at,
      lastLogin: row.last_login || undefined,
    };
  } catch (error) {
    console.error('Error getting user by email:', error);
    return null;
  }
}

/**
 * Get user by username
 */
export async function getUserByUsername(username: string): Promise<User | null> {
  try {
    const result = await query<{
      id: string;
      email: string;
      username: string;
      password_hash: string;
      full_name: string | null;
      role: string;
      is_active: boolean;
      created_at: Date;
      last_login: Date | null;
    }>(
      'SELECT id, email, username, password_hash, full_name, role, is_active, created_at, last_login FROM users WHERE username = $1 AND is_active = TRUE',
      [username]
    );
    
    if (result.rows.length === 0) return null;
    
    const row = result.rows[0];
    return {
      id: row.id,
      email: row.email,
      username: row.username,
      fullName: row.full_name || undefined,
      role: row.role,
      isActive: row.is_active,
      createdAt: row.created_at,
      lastLogin: row.last_login || undefined,
    };
  } catch (error) {
    console.error('Error getting user by username:', error);
    return null;
  }
}

/**
 * Create new user
 */
export async function createUser(params: {
  email: string;
  username: string;
  password: string;
  fullName?: string;
  role?: string;
}): Promise<User | null> {
  try {
    const id = generateUserId();
    const passwordHash = await hashPassword(params.password);
    const role = params.role || 'user';
    
    await query(
      `INSERT INTO users (id, email, username, password_hash, full_name, role)
       VALUES ($1, $2, $3, $4, $5, $6)`,
      [id, params.email, params.username, passwordHash, params.fullName || null, role]
    );
    
    return getUserByEmail(params.email);
  } catch (error) {
    console.error('Error creating user:', error);
    return null;
  }
}

/**
 * Create session
 */
export async function createSession(userId: string, ipAddress?: string, userAgent?: string): Promise<Session | null> {
  try {
    const id = `session_${Date.now()}_${crypto.randomBytes(8).toString('hex')}`;
    const token = generateToken();
    const expiresAt = new Date();
    expiresAt.setDate(expiresAt.getDate() + 7); // 7 days expiry
    
    await query(
      `INSERT INTO sessions (id, user_id, token, expires_at, ip_address, user_agent)
       VALUES ($1, $2, $3, $4, $5, $6)`,
      [id, userId, token, expiresAt, ipAddress || null, userAgent || null]
    );
    
    // Update last_login
    await query(
      'UPDATE users SET last_login = CURRENT_TIMESTAMP WHERE id = $1',
      [userId]
    );
    
    return {
      id,
      userId,
      token,
      expiresAt,
      createdAt: new Date(),
    };
  } catch (error) {
    console.error('Error creating session:', error);
    return null;
  }
}

/**
 * Get session by token
 */
export async function getSessionByToken(token: string): Promise<Session | null> {
  try {
    const result = await query<{
      id: string;
      user_id: string;
      token: string;
      expires_at: Date;
      created_at: Date;
    }>(
      'SELECT id, user_id, token, expires_at, created_at FROM sessions WHERE token = $1 AND expires_at > CURRENT_TIMESTAMP',
      [token]
    );
    
    if (result.rows.length === 0) return null;
    
    const row = result.rows[0];
    return {
      id: row.id,
      userId: row.user_id,
      token: row.token,
      expiresAt: row.expires_at,
      createdAt: row.created_at,
    };
  } catch (error) {
    console.error('Error getting session:', error);
    return null;
  }
}

/**
 * Delete session
 */
export async function deleteSession(token: string): Promise<boolean> {
  try {
    await query('DELETE FROM sessions WHERE token = $1', [token]);
    return true;
  } catch (error) {
    console.error('Error deleting session:', error);
    return false;
  }
}

/**
 * Get user by session token
 */
export async function getUserBySessionToken(token: string): Promise<User | null> {
  const session = await getSessionByToken(token);
  if (!session) return null;
  
  try {
    const result = await query<{
      id: string;
      email: string;
      username: string;
      password_hash: string;
      full_name: string | null;
      role: string;
      is_active: boolean;
      created_at: Date;
      last_login: Date | null;
    }>(
      'SELECT id, email, username, password_hash, full_name, role, is_active, created_at, last_login FROM users WHERE id = $1 AND is_active = TRUE',
      [session.userId]
    );
    
    if (result.rows.length === 0) return null;
    
    const row = result.rows[0];
    return {
      id: row.id,
      email: row.email,
      username: row.username,
      fullName: row.full_name || undefined,
      role: row.role,
      isActive: row.is_active,
      createdAt: row.created_at,
      lastLogin: row.last_login || undefined,
    };
  } catch (error) {
    console.error('Error getting user by session:', error);
    return null;
  }
}
