import { test } from 'node:test';
import assert from 'node:assert/strict';
import {
  parsePackCount,
  parseSize,
  pricePerUnit,
  classifySeller,
  enrich,
} from '../src/normalize.js';

test('parsePackCount reads common pack notations', () => {
  assert.equal(parsePackCount('Coffee 200g x 3 packs'), 3);
  assert.equal(parsePackCount('UHT Milk 1L x 12 boxes'), 12);
  assert.equal(parsePackCount('Sachet 1.8g x 50 pcs'), 50);
  assert.equal(parsePackCount('แชมพู 500ml แพ็ค 2'), 2);
  assert.equal(parsePackCount('single bottle 500ml'), 1);
});

test('parseSize normalises to base units', () => {
  assert.deepEqual(parseSize('Milk 1L'), { dim: 'volume', baseQty: 1000 });
  assert.deepEqual(parseSize('Shampoo 500 ml'), { dim: 'volume', baseQty: 500 });
  assert.deepEqual(parseSize('Coffee 200g'), { dim: 'weight', baseQty: 200 });
  assert.deepEqual(parseSize('Rice 2 kg'), { dim: 'weight', baseQty: 2000 });
  assert.deepEqual(parseSize('Mask 50 pcs'), { dim: 'count', baseQty: 50 });
});

test('pricePerUnit accounts for pack multiplier', () => {
  // 200g x 3 = 600g = 0.6kg at ฿289 -> ~481.67/kg
  const a = pricePerUnit('Coffee 200g x 3 packs', 289);
  assert.equal(a.unitLabel, 'kg');
  assert.ok(Math.abs(a.pricePerUnit - 289 / 0.6) < 0.01);
  assert.equal(a.pack, 3);

  // 1L x 12 = 12L at ฿399 -> 33.25/L
  const b = pricePerUnit('UHT Milk 1L x 12 boxes', 399);
  assert.equal(b.unitLabel, 'L');
  assert.ok(Math.abs(b.pricePerUnit - 399 / 12) < 0.01);
});

test('pricePerUnit lets you compare unequal pack sizes correctly', () => {
  const big = pricePerUnit('Shampoo 1L jumbo', 329); // 329/L
  const small = pricePerUnit('Shampoo 500 ml bottle', 189); // 378/L
  assert.ok(big.pricePerUnit < small.pricePerUnit); // the 1L is the better deal per litre
});

test('pricePerUnit returns null when size is unknown', () => {
  const r = pricePerUnit('Mystery gadget', 100);
  assert.equal(r.pricePerUnit, null);
});

test('classifySeller distinguishes domestic vs overseas', () => {
  assert.equal(classifySeller({ location: 'Bangkok' }), true);
  assert.equal(classifySeller({ location: 'Chiang Mai' }), true);
  assert.equal(classifySeller({ location: 'Overseas - China' }), false);
  assert.equal(classifySeller({ location: '' }), null);
  assert.equal(classifySeller({ location: 'x', flags: { overseas: true } }), false);
});

test('enrich produces the full comparable record', () => {
  const r = enrich({
    site: 'shopee',
    id: '1.2',
    title: 'Nescafe 200g x 3',
    price: 289,
    location: 'Bangkok',
    url: 'https://shopee.co.th/x',
  });
  assert.equal(r.site, 'shopee');
  assert.equal(r.sellerOrigin, 'local');
  assert.equal(r.unit, 'kg');
  assert.ok(r.pricePerUnit > 0);
  assert.equal(r.url, 'https://shopee.co.th/x');
});
