#!/usr/bin/env node
/**
 * Configure Mini App manifest (farcaster.json) with your domain
 *
 * Usage:
 *   node scripts/config-miniapp.mjs https://your-domain.vercel.app
 *   npm run miniapp:config -- https://your-domain.vercel.app
 */

import { readFileSync, writeFileSync, copyFileSync, existsSync } from 'fs';
import { join, dirname } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const manifestPath = join(__dirname, '..', 'public', '.well-known', 'farcaster.json');
const backupPath = manifestPath + '.bak';

// Get domain from command line
const domain = process.argv[2];

if (!domain) {
  console.error('❌ Error: Please provide a domain');
  console.error('');
  console.error('Usage:');
  console.error('  node scripts/config-miniapp.mjs https://your-domain.vercel.app');
  console.error('  npm run miniapp:config -- https://your-domain.vercel.app');
  process.exit(1);
}

// Validate HTTPS
if (!domain.startsWith('https://')) {
  console.error('❌ Error: Domain must use HTTPS');
  console.error(`   Got: ${domain}`);
  console.error('   Expected: https://your-domain.vercel.app');
  process.exit(1);
}

// Remove trailing slash
const cleanDomain = domain.replace(/\/$/, '');

// Validate URL format
try {
  new URL(cleanDomain);
} catch (e) {
  console.error('❌ Error: Invalid URL format');
  console.error(`   Got: ${domain}`);
  process.exit(1);
}

// Check if manifest exists
if (!existsSync(manifestPath)) {
  console.error('❌ Error: farcaster.json not found');
  console.error(`   Expected at: ${manifestPath}`);
  process.exit(1);
}

// Read current manifest
let manifest;
try {
  const content = readFileSync(manifestPath, 'utf8');
  manifest = JSON.parse(content);
} catch (e) {
  console.error('❌ Error: Failed to parse farcaster.json');
  console.error(`   ${e.message}`);
  process.exit(1);
}

// Backup original
console.log('📦 Creating backup: farcaster.json.bak');
copyFileSync(manifestPath, backupPath);

// Update URLs
console.log(`🔧 Configuring domain: ${cleanDomain}`);

manifest.frame.homeUrl = cleanDomain;
manifest.frame.iconUrl = `${cleanDomain}/assets/icon.png`;
manifest.frame.imageUrl = `${cleanDomain}/assets/preview.png`;
manifest.frame.splashImageUrl = `${cleanDomain}/assets/splash.png`;

// Validate JSON
try {
  const newContent = JSON.stringify(manifest, null, 2);
  JSON.parse(newContent); // Validate it parses back correctly

  // Write updated manifest
  writeFileSync(manifestPath, newContent);
  console.log('✅ Updated farcaster.json successfully!');
} catch (e) {
  console.error('❌ Error: Failed to write valid JSON');
  console.error(`   ${e.message}`);
  process.exit(1);
}

// Summary
console.log('');
console.log('📋 Updated values:');
console.log(`   homeUrl:       ${manifest.frame.homeUrl}`);
console.log(`   iconUrl:       ${manifest.frame.iconUrl}`);
console.log(`   imageUrl:      ${manifest.frame.imageUrl}`);
console.log(`   splashImageUrl: ${manifest.frame.splashImageUrl}`);
console.log('');
console.log('⚠️  Remember to update accountAssociation manually:');
console.log('   1. Go to Base Build (Preview)');
console.log('   2. Create Account Association for your domain');
console.log('   3. Copy header, payload, and signature to farcaster.json');
console.log('');
console.log('🔍 Verify after deployment:');
console.log(`   curl -s ${cleanDomain}/.well-known/farcaster.json | jq .`);
