/**
 * Test script to verify password hashing and verification
 * Tests SHA-256 hash verification for existing users
 */

const crypto = require('crypto');

// Password hash from database
const storedHash = '240be518fabd2724ddb6f04eeb1da5967448d7e831c08c8fa822809f74c720a9';

// Test passwords
const testPasswords = [
  'admin',
  'Admin',
  'password',
  'Password123',
  'bagana123',
  'Bagana123'
];

console.log('🔍 Testing password verification...\n');
console.log(`Stored hash: ${storedHash}\n`);

// Test each password
testPasswords.forEach(password => {
  const passwordHash = crypto.createHash('sha256').update(password).digest('hex');
  const matches = passwordHash === storedHash;
  
  console.log(`Password: "${password}"`);
  console.log(`  Hash:    ${passwordHash}`);
  console.log(`  Match:   ${matches ? '✅ YES' : '❌ NO'}\n`);
});

// Test the actual verifyPassword function if available
console.log('\n📋 Testing verifyPassword function...\n');

// Try to load the auth module from the built Next.js app
try {
  // In standalone mode, the code is in .next/server
  // We need to test via API or use the compiled code
  console.log('Note: To test verifyPassword function, use the API endpoint');
  console.log('Example: curl -X POST http://localhost:3000/api/auth/login \\');
  console.log('  -H "Content-Type: application/json" \\');
  console.log('  -d \'{"email":"admin@bagana.ai","password":"<password>"}\'\n');
} catch (error) {
  console.error('Error:', error.message);
}
