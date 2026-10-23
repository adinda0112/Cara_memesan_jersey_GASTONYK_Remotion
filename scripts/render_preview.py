"""Local preview renderer for the Remotion project when npm packages are unavailable.
Renders the same eight scene plan with Pillow + FFmpeg and uses the project's TTS audio.
"""
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageOps
from pathlib import Path
import subprocess, math, json, shutil
import numpy as np

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / 'public' / 'assets'
AUDIO = ROOT / 'public' / 'audio'
PREVIEW = ROOT / 'preview' / 'final'
CLIPS = ROOT / 'out' / 'clips'
OUT = ROOT / 'out' / 'tutorial-jersey-gaston-final.mp4'
W, H, FPS = 1080, 1920, 30
PREVIEW.mkdir(parents=True, exist_ok=True)
CLIPS.mkdir(parents=True, exist_ok=True)

FONT_CANDIDATES = {
    'bold': [
        '/usr/share/fonts/opentype/inter/InterDisplay-Bold.otf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf',
        'C:/Windows/Fonts/arialbd.ttf',
        '/Library/Fonts/Arial Bold.ttf',
    ],
    'medium': [
        '/usr/share/fonts/opentype/inter/Inter-Medium.otf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        'C:/Windows/Fonts/arial.ttf',
        '/Library/Fonts/Arial.ttf',
    ],
    'regular': [
        '/usr/share/fonts/opentype/inter/Inter-Regular.otf',
        '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',
        'C:/Windows/Fonts/arial.ttf',
        '/Library/Fonts/Arial.ttf',
    ],
}
def font(size, bold=False, medium=False):
    key = 'bold' if bold else ('medium' if medium else 'regular')
    for path in FONT_CANDIDATES[key]:
        if Path(path).exists():
            return ImageFont.truetype(path, size)
    return ImageFont.load_default()

SCENES = [
 dict(id='intro',step='PANDUAN PEMESANAN',title='CARA MEMESAN JERSEY\nGASTON.YK',subtitle='Panduan singkat berdasarkan tampilan website asli',caption='Mau pesan jersey GASTON YK? Ikuti panduan singkat ini.',asset='catalog-grid.png',duration=189,kind='intro',box=(82,505,916,678),voice='voice-01-intro.wav'),
 dict(id='catalog',step='LANGKAH 01 / 06',title='Buka Store dan pilih produk',subtitle='Ketik alamat website, lalu buka menu Store.',caption='Buka gaston.sevenpion.web.id. Pilih Store untuk melihat koleksi.',asset='catalog-store.png',duration=261,kind='catalog',box=(95,420,890,960),voice='voice-02-catalog.wav',focus=[(425,480,130,62),(390,1260,110,82)]),
 dict(id='options',step='LANGKAH 02 / 06',title='Atur pilihan produk',subtitle='Ikuti opsi yang tampil pada produk yang kamu pilih.',caption='Pilih produk, tekan Beli, lalu atur ukuran. Nama punggung opsional, maksimal 10 huruf. Tentukan jumlah dan tekan Beli Langsung.',asset='product-modal.png',duration=307,kind='options',box=(130,420,820,1070),voice='voice-03-options.wav',focus=[(172,805,585,112),(172,988,735,108),(172,1150,270,100),(172,1335,735,108)],badge='CONTOH MODAL BELI LANGSUNG'),
 dict(id='checkout',step='LANGKAH 03 / 06',title='Isi data pembeli',subtitle='Gunakan nama dan nomor WhatsApp yang aktif.',caption='Isi nama lengkap dan nomor WhatsApp aktif. Catatan tambahan boleh dikosongkan.',asset='checkout-fields.png',duration=167,kind='checkout',box=(170,420,740,1070),voice='voice-04-checkout.wav',focus=[(200,780,680,275)]),
 dict(id='summary',step='LANGKAH 04 / 06',title='Periksa pesanan',subtitle='Pastikan semua detail dan total sudah benar.',caption='Cek produk, ukuran, nama, jumlah, dan total. Jika benar, tekan Konfirmasi Pesanan.',asset='order-summary.png',duration=186,kind='summary',box=(90,470,900,1046),voice='voice-05-summary.wav',focus=[(195,1210,690,140)]),
 dict(id='payment',step='LANGKAH 05 / 06',title='Selesaikan pembayaran',subtitle='Ikuti instruksi pada halaman pembayaran.',caption='Di halaman QRIS, cek nominal dan batas waktu. Bayar hanya dengan QRIS pesananmu sendiri. QRIS di video ini disamarkan.',asset='payment-example.png',duration=175,kind='payment',box=(175,440,730,1088),voice='voice-06-payment.wav',focus=[(205,855,670,540)],badge='CONTOH QRIS • BUKAN UNTUK PEMBAYARAN'),
 dict(id='status',step='LANGKAH 06 / 06',title='Pantau status pesanan',subtitle='Status diperbarui setelah pembayaran terverifikasi.',caption='Setelah pembayaran terverifikasi, simpan kode pesanan dan pantau statusnya.',asset='status-example.png',duration=140,kind='status',box=(160,430,760,1133),voice='voice-07-status.wav',focus=[(195,1010,690,300)],badge='CONTOH TAMPILAN STATUS'),
 dict(id='outro',step='SELESAI',title='Selesai, tinggal pantau!',subtitle='Simpan kode pesanan untuk memudahkan pengecekan.',caption='Untuk pengambilan atau pengiriman, hubungi admin sesuai petunjuk website. Selesai!',asset='catalog-grid.png',duration=226,kind='outro',box=(60,510,500,370),voice='voice-08-outro.wav'),
]
TOTAL_FRAMES = sum(s['duration'] for s in SCENES)
DURATION = TOTAL_FRAMES/FPS

