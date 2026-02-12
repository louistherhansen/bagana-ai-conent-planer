/**
 * Test Login API
 * Tests the login functionality and database connection
 */

import { config } from 'dotenv';
import path from 'path';

// Load environment variables
config({ path: path.resolve(process.cwd(), '.env') });

const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:3000/api';
const TEST_EMAIL = process.env.TEST_EMAIL || 'test@bagana.ai';
const TEST_USERNAME = process.env.TEST_USERNAME || 'testuser';
const TEST_PASSWORD = process.env.TEST_PASSWORD || 'test123456';

async function testLogin(emailOrUsername: string, password: string) {
  console.log('\n=== Testing Login ===');
  console.log(`Email/Username: ${emailOrUsername}`);
  console.log(`Password: ${password.length > 0 ? '***' : '(empty)'}`);
  console.log(`API URL: ${API_URL}/auth/login`);
  
  try {
    const response = await fetch(`${API_URL}/auth/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email: emailOrUsername,
        password: password,
      }),
    });

    const data = await response.json();
    
    console.log(`\nStatus: ${response.status} ${response.statusText}`);
    console.log('Response:', JSON.stringify(data, null, 2));
    
    if (response.ok) {
      console.log('\n✅ Login successful!');
      if (data.token) {
        console.log(`Token: ${data.token.substring(0, 20)}...`);
      }
      return true;
    } else {
      console.log('\n❌ Login failed!');
      return false;
    }
  } catch (error) {
    console.error('\n❌ Error:', error);
    return false;
  }
}

async function testRegister(email: string, username: string, password: string) {
  console.log('\n=== Testing Registration ===');
  console.log(`Email: ${email}`);
  console.log(`Username: ${username}`);
  console.log(`Password: ${password.length > 0 ? '***' : '(empty)'}`);
  console.log(`API URL: ${API_URL}/auth/register`);
  
  try {
    const response = await fetch(`${API_URL}/auth/register`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({
        email,
        username,
        password,
        fullName: 'Test User',
      }),
    });

    const data = await response.json();
    
    console.log(`\nStatus: ${response.status} ${response.statusText}`);
    console.log('Response:', JSON.stringify(data, null, 2));
    
    if (response.ok) {
      console.log('\n✅ Registration successful!');
      return true;
    } else {
      console.log('\n❌ Registration failed!');
      return false;
    }
  } catch (error) {
    console.error('\n❌ Error:', error);
    return false;
  }
}

async function testHealth() {
  console.log('\n=== Testing Health Check ===');
  try {
    const response = await fetch(`${API_URL.replace('/api', '')}/api/health`);
    const data = await response.json().catch(() => ({ status: 'unknown' }));
    console.log(`Status: ${response.status}`);
    console.log('Response:', JSON.stringify(data, null, 2));
    return response.ok;
  } catch (error) {
    console.error('❌ Health check failed:', error);
    return false;
  }
}

async function main() {
  console.log('='.repeat(60));
  console.log('BAGANA AI - Login API Test');
  console.log('='.repeat(60));
  
  // Test health check
  await testHealth();
  
  // Test registration first
  const registered = await testRegister(TEST_EMAIL, TEST_USERNAME, TEST_PASSWORD);
  
  if (!registered) {
    console.log('\n⚠️  Registration failed or user already exists. Trying login...');
  }
  
  // Test login with email
  await testLogin(TEST_EMAIL, TEST_PASSWORD);
  
  // Test login with username
  await testLogin(TEST_USERNAME, TEST_PASSWORD);
  
  // Test login with wrong password
  console.log('\n=== Testing Wrong Password ===');
  await testLogin(TEST_EMAIL, 'wrongpassword');
  
  // Test login with non-existent user
  console.log('\n=== Testing Non-existent User ===');
  await testLogin('nonexistent@test.com', TEST_PASSWORD);
  
  console.log('\n' + '='.repeat(60));
  console.log('Test completed!');
  console.log('='.repeat(60));
}

main().catch(console.error);
