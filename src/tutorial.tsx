import React from 'react';
import {
  AbsoluteFill,
  Audio,
  Composition,
  Img,
  Sequence,
  interpolate,
  spring,
  staticFile,
  useCurrentFrame,
  useVideoConfig,
} from 'remotion';

type FocusBox = { left: number; top: number; width: number; height: number };
type SceneData = {
  id: string;
  step: string;
  title: string;
  subtitle: string;
  caption: string;
  asset: string;
  voice: string;
  duration: number;
  kind: 'intro' | 'catalog' | 'options' | 'checkout' | 'summary' | 'payment' | 'status' | 'outro';
  imageBox?: FocusBox;
  focus?: FocusBox[];
  badge?: string;
};

const scenes: SceneData[] = [
  {
    id: 'intro', step: 'PANDUAN PEMESANAN', title: 'CARA MEMESAN JERSEY\nGASTON.YK',
    subtitle: 'Panduan singkat berdasarkan tampilan website asli',
    caption: 'Mau pesan jersey GASTON YK? Ikuti panduan singkat ini.',
    asset: 'catalog-grid.png', voice: 'voice-01-intro.wav', duration: 189, kind: 'intro',
    imageBox: { left: 82, top: 505, width: 916, height: 678 },
  },
  {
    id: 'catalog', step: 'LANGKAH 01 / 06', title: 'Buka Store dan pilih produk',
    subtitle: 'Ketik alamat website, lalu buka menu Store.',
    caption: 'Buka gaston.sevenpion.web.id. Pilih Store untuk melihat koleksi.',
    asset: 'catalog-store.png', voice: 'voice-02-catalog.wav', duration: 261, kind: 'catalog',
    imageBox: { left: 95, top: 420, width: 890, height: 960 },
    focus: [{ left: 425, top: 480, width: 130, height: 62 }, { left: 390, top: 1260, width: 110, height: 82 }],
  },
  {
    id: 'options', step: 'LANGKAH 02 / 06', title: 'Atur pilihan produk',
    subtitle: 'Ikuti opsi yang tampil pada produk yang kamu pilih.',
    caption: 'Pilih produk, tekan Beli, lalu atur ukuran. Nama punggung opsional, maksimal 10 huruf. Tentukan jumlah dan tekan Beli Langsung.',
    asset: 'product-modal.png', voice: 'voice-03-options.wav', duration: 307, kind: 'options',
    imageBox: { left: 130, top: 420, width: 820, height: 1070 },
    focus: [
      { left: 172, top: 805, width: 585, height: 112 },
      { left: 172, top: 988, width: 735, height: 108 },
      { left: 172, top: 1150, width: 270, height: 100 },
      { left: 172, top: 1335, width: 735, height: 108 },
    ],
    badge: 'CONTOH MODAL BELI LANGSUNG',
  },
  {
    id: 'checkout', step: 'LANGKAH 03 / 06', title: 'Isi data pembeli',
    subtitle: 'Gunakan nama dan nomor WhatsApp yang aktif.',
    caption: 'Isi nama lengkap dan nomor WhatsApp aktif. Catatan tambahan boleh dikosongkan.',
    asset: 'checkout-fields.png', voice: 'voice-04-checkout.wav', duration: 167, kind: 'checkout',
    imageBox: { left: 170, top: 420, width: 740, height: 1070 },
    focus: [{ left: 200, top: 780, width: 680, height: 275 }],
  },
  {
    id: 'summary', step: 'LANGKAH 04 / 06', title: 'Periksa pesanan',
    subtitle: 'Pastikan semua detail dan total sudah benar.',
    caption: 'Cek produk, ukuran, nama, jumlah, dan total. Jika benar, tekan Konfirmasi Pesanan.',
    asset: 'order-summary.png', voice: 'voice-05-summary.wav', duration: 186, kind: 'summary',
    imageBox: { left: 90, top: 470, width: 900, height: 1046 },
    focus: [{ left: 195, top: 1210, width: 690, height: 140 }],
  },
  {
    id: 'payment', step: 'LANGKAH 05 / 06', title: 'Selesaikan pembayaran',
    subtitle: 'Ikuti instruksi pada halaman pembayaran.',
    caption: 'Di halaman QRIS, cek nominal dan batas waktu. Bayar hanya dengan QRIS pesananmu sendiri. QRIS di video ini disamarkan.',
    asset: 'payment-example.png', voice: 'voice-06-payment.wav', duration: 175, kind: 'payment',
    imageBox: { left: 175, top: 440, width: 730, height: 1088 },
    focus: [{ left: 205, top: 855, width: 670, height: 540 }],
    badge: 'CONTOH QRIS • BUKAN UNTUK PEMBAYARAN',
  },
  {
    id: 'status', step: 'LANGKAH 06 / 06', title: 'Pantau status pesanan',
    subtitle: 'Status diperbarui setelah pembayaran terverifikasi.',
    caption: 'Setelah pembayaran terverifikasi, simpan kode pesanan dan pantau statusnya.',
    asset: 'status-example.png', voice: 'voice-07-status.wav', duration: 140, kind: 'status',
    imageBox: { left: 160, top: 430, width: 760, height: 1133 },
    focus: [{ left: 195, top: 1010, width: 690, height: 300 }],
    badge: 'CONTOH TAMPILAN STATUS',
  },
  {
    id: 'outro', step: 'SELESAI', title: 'Selesai, tinggal pantau!',
    subtitle: 'Simpan kode pesanan untuk memudahkan pengecekan.',
    caption: 'Untuk pengambilan atau pengiriman, hubungi admin sesuai petunjuk website. Selesai!',
    asset: 'catalog-grid.png', voice: 'voice-08-outro.wav', duration: 226, kind: 'outro',
    imageBox: { left: 60, top: 510, width: 500, height: 370 },
  },
];
const totalFrames = scenes.reduce((sum, scene) => sum + scene.duration, 0);