# Build the brand gradient once.
y, x = np.mgrid[0:H, 0:W]
base = np.zeros((H,W,3),dtype=np.float32)
for i,(a,b) in enumerate(zip((8,8,10),(32,9,16))): base[:,:,i]=a+(b-a)*(y/H)
dist=np.sqrt(((x-W*.56)/(W*.8))**2+((y-H*.48)/(H*.78))**2)
glow=np.clip(1-dist,0,1)**2
base[:,:,0]+=glow*35; base[:,:,1]+=glow*5; base[:,:,2]+=glow*9
BG=Image.fromarray(np.uint8(np.clip(base,0,255)),'RGB').convert('RGBA')
dots=Image.new('RGBA',(W,H),(0,0,0,0)); dd=ImageDraw.Draw(dots)
for yy in range(60,H,82):
    for xx in range(35+(yy//82%2)*30,W,90): dd.ellipse((xx,yy,xx+2,yy+2),fill=(255,239,230,23))
BG=Image.alpha_composite(BG,dots)
WHITE=(250,247,244,255); MUTED=(205,187,189,255); ORANGE=(255,112,75,255); GOLD=(245,176,91,255)

def wrap_lines(draw,text,fnt,max_width):
    words=text.split(); lines=[]; cur=''
    for word in words:
        trial=(cur+' '+word).strip()
        if draw.textbbox((0,0),trial,font=fnt)[2] <= max_width or not cur: cur=trial
        else: lines.append(cur); cur=word
    if cur: lines.append(cur)
    return lines

def draw_multiline(draw,text,xy,fnt,fill,max_width,line_gap=5,max_lines=3):
    x0,y0=xy
    for line in wrap_lines(draw,text,fnt,max_width)[:max_lines]:
        draw.text((x0,y0),line,font=fnt,fill=fill,stroke_width=0)
        y0 += fnt.size+line_gap
    return y0

def draw_round_card(im,box,fill=(22,15,18,248),outline=(99,54,47,255),radius=24,shadow=True):
    x0,y0,w,h=box
    if shadow:
        layer=Image.new('RGBA',(W,H),(0,0,0,0)); d=ImageDraw.Draw(layer)
        d.rounded_rectangle((x0+6,y0+10,x0+w+6,y0+h+10),radius=radius,fill=(0,0,0,115))
        im.alpha_composite(layer.filter(ImageFilter.GaussianBlur(12)))
    d=ImageDraw.Draw(im)
    d.rounded_rectangle((x0,y0,x0+w,y0+h),radius=radius,fill=fill,outline=outline,width=3)

def paste_rounded(im, asset, box, radius=18, zoom=1.0):
    x0,y0,w,h=box
    src=Image.open(ASSETS/asset).convert('RGB')
    # Match screenshot aspect ratios to the layout card. A very slight zoom is used for motion in the video.
    fitted=ImageOps.fit(src,(w,h),method=Image.Resampling.LANCZOS,centering=(.5,.5))
    if zoom != 1.0:
        zw,zh=int(w*zoom),int(h*zoom)
        fitted=ImageOps.fit(fitted,(zw,zh),method=Image.Resampling.LANCZOS)
        fitted=fitted.crop(((zw-w)//2,(zh-h)//2,(zw-w)//2+w,(zh-h)//2+h))
    mask=Image.new('L',(w,h),0); ImageDraw.Draw(mask).rounded_rectangle((0,0,w-1,h-1),radius=radius,fill=255)
    im.paste(fitted,(x0,y0),mask)

def draw_header(d,scene,idx):
    d.ellipse((58,34,120,96),outline=(255,247,243,230),width=3)
    d.text((76,34),'G',font=font(42,True),fill=WHITE)
    d.text((136,37),'GASTON.YK',font=font(28,True),fill=WHITE)
    d.text((138,73),'OFFICIAL STORE',font=font(14),fill=MUTED)
    d.rounded_rectangle((58,124,370,176),radius=26,fill=(50,21,27,255),outline=(118,64,55,255),width=2)
    d.text((78,139),scene['step'],font=font(17,True),fill=(255,177,143,255))

def draw_title(d,scene):
    if scene['kind']=='intro':
        draw_multiline(d,scene['title'],(58,215),font(63,True),WHITE,960,0,2)
        d.text((62,365),scene['subtitle'],font=font(27),fill=MUTED)
    else:
        title_size=54 if len(scene['title'])>23 else 60
        draw_multiline(d,scene['title'],(58,220),font(title_size,True),WHITE,960,2,2)
        d.text((62,312),scene['subtitle'],font=font(27),fill=MUTED)

def draw_caption(d,text,top,height):
    d.rounded_rectangle((58,top,1022,top+height),radius=24,fill=(22,15,18,250),outline=(99,54,47,255),width=2)
    d.rounded_rectangle((58,top+24,66,top+height-24),radius=4,fill=ORANGE)
    draw_multiline(d,text,(90,top+25),font(25,True),WHITE,890,5,3)

def draw_badge(d,text):
    d.rounded_rectangle((180,378,900,426),radius=24,fill=(50,21,27,255),outline=(138,71,57,255),width=2)
    f=font(17,True); bbox=d.textbbox((0,0),text,font=f); tw=bbox[2]-bbox[0]
    d.text(((W-tw)//2,391),text,font=f,fill=(255,193,143,255))

def draw_focus(d,boxes,frame):
    pulse=int(190+65*(.5+.5*math.sin(frame/8)))
    color=(255,105,66,pulse)
    for box in boxes:
        x0,y0,w,h=box
        d.rounded_rectangle((x0,y0,x0+w,y0+h),radius=18,outline=color,width=4)

def draw_progress(d,idx,scene_frame):
    progress=(idx+scene_frame/SCENES[idx]['duration'])/len(SCENES)
    d.rounded_rectangle((58,1842,1022,1849),radius=4,fill=(255,255,255,45))
    d.rounded_rectangle((58,1842,58+int(964*progress),1849),radius=4,fill=ORANGE)
    d.text((58,1870),'GASTON.YK  •  gaston.sevenpion.web.id',font=font(17),fill=(183,162,164,255))

def make_still(scene,idx,frame):
    im=BG.copy(); d=ImageDraw.Draw(im)
    draw_header(d,scene,idx); draw_title(d,scene)
    kind=scene['kind']; box=scene['box']
    if kind=='intro':
        draw_round_card(im,box,fill=(248,245,241,255),outline=(241,126,91,255),radius=28)
        paste_rounded(im,scene['asset'],(box[0]+4,box[1]+4,box[2]-8,box[3]-8),radius=22)
        d=ImageDraw.Draw(im)
        d.rounded_rectangle((60,1240,1020,1358),radius=24,fill=(50,21,27,255),outline=(128,67,55,255),width=2)
        f=font(27,True); text=scene['caption']; bbox=d.textbbox((0,0),text,font=f); tw=bbox[2]-bbox[0]
        d.text(((W-tw)//2,1280),text,font=f,fill=WHITE)
    elif kind=='outro':
        draw_round_card(im,box,fill=(248,245,241,255),outline=(241,126,91,255),radius=24)
        paste_rounded(im,scene['asset'],(box[0]+4,box[1]+4,box[2]-8,box[3]-8),radius=20)
        items=[('01','SIMPAN KODE','Simpan kode pesananmu.'),('02','PANTAU STATUS','Cek pembaruan pesanan.'),('03','HUBUNGI ADMIN','Atur pengambilan atau pengiriman.')]
        for i,(n,title,desc) in enumerate(items):
            x0,y0=590,510+i*150
            d.rounded_rectangle((x0,y0,x0+430,y0+126),radius=22,fill=(28,20,23,255),outline=(101,55,47,255),width=2)
            d.rounded_rectangle((x0+18,y0+32,x0+80,y0+94),radius=18,fill=ORANGE)
            d.text((x0+29,y0+49),n,font=font(22,True),fill=(28,16,18,255))
            d.text((x0+98,y0+22),title,font=font(21,True),fill=WHITE)
            draw_multiline(d,desc,(x0+98,y0+57),font(18),MUTED,295,3,2)
        d.rounded_rectangle((60,1030,1020,1275),radius=26,fill=(50,21,27,255),outline=(128,67,55,255),width=2)
        d.text((94,1060),'BUTUH BANTUAN?',font=font(22,True),fill=GOLD)
        draw_multiline(d,scene['caption'],(94,1100),font(27,True),WHITE,870,6,3)
        d.text((94,1215),'gaston.sevenpion.web.id',font=font(22,True),fill=(255,177,143,255))
        draw_caption(d,scene['caption'],1400,170)
    else:
        draw_round_card(im,box,fill=(248,245,241,255),outline=(241,126,91,255),radius=24)
        paste_rounded(im,scene['asset'],(box[0]+4,box[1]+4,box[2]-8,box[3]-8),radius=20)
        d=ImageDraw.Draw(im)
        if scene.get('focus'): draw_focus(d,scene['focus'],frame)
        if scene.get('badge'): draw_badge(d,scene['badge'])
        if kind=='catalog': draw_caption(d,scene['caption'],1410,170)
        elif kind=='options': draw_caption(d,scene['caption'],1515,170)
        elif kind=='checkout': draw_caption(d,scene['caption'],1510,170)
        elif kind=='summary': draw_caption(d,scene['caption'],1530,170)
        elif kind=='payment': draw_caption(d,scene['caption'],1540,170)
        elif kind=='status': draw_caption(d,scene['caption'],1580,130)
    draw_progress(d,idx,frame)
    return im.convert('RGB')

# Render and inspect representative stills for each scene.
contact=Image.new('RGB',(4*270,2*500),(16,12,14)); cd=ImageDraw.Draw(contact)
clip_paths=[]; global_frame=0
for idx,scene in enumerate(SCENES):
    middle=scene['duration']//2
    still=make_still(scene,idx,middle)
    still_path=PREVIEW/f'{idx+1:02d}-{scene["id"]}.png'
    still.save(still_path,optimize=True)
    thumb=still.resize((250,444),Image.Resampling.LANCZOS)
    col=idx%4; row=idx//4; x=col*270+10; y=row*500+8
    contact.paste(thumb,(x,y)); cd.text((x,y+448),scene['title'].replace('\n',' ')[:30],font=font(13,True),fill=WHITE)
    clip=CLIPS/f'{idx+1:02d}-{scene["id"]}.mp4'
    frames=scene['duration']; dur=frames/FPS
    # A very subtle push-in across each scene; framing remains legible.
    vf=f"zoompan=z='min(1+0.00011*on,1.025)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=1:s={W}x{H}:fps={FPS},trim=end_frame={frames},setpts=N/({FPS}*TB),format=yuv420p"
    cmd=['ffmpeg','-y','-loglevel','error','-loop','1','-framerate',str(FPS),'-i',str(still_path),'-vf',vf,'-frames:v',str(frames),'-an','-c:v','libx264','-preset','ultrafast','-crf','19','-pix_fmt','yuv420p','-r',str(FPS),str(clip)]
    subprocess.run(cmd,check=True)
    clip_paths.append(clip); global_frame+=frames
contact.save(PREVIEW/'storyboard.jpg',quality=93)
concat=ROOT/'out'/'final-concat.txt'; concat.parent.mkdir(parents=True,exist_ok=True)
concat.write_text(''.join(f"file '{p.as_posix()}'\n" for p in clip_paths),encoding='utf-8')
silent=ROOT/'out'/'final-silent.mp4'
subprocess.run(['ffmpeg','-y','-loglevel','error','-f','concat','-safe','0','-i',str(concat),'-c','copy','-movflags','+faststart',str(silent)],check=True)
# Mix clear Indonesian TTS over the quiet original instrumental bed.
final_cmd=['ffmpeg','-y','-loglevel','error','-i',str(silent),'-i',str(AUDIO/'voiceover.wav'),'-i',str(AUDIO/'music.wav'),
 '-filter_complex','[1:a]volume=1.0[voice];[2:a]volume=0.10[music];[voice][music]amix=inputs=2:duration=first:dropout_transition=1:normalize=0,alimiter=limit=0.95[a]',
 '-map','0:v:0','-map','[a]','-c:v','copy','-c:a','aac','-b:a','192k','-ar','44100','-shortest','-movflags','+faststart',str(OUT)]
subprocess.run(final_cmd,check=True)
# Save exact scene timing and render metadata.
meta={'width':W,'height':H,'fps':FPS,'frames':TOTAL_FRAMES,'duration_seconds':DURATION,'scenes':[{'id':s['id'],'frames':s['duration'],'seconds':round(s['duration']/FPS,3),'title':s['title'].replace('\n',' ')} for s in SCENES]}
(PREVIEW/'render-info.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2),encoding='utf-8')
print(f'Wrote {OUT} ({DURATION:.3f}s, {TOTAL_FRAMES} frames, {W}x{H} @ {FPS}fps)')
