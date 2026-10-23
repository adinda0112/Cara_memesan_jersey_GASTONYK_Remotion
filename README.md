# Cara Memesan Jersey di Website GASTON.YK — Remotion

Proyek video tutorial vertikal berdasarkan screenshot website GASTON.YK yang diberikan pengguna. Screenshot, isi tampilan, dan desain visual tetap dipertahankan; revisi ini mengganti voice-over dengan audio ElevenLabs milik pengguna dan menyelaraskan durasi scene.

## Spesifikasi video
- 1080 × 1920 (9:16), 30 FPS
- Durasi final: sekitar 55,03 detik
- 8 scene yang mudah diedit
- Screenshot website asli tetap menggunakan aset proyek
- Voice-over: ElevenLabs, suara Senandika yang diberikan pengguna
- Musik instrumental latar dengan volume rendah

## File utama
- `src/tutorial.tsx` — komposisi Remotion dan delapan scene
- `public/assets/` — screenshot website yang dipakai video; jangan mengganti jika ingin mempertahankan visual yang sama
- `public/audio/voiceover.wav` — voice-over ElevenLabs yang sudah disusun dan disinkronkan
- `public/audio/voice-01-*.wav` sampai `voice-08-*.wav` — audio per scene, sudah diberi padding agar pas dengan scene masing-masing
- `public/audio/music.wav` — musik latar
- `source/ElevenLabs-voiceover-original.wav` — file asli ElevenLabs yang diberikan pengguna
- `docs/NARASI.txt` — naskah acuan proyek
- `docs/subtitles.srt` — file subtitle tambahan

## Preview dan render melalui Remotion
Pastikan Node.js 20+ terpasang. Buka terminal pada folder proyek, lalu jalankan:

```bash
npm install
npm run studio
```

Pilih komposisi `GastonTutorial` untuk melihat preview. Setelah sesuai, jalankan:

```bash
npm run render
```

Hasilnya tersimpan di `out/tutorial-jersey-gaston.mp4`.

## Render preview lokal (jika npm tidak tersedia)
Proyek menyertakan renderer Python + FFmpeg:

```bash
python scripts/render_preview.py
```

Output: `out/tutorial-jersey-gaston-final.mp4`; storyboard berada di `preview/final/storyboard.jpg`. Renderer lokal membutuhkan Python, Pillow, NumPy, dan FFmpeg.

## Audio dan sinkronisasi
- Audio ElevenLabs asli dipotong pada jeda berenergi rendah di antara bagian narasi. Dua jeda antarbagiannya yang terlalu panjang diringkas agar tempo video tetap ringkas; ucapan tidak dipercepat atau diubah nadanya.
- Delapan file suara per scene dipadankan dengan durasi scene Remotion. `voiceover.wav` adalah gabungan klip-klip tersebut.
- Jangan jalankan `python scripts/prepare_audio.py` kecuali ingin membuat ulang audio TTS fallback; skrip tersebut akan menimpa voice-over ElevenLabs.

## Akurasi dan privasi
- Urutan halaman dan komponen mengikuti screenshot yang diberikan pengguna.
- QRIS, nominal dinamis, nama, nomor WhatsApp, dan kode pesanan sensitif tetap disamarkan sebagaimana aset proyek.
- Tidak ada transaksi baru yang dilakukan atau diklaim berhasil.