const Focus: React.FC<{ box: FocusBox; frame: number; index: number }> = ({ box, frame, index }) => {
  const pulse = interpolate(Math.sin((frame + index * 8) / 8), [-1, 1], [0.58, 1]);
  return <div style={{
    position: 'absolute', left: box.left, top: box.top, width: box.width, height: box.height,
    border: `4px solid rgba(255, 105, 66, ${pulse})`, borderRadius: 18,
    boxShadow: '0 0 24px rgba(255, 105, 66, .18)', pointerEvents: 'none',
  }} />;
};

const BrandHeader: React.FC<{ scene: SceneData; index: number }> = ({ scene, index }) => (
  <>
    <div style={{ position: 'absolute', left: 58, top: 34, width: 62, height: 62, borderRadius: 31,
      border: '2px solid rgba(255,247,243,.9)', display: 'flex', alignItems: 'center', justifyContent: 'center',
      fontSize: 40, fontWeight: 900, color: '#fffaf7' }}>G</div>
    <div style={{ position: 'absolute', left: 136, top: 37, fontSize: 28, fontWeight: 900, letterSpacing: 1.2, color: '#fffaf7' }}>GASTON.YK</div>
    <div style={{ position: 'absolute', left: 138, top: 72, fontSize: 14, letterSpacing: 2.2, color: '#c8b7b9' }}>OFFICIAL STORE</div>
    <div style={{ position: 'absolute', left: 58, top: 124, padding: '12px 22px', borderRadius: 30,
      background: '#32151b', border: '2px solid #764037', color: '#ffb18f', fontSize: 17, fontWeight: 850, letterSpacing: 1 }}>
      {scene.step}
    </div>
  </>
);

const CaptionCard: React.FC<{ text: string; top: number; height: number }> = ({ text, top, height }) => (
  <div style={{ position: 'absolute', left: 58, top, width: 964, height, boxSizing: 'border-box',
    padding: '22px 30px 20px 38px', borderRadius: 24, background: 'rgba(22, 15, 18, .97)',
    border: '2px solid #63362f', boxShadow: '0 18px 40px rgba(0,0,0,.22)', color: '#faf7f4',
    display: 'flex', alignItems: 'center' }}>
    <div style={{ position: 'absolute', left: 0, top: 22, bottom: 22, width: 7, background: '#ff704b', borderRadius: 4 }} />
    <div style={{ fontSize: 25, fontWeight: 650, lineHeight: 1.28 }}>{text}</div>
  </div>
);

