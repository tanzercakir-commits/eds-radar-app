#!/usr/bin/env python3
"""
cameras.json dogrulama scripti.
Kullanim: python3 scripts/validate_cameras.py assets/data/cameras.json
"""
import json, sys, os
from collections import Counter

REQUIRED_TOP = {'version', 'updated_at', 'changelog', 'cameras'}
REQUIRED_CAM = {'aciklama', 'lat', 'lng'}
LAT_MIN, LAT_MAX = 35.5, 42.5
LNG_MIN, LNG_MAX = 25.5, 45.0

def fail(msg):
    print('HATA: ' + msg)
    sys.exit(1)

def warn(msg):
    print('UYARI: ' + msg)

def ok(msg):
    print('OK: ' + msg)

path = sys.argv[1] if len(sys.argv) > 1 else 'assets/data/cameras.json'

if not os.path.exists(path):
    fail('Dosya bulunamadi: ' + path)

try:
    with open(path, encoding='utf-8') as f:
        data = json.load(f)
except json.JSONDecodeError as e:
    fail('Gecersiz JSON: ' + str(e))

if not isinstance(data, dict):
    fail('Kok eleman bir obje olmali (duz dizi kabul edilmez)')

missing = REQUIRED_TOP - set(data.keys())
if missing:
    fail('Eksik alan(lar): ' + str(missing))

version = data['version']
if not isinstance(version, int) or version < 1:
    fail('version pozitif tam sayi olmali, alinan: ' + repr(version))

ok('Versiyon: ' + str(version))
ok('Guncelleme tarihi: ' + str(data['updated_at']))
ok('Changelog: ' + str(data['changelog']))

cameras = data['cameras']
if not isinstance(cameras, list) or len(cameras) == 0:
    fail('cameras bos veya liste degil')

ok('Toplam kamera sayisi: ' + str(len(cameras)))

errors = []
coord_seen = {}
for i, cam in enumerate(cameras):
    for field in REQUIRED_CAM:
        if field not in cam:
            errors.append('[' + str(i) + '] eksik alan: ' + field + ' — ' + cam.get('aciklama', '?'))

    lat = cam.get('lat')
    lng = cam.get('lng')
    if lat is not None and lng is not None:
        if not (LAT_MIN <= lat <= LAT_MAX) or not (LNG_MIN <= lng <= LNG_MAX):
            errors.append('[' + str(i) + '] Turkiye disi koordinat: lat=' + str(lat) + ' lng=' + str(lng))
        key = (round(lat, 5), round(lng, 5))
        if key in coord_seen:
            warn('Mukerrer koordinat [' + str(i) + '] <-> [' + str(coord_seen[key]) + ']: ' + str(key))
        else:
            coord_seen[key] = i

if errors:
    print(str(len(errors)) + ' hata bulundu:')
    for e in errors[:20]:
        print('  ' + e)
    if len(errors) > 20:
        print('  ... ve ' + str(len(errors) - 20) + ' hata daha')
    sys.exit(1)

il_counter = Counter(cam.get('il', 'Bilinmiyor') for cam in cameras)
print('\nIl dagilimi (ilk 10):')
for il, count in il_counter.most_common(10):
    print('  ' + str(il) + ': ' + str(count))

print('\nTum dogrulamalar gecti — ' + str(len(cameras)) + ' kamera, versiyon ' + str(version))
