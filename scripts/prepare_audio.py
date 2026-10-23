from pathlib import Path
import subprocess, wave, math
import numpy as np
ROOT=Path(__file__).resolve().parents[1]
AUDIO=ROOT/'public'/'audio'; AUDIO.mkdir(parents=True,exist_ok=True)
FPS=30; SR=22050; RATE=175
NARRATION=[
('01-intro','Mau pesan jersey GASTON YK? Ikuti panduan singkat ini.'),
('02-catalog','Buka gaston titik sevenpion titik web titik id. Pilih Store untuk melihat koleksi.'),
('03-options','Pilih produk, tekan Beli, lalu atur ukuran. Nama punggung opsional, maksimal sepuluh huruf. Tentukan jumlah dan tekan Beli Langsung.'),
('04-checkout','Isi nama lengkap dan nomor WhatsApp aktif. Catatan tambahan boleh dikosongkan.'),
('05-summary','Cek produk, ukuran, nama, jumlah, dan total. Jika benar, tekan Konfirmasi Pesanan.'),
('06-payment','Di halaman QRIS, cek nominal dan batas waktu. Bayar hanya dengan QRIS pesananmu sendiri. QRIS di video ini disamarkan.'),
('07-status','Setelah pembayaran terverifikasi, simpan kode pesanan dan pantau statusnya.'),
('08-outro','Untuk pengambilan atau pengiriman, hubungi admin sesuai petunjuk website. Selesai!'),
]
clips=[]; scene_frames=[]; scene_durations=[]
for name,text in NARRATION:
    out=AUDIO/f'voice-{name}.wav'
    subprocess.run(['espeak','-v','id+f2','-s',str(RATE),'-p','48','-a','165','-g','3','-w',str(out),text],check=True)
    with wave.open(str(out),'rb') as w:
        params=w.getparams(); data=np.frombuffer(w.readframes(w.getnframes()),dtype=np.int16).copy()
    if params.framerate!=SR or params.nchannels!=1 or params.sampwidth!=2:
        raise RuntimeError(f'Unexpected voice audio format: {out} {params}')
    frames=math.ceil((len(data)/SR+0.35)*FPS)
    target=round(frames/FPS*SR)
    if len(data)<target: data=np.pad(data,(0,target-len(data)))
    else: data=data[:target]
    clips.append(data.astype(np.int16)); scene_frames.append(frames)
    scene_durations.append(len(data)/SR)
voice=np.concatenate(clips).astype(np.int16)
with wave.open(str(AUDIO/'voiceover.wav'),'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes(voice.tobytes())
TOTAL_FRAMES=sum(scene_frames); DURATION=TOTAL_FRAMES/FPS
# Gentle, original instrumental bed synthesized locally; no copyrighted recording.
n=int(DURATION*SR); t=np.arange(n,dtype=np.float32)/SR
music=np.zeros(n,dtype=np.float32)
beat=60/94
chords=[[146.83,174.61,220.00,293.66],[116.54,146.83,174.61,233.08],[130.81,164.81,196.00,261.63],[130.81,164.81,196.00,246.94]]
# Chunked vector synthesis for a warm, low-volume electronic pad.
for i in range(0,n,4096):
    tt=t[i:i+4096]
    if not len(tt): continue
    idx=(tt//(beat*4)).astype(int)%len(chords)
    local=np.mod(tt,beat*4)
    swell=.5-.5*np.cos(2*np.pi*local/(beat*4))
    val=np.zeros_like(tt)
    for j in range(4):
        freqs=np.array([chords[k][j] for k in idx])
        val += np.sin(2*np.pi*freqs*tt+j*.12)*(0.45 if j<2 else 0.28)
    music[i:i+len(tt)] += .018*(.58+.42*swell)*val
# Soft beat pulse, intentionally quiet beneath speech.
for b in range(int(DURATION/beat)+1):
    start=int(b*beat*SR)
    if start>=n: break
    dur=min(int(.15*SR),n-start); tt=np.arange(dur,dtype=np.float32)/SR
    music[start:start+dur]+=np.sin(2*np.pi*(68-16*tt/.15)*tt)*np.exp(-tt*23)*.022
    if b%2==1:
        dur2=min(int(.035*SR),n-start)
        music[start:start+dur2]+=np.random.default_rng(9+b).normal(0,1,dur2).astype(np.float32)*np.exp(-np.arange(dur2)/SR*95)*.004
fade_in=min(int(1.2*SR),n); fade_out=min(int(1.8*SR),n)
music[:fade_in]*=np.linspace(0,1,fade_in)
music[-fade_out:]*=np.linspace(1,0,fade_out)
music=np.clip(music,-.08,.08)
with wave.open(str(AUDIO/'music.wav'),'wb') as w:
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(SR); w.writeframes((music*32767).astype(np.int16).tobytes())
print('Voice clips:')
for (name,_),f,d in zip(NARRATION,scene_frames,scene_durations): print(f'{name}: {f} frames, {f/FPS:.2f}s')
print(f'TOTAL: {TOTAL_FRAMES} frames, {DURATION:.3f}s')
(ROOT/'scenes.json').write_text(__import__('json').dumps([{'id':name,'text':text,'frames':frames,'seconds':round(frames/FPS,3)} for (name,text),frames in zip(NARRATION,scene_frames)],ensure_ascii=False,indent=2),encoding='utf-8')