const Badge: React.FC<{ text: string }> = ({ text }) => (
  <div style={{ position: 'absolute', left: 180, top: 378, width: 720, minHeight: 48, padding: '8px 18px',
    boxSizing: 'border-box', borderRadius: 24, background: '#32151b', border: '2px solid #8a4739',
    color: '#ffc18f', fontSize: 17, fontWeight: 900, letterSpacing: 1, textAlign: 'center',
    display: 'flex', justifyContent: 'center', alignItems: 'center' }}>{text}</div>
);

const OutroChecklist: React.FC = () => (
  <>
    {[
      { n: '01', title: 'SIMPAN KODE', desc: 'Simpan kode pesananmu.' },
      { n: '02', title: 'PANTAU STATUS', desc: 'Cek pembaruan pesanan.' },
      { n: '03', title: 'HUBUNGI ADMIN', desc: 'Atur pengambilan atau pengiriman.' },
    ].map((item, i) => (
      <div key={item.n} style={{ position: 'absolute', left: 590, top: 510 + i * 150, width: 430, height: 126,
        boxSizing: 'border-box', padding: '18px 20px', display: 'flex', alignItems: 'center', gap: 18,
        borderRadius: 22, background: '#1c1417', border: '2px solid #65372f' }}>
        <div style={{ width: 62, height: 62, flexShrink: 0, borderRadius: 18, background: '#ff704b',
          display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 22, fontWeight: 900, color: '#1c1012' }}>{item.n}</div>
        <div>
          <div style={{ fontSize: 21, fontWeight: 900, color: '#fffaf7' }}>{item.title}</div>
          <div style={{ marginTop: 8, fontSize: 18, lineHeight: 1.25, color: '#cdbbbc' }}>{item.desc}</div>
        </div>
      </div>
    ))}
    <div style={{ position: 'absolute', left: 60, top: 1030, width: 960, height: 245, boxSizing: 'border-box',
      padding: '28px 34px', borderRadius: 26, background: '#32151b', border: '2px solid #804337' }}>
      <div style={{ fontSize: 22, fontWeight: 900, color: '#f5b05b', letterSpacing: 1 }}>BUTUH BANTUAN?</div>
      <div style={{ marginTop: 16, fontSize: 27, lineHeight: 1.28, color: '#fffaf7' }}>
        Ikuti petunjuk website atau hubungi admin GASTON.YK untuk pengambilan dan pengiriman.
      </div>
      <div style={{ marginTop: 22, fontSize: 22, fontWeight: 850, color: '#ffb18f' }}>gaston.sevenpion.web.id</div>
    </div>
  </>
);

