#[inline(always)]
fn load_le_u32(b: &[u8]) -> u32 {
    u32::from_le_bytes([b[0], b[1], b[2], b[3]])
}

#[inline(always)]
fn load_le_u64(b: &[u8]) -> u64 {
    u64::from_le_bytes([b[0], b[1], b[2], b[3], b[4], b[5], b[6], b[7]])
}

#[inline(always)]
fn qr(s: &mut [u32; 16], a: usize, b: usize, c: usize, d: usize) {
    s[a] = s[a].wrapping_add(s[b]);
    s[d] = (s[d] ^ s[a]).rotate_left(16);
    s[c] = s[c].wrapping_add(s[d]);
    s[b] = (s[b] ^ s[c]).rotate_left(12);
    s[a] = s[a].wrapping_add(s[b]);
    s[d] = (s[d] ^ s[a]).rotate_left(8);
    s[c] = s[c].wrapping_add(s[d]);
    s[b] = (s[b] ^ s[c]).rotate_left(7);
}

pub fn chacha20_block(key: &[u8; 32], counter: u32, nonce: &[u8; 12]) -> [u8; 64] {
    let mut st = [0u32; 16];
    st[0] = 0x6170_7865;
    st[1] = 0x3320_646e;
    st[2] = 0x7962_2d32;
    st[3] = 0x6b20_6574;
    for i in 0..8 {
        st[4 + i] = load_le_u32(&key[i * 4..i * 4 + 4]);
    }
    st[12] = counter;
    st[13] = load_le_u32(&nonce[0..4]);
    st[14] = load_le_u32(&nonce[4..8]);
    st[15] = load_le_u32(&nonce[8..12]);

    let mut w = st;
    for _ in 0..10 {
        qr(&mut w, 0, 4, 8, 12);
        qr(&mut w, 1, 5, 9, 13);
        qr(&mut w, 2, 6, 10, 14);
        qr(&mut w, 3, 7, 11, 15);
        qr(&mut w, 0, 5, 10, 15);
        qr(&mut w, 1, 6, 11, 12);
        qr(&mut w, 2, 7, 8, 13);
        qr(&mut w, 3, 4, 9, 14);
    }

    let mut out = [0u8; 64];
    for i in 0..16 {
        let word = w[i].wrapping_add(st[i]).to_le_bytes();
        out[i * 4..i * 4 + 4].copy_from_slice(&word);
    }
    out
}

pub fn chacha20_xor(key: &[u8; 32], nonce: &[u8; 12], data: &[u8], start_counter: u32) -> Vec<u8> {
    let mut out = Vec::with_capacity(data.len());
    out.resize(data.len(), 0);
    let mut ctr = start_counter;
    let mut off = 0usize;
    while off < data.len() {
        let mut blk = chacha20_block(key, ctr, nonce);
        ctr = ctr.wrapping_add(1);
        let lim = (data.len() - off).min(64);
        for j in 0..lim {
            out[off + j] = data[off + j] ^ blk[j];
        }
        zeroize_slice(&mut blk);
        off += lim;
    }
    out
}

pub fn compute_mac256(
    mac_key: &[u8; 32],
    nonce: &[u8; 12],
    orig_len: u64,
    ciphertext: &[u8],
) -> [u8; 32] {
    let mut st = [
        load_le_u64(&mac_key[0..8]) ^ 0x736f_6d65_7073_6575,
        load_le_u64(&mac_key[8..16]) ^ 0x646f_7261_6e64_6f6d,
        load_le_u64(&mac_key[16..24]) ^ 0x6c79_6765_6e65_7261,
        load_le_u64(&mac_key[24..32]) ^ 0x7465_6462_7974_6573,
    ];

    let mix = |s: &mut [u64; 4], w: u64| {
        s[0] = s[0].wrapping_add(w).wrapping_mul(0x9E37_79B9_7F4A_7C15);
        s[1] = (s[1] ^ s[0]).rotate_left(17).wrapping_add(s[2]);
        s[2] = s[2].wrapping_add(s[3]).rotate_left(29) ^ w;
        s[3] = (s[3] ^ s[1]).rotate_left(41).wrapping_mul(0xBF58_476D_1CE4_E5B9);
    };

    let mut hdr = [0u8; 24];
    hdr[0..12].copy_from_slice(nonce);
    hdr[12..20].copy_from_slice(&orig_len.to_le_bytes());
    for chunk in hdr.chunks_exact(8) {
        mix(&mut st, load_le_u64(chunk));
    }

    let mut it = ciphertext.chunks_exact(8);
    for chunk in &mut it {
        mix(&mut st, load_le_u64(chunk));
    }
    let rem = it.remainder();
    let mut tail = [0u8; 8];
    tail[..rem.len()].copy_from_slice(rem);
    tail[7] ^= (rem.len() as u8).wrapping_mul(0x5A);
    mix(&mut st, load_le_u64(&tail));

    for r in 0..8u64 {
        mix(&mut st, r ^ (ciphertext.len() as u64).rotate_left(13));
    }

    let mut out = [0u8; 32];
    for i in 0..4 {
        out[i * 8..i * 8 + 8].copy_from_slice(&st[i].to_le_bytes());
    }
    out
}

#[inline(never)]
pub fn zeroize_slice(buf: &mut [u8]) {
    for b in buf.iter_mut() {
        unsafe {
            core::ptr::write_volatile(b as *mut u8, 0);
        }
    }
    core::sync::atomic::compiler_fence(core::sync::atomic::Ordering::SeqCst);
}

pub fn ct_eq(a: &[u8], b: &[u8]) -> bool {
    if a.len() != b.len() {
        return false;
    }
    let mut diff = 0u8;
    for (&x, &y) in a.iter().zip(b.iter()) {
        diff |= x ^ y;
    }
    diff == 0
}
