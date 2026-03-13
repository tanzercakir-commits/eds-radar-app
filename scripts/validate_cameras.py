#!/usr/bin/env python3
"""
cameras.json doğrulama scripti.
Kullanım: python3 scripts/validate_cameras.py assets/data/cameras.json
"""
import json, sys, os
from collections import Counter

REQUIRED_TOP = {'version', 'updated_at', 'changelog', 'cameras'}
REQUIRED_CAM = {'aciklama', 'lat', 'lng'}
# Türkiye sınırları (yaklaşık)
LAT_MIN, LAT_MAX = 35.5, 42.5
LNG_MIN, LNG_MAX = 25.5, 45.0

def fail(msg):
    print(f'❌ HATA: {msg}')
    sys.exit(1)

def warn(msg):
    print(f'⚠️  UYARI: {msg}')

def ok(msg):
    print(f'✅ {msg}')

path = sys.argv[1] if len(sys.argv) > 1 else 'assets/data/cameras.json'

# 1. Dosya varlığı
if not os.path.exists(path):
    fail(f'Dosya bulunamadı: {path}')

# 2. JSON geçerliliği
try:
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
except json.JSONDecodeError as e:
    fail(f'Geçersiz JSON: {e}')

# 3. Üst seviye yapı
if not isinstance(data, dict):
    fail('Kök eleman bir obje olmalı (düz dizi kabul edilmez)')

missing = REQUIRED_TOP - set(data.keys())
if missing:
    fail(f'Eksik alan(lar): {missing}')

# 4. Versiyon
version = data['version']
if not isinstance(version, int) or version < 1:
    fail(f'version pozitif tam sayı olmalı, alınan: {version!r}')
ok(f'Versiyon: {version}')
ok(f'Güncelleme tarihi: {data["updated_at"]}')
ok(f'Changelog: {data["changelog"]}')

# 5. Kamera listesi
cameras = data['cameras']
if not isinstance(cameras, list) or len(cameras) == 0:
    fail('cameras boş veya liste değil')

ok(f'Toplam kamera sayısı: {len(cameras)}')

# 6. Her kamera için doğrulama
errors = []
coord_seen = {}
for i, cam in enumerate(cameras):
    for field in REQUIRED_CAM:
        if field not in cam:
            errors.append(f'  [{i}] eksik alan: {field} — {cam.get("aciklama","?")}')

    lat = cam.get('lat')
    lng = cam.get('lng')
    if lat is not None and lng is not None:
        if not (LAT_MIN <= lat <= LAT_MAX) or not (LNG_MIN <= lng <= LNG_MAX):
            errors.append(f'  [{i}] Türkiye dışı koordinat: lat={lat}, lng={lng} — {cam.get("aciklama","?")}')
        key = (round(lat, 5), round(lng, 5))
        if key in coord_seen:
            warn(f'Mükerrer koordinat [{i}] ↔ [{coord_seen[key]}]: {key}')
        else:
            coord_seen[key] = i

if errors:
    print(f'
❌ {len(errors)} hata bulundu:')
    for e in errors[:20]:
        print(e)
    if len(errors) > 20:
        print(f'  ... ve {len(errors)-20} hata daha')
    sys.exit(1)

# 7. İl dağılımı
il_counter = Counter(cam.get('il', 'Bilinmiyor') for cam in cameras)
print(f'
📊 İl dağılımı (ilk 10):')
for il, count in il_counter.most_common(10):
    print(f'   {il}: {count}')

print(f'
✅ Tüm doğrulamalar geçti — {len(cameras)} kamera, versiyon {version}')