const SceneView: React.FC<{ scene: SceneData; index: number }> = ({ scene, index }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();
  const enter = spring({ frame, fps, config: { damping: 22, stiffness: 90, mass: 0.8 } });
  const fade = interpolate(frame, [0, 10, scene.duration - 8, scene.duration], [0, 1, 1, 0], { extrapolateLeft: 'clamp', extrapolateRight: 'clamp' });
  const zoom = interpolate(frame, [0, scene.duration - 1], [1, 1.035], { extrapolateRight: 'clamp' });
  const drift = interpolate(frame, [0, Math.min(24, scene.duration - 1)], [24, 0], { extrapolateRight: 'clamp' });
  const progress = (index + frame / scene.duration) / scenes.length;
  const titleSize = scene.kind === 'intro' ? 63 : scene.title.length > 23 ? 54 : 60;
  const titleTop = scene.kind === 'intro' ? 215 : 220;
  const subtitleTop = scene.kind === 'intro' ? 365 : 312;
  const imageBox = scene.imageBox;
  const captionTop = scene.kind === 'catalog' ? 1410 : scene.kind === 'options' ? 1515 : scene.kind === 'checkout' ? 1510 : scene.kind === 'summary' ? 1530 : scene.kind === 'payment' ? 1540 : scene.kind === 'status' ? 1580 : 0;
  const captionHeight = scene.kind === 'status' ? 130 : 170;

  return (
    <AbsoluteFill style={{ background: 'radial-gradient(ellipse at 56% 46%, #42131b 0%, #210b11 49%, #08080a 100%)', color: '#faf7f4', fontFamily: 'Inter, Arial, sans-serif', overflow: 'hidden' }}>
      <div style={{ position: 'absolute', inset: 0, opacity: 0.12,
        backgroundImage: 'radial-gradient(rgba(255,255,255,.8) 1px, transparent 1px)', backgroundSize: '54px 54px' }} />
      <AbsoluteFill style={{ opacity: fade }}>
        <BrandHeader scene={scene} index={index} />
        <div style={{ position: 'absolute', left: 58, right: 58, top: titleTop, fontSize: titleSize, lineHeight: 1.02,
          fontWeight: 950, letterSpacing: -1.6, whiteSpace: 'pre-line', transform: `translateY(${drift + (1 - enter) * 10}px)` }}>
          {scene.title}
        </div>
        <div style={{ position: 'absolute', left: 62, right: 62, top: subtitleTop, fontSize: 27, lineHeight: 1.28, color: '#cdbbbc' }}>
          {scene.subtitle}
        </div>

        {scene.kind === 'intro' && imageBox && (
          <>
            <div style={{ position: 'absolute', ...imageBox, borderRadius: 28, background: '#f6f2ee', border: '3px solid #f17e5b', overflow: 'hidden', boxShadow: '0 28px 60px rgba(0,0,0,.3)' }}>
              <Img src={staticFile(`assets/${scene.asset}`)} style={{ width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${zoom})`, transformOrigin: 'center center' }} />
            </div>
            <div style={{ position: 'absolute', left: 60, top: 1240, width: 960, height: 118, borderRadius: 24,
              background: '#32151b', border: '2px solid #804337', display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 27, fontWeight: 850, color: '#f8f3ef', letterSpacing: 0.5 }}>
              {scene.caption}
            </div>
          </>
        )}

        {scene.kind === 'catalog' && imageBox && (
          <>
            <div style={{ position: 'absolute', ...imageBox, borderRadius: 24, background: '#f6f2ee', border: '3px solid #f17e5b', overflow: 'hidden', boxShadow: '0 24px 50px rgba(0,0,0,.28)' }}>
              <Img src={staticFile(`assets/${scene.asset}`)} style={{ width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${zoom}) translateY(${interpolate(frame, [0, scene.duration], [0, -5], { extrapolateRight: 'clamp' })}px)`, transformOrigin: 'center center' }} />
            </div>
            {scene.focus?.map((box, i) => <Focus key={i} box={box} frame={frame} index={i} />)}
            <CaptionCard text={scene.caption} top={captionTop} height={170} />
          </>
        )}

        {scene.kind === 'options' && imageBox && (
          <>
            <div style={{ position: 'absolute', ...imageBox, borderRadius: 24, background: '#f6f2ee', border: '3px solid #f17e5b', overflow: 'hidden', boxShadow: '0 24px 50px rgba(0,0,0,.28)' }}>
              <Img src={staticFile(`assets/${scene.asset}`)} style={{ width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${zoom})`, transformOrigin: 'center center' }} />
            </div>
            {scene.focus?.map((box, i) => <Focus key={i} box={box} frame={frame} index={i} />)}
            {scene.badge && <Badge text={scene.badge} />}
            <CaptionCard text={scene.caption} top={captionTop} height={captionHeight} />
          </>
        )}

        {scene.kind === 'checkout' && imageBox && (
          <>
            <div style={{ position: 'absolute', ...imageBox, borderRadius: 24, background: '#f6f2ee', border: '3px solid #f17e5b', overflow: 'hidden', boxShadow: '0 24px 50px rgba(0,0,0,.28)' }}>
              <Img src={staticFile(`assets/${scene.asset}`)} style={{ width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${zoom})`, transformOrigin: 'center center' }} />
            </div>
            {scene.focus?.map((box, i) => <Focus key={i} box={box} frame={frame} index={i} />)}
            <CaptionCard text={scene.caption} top={captionTop} height={captionHeight} />
          </>
        )}

        {scene.kind === 'summary' && imageBox && (
          <>
            <div style={{ position: 'absolute', ...imageBox, borderRadius: 24, background: '#f6f2ee', border: '3px solid #f17e5b', overflow: 'hidden', boxShadow: '0 24px 50px rgba(0,0,0,.28)' }}>
              <Img src={staticFile(`assets/${scene.asset}`)} style={{ width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${zoom})`, transformOrigin: 'center center' }} />
            </div>
            {scene.focus?.map((box, i) => <Focus key={i} box={box} frame={frame} index={i} />)}
            <CaptionCard text={scene.caption} top={captionTop} height={captionHeight} />
          </>
        )}

        {scene.kind === 'payment' && imageBox && (
          <>
            {scene.badge && <Badge text={scene.badge} />}
            <div style={{ position: 'absolute', ...imageBox, borderRadius: 24, background: '#f6f2ee', border: '3px solid #f17e5b', overflow: 'hidden', boxShadow: '0 24px 50px rgba(0,0,0,.28)' }}>
              <Img src={staticFile(`assets/${scene.asset}`)} style={{ width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${zoom})`, transformOrigin: 'center center' }} />
            </div>
            {scene.focus?.map((box, i) => <Focus key={i} box={box} frame={frame} index={i} />)}
            <CaptionCard text={scene.caption} top={captionTop} height={captionHeight} />
          </>
        )}

        {scene.kind === 'status' && imageBox && (
          <>
            {scene.badge && <Badge text={scene.badge} />}
            <div style={{ position: 'absolute', ...imageBox, borderRadius: 24, background: '#f6f2ee', border: '3px solid #f17e5b', overflow: 'hidden', boxShadow: '0 24px 50px rgba(0,0,0,.28)' }}>
              <Img src={staticFile(`assets/${scene.asset}`)} style={{ width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${zoom})`, transformOrigin: 'center center' }} />
            </div>
            {scene.focus?.map((box, i) => <Focus key={i} box={box} frame={frame} index={i} />)}
            <CaptionCard text={scene.caption} top={captionTop} height={captionHeight} />
          </>
        )}

        {scene.kind === 'outro' && imageBox && (
          <>
            <div style={{ position: 'absolute', ...imageBox, borderRadius: 24, background: '#f6f2ee', border: '3px solid #f17e5b', overflow: 'hidden', boxShadow: '0 24px 50px rgba(0,0,0,.28)' }}>
              <Img src={staticFile(`assets/${scene.asset}`)} style={{ width: '100%', height: '100%', objectFit: 'cover', transform: `scale(${zoom})`, transformOrigin: 'center center' }} />
            </div>
            <OutroChecklist />
            <CaptionCard text={scene.caption} top={1400} height={170} />
          </>
        )}

        <div style={{ position: 'absolute', left: 58, right: 58, bottom: 70, height: 7, borderRadius: 5, background: 'rgba(255,255,255,.16)' }}>
          <div style={{ height: 7, width: `${Math.max(0, Math.min(100, progress * 100))}%`, borderRadius: 5, background: '#ff704b' }} />
        </div>
        <div style={{ position: 'absolute', left: 58, bottom: 30, fontSize: 17, color: '#b7a2a4', letterSpacing: 0.4 }}>GASTON.YK  •  gaston.sevenpion.web.id</div>
      </AbsoluteFill>
    </AbsoluteFill>
  );
};

export const Tutorial: React.FC = () => {
  let from = 0;
  return (
    <AbsoluteFill>
      <Audio src={staticFile('audio/music.wav')} volume={0.13} />
      {scenes.map((scene, index) => {
        const start = from;
        from += scene.duration;
        return <Sequence key={scene.id} from={start} durationInFrames={scene.duration}>
          <SceneView scene={scene} index={index} />
          <Audio src={staticFile(`audio/${scene.voice}`)} volume={1} />
        </Sequence>;
      })}
    </AbsoluteFill>
  );
};

export const Root: React.FC = () => (
  <Composition id="GastonTutorial" component={Tutorial} durationInFrames={totalFrames} fps={30} width={1080} height={1920} />
);
