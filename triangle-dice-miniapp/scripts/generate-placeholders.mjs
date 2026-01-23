#!/usr/bin/env node
/**
 * Generate placeholder PNG images for the Mini App
 * These should be replaced with actual assets before production deployment
 */

import { writeFileSync, mkdirSync, existsSync } from 'fs';
import { dirname, join } from 'path';
import { fileURLToPath } from 'url';

const __dirname = dirname(fileURLToPath(import.meta.url));
const assetsDir = join(__dirname, '..', 'public', 'assets');

// Ensure assets directory exists
if (!existsSync(assetsDir)) {
  mkdirSync(assetsDir, { recursive: true });
}

// Minimal 1x1 PNG (dark purple color #0f0f1a)
// This is a valid PNG file that displays as a solid color
const minimalPNG = Buffer.from([
  0x89, 0x50, 0x4e, 0x47, 0x0d, 0x0a, 0x1a, 0x0a, // PNG signature
  0x00, 0x00, 0x00, 0x0d, 0x49, 0x48, 0x44, 0x52, // IHDR chunk
  0x00, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x01,
  0x08, 0x02, 0x00, 0x00, 0x00, 0x90, 0x77, 0x53,
  0xde, 0x00, 0x00, 0x00, 0x0c, 0x49, 0x44, 0x41, // IDAT chunk
  0x54, 0x08, 0xd7, 0x63, 0xf8, 0xcf, 0xc0, 0x00,
  0x00, 0x00, 0x03, 0x00, 0x01, 0x00, 0x18, 0xdd,
  0x8d, 0xb4, 0x00, 0x00, 0x00, 0x00, 0x49, 0x45, // IEND chunk
  0x4e, 0x44, 0xae, 0x42, 0x60, 0x82
]);

// Write placeholder images
const files = ['icon.png', 'preview.png', 'splash.png'];

for (const file of files) {
  const filePath = join(assetsDir, file);
  writeFileSync(filePath, minimalPNG);
  console.log(`Created placeholder: ${filePath}`);
}

console.log('\n⚠️  These are placeholder images (1x1 pixel).');
console.log('Replace them with actual assets before production deployment:');
console.log('  - icon.png: 512x512 or larger, app icon');
console.log('  - preview.png: 1200x630 recommended, social preview');
console.log('  - splash.png: 1200x1200 recommended, splash screen');
