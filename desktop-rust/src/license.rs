use std::collections::HashMap;
use std::env;
use std::fs;
use std::path::PathBuf;
use std::time::{SystemTime, UNIX_EPOCH};

use base64::engine::general_purpose::URL_SAFE_NO_PAD;
use base64::Engine;
use ed25519_dalek::{Signature, Verifier, VerifyingKey};
use sha2::{Digest, Sha256};

use crate::vault_meta::LICENSE_PUBKEY;

fn show_error_dialog(msg: &str) {
    #[cfg(target_os = "windows")]
    {
        use std::ffi::OsStr;
        use std::os::windows::ffi::OsStrExt;
        use windows_sys::Win32::UI::WindowsAndMessaging::{MessageBoxW, MB_ICONERROR, MB_OK};

        let title: Vec<u16> = OsStr::new("Junior Mission Orion - Licencia Requerida")
            .encode_wide()
            .chain(std::iter::once(0))
            .collect();
        let body: Vec<u16> = OsStr::new(msg)
            .encode_wide()
            .chain(std::iter::once(0))
            .collect();
        unsafe {
            MessageBoxW(std::ptr::null_mut(), body.as_ptr(), title.as_ptr(), MB_OK | MB_ICONERROR);
        }
    }
    #[cfg(not(target_os = "windows"))]
    {
        eprintln!("[Licencia] {msg}");
    }
}

#[cfg(target_os = "windows")]
fn read_machine_guid_sha256() -> Option<String> {
    use std::ffi::OsStr;
    use std::os::windows::ffi::OsStrExt;
    use windows_sys::Win32::System::Registry::{
        RegCloseKey, RegOpenKeyExW, RegQueryValueExW, HKEY_LOCAL_MACHINE, KEY_READ,
        KEY_WOW64_64KEY,
    };

    let subkey: Vec<u16> = OsStr::new("SOFTWARE\\Microsoft\\Cryptography")
        .encode_wide()
        .chain(std::iter::once(0))
        .collect();
    let value_name: Vec<u16> = OsStr::new("MachineGuid")
        .encode_wide()
        .chain(std::iter::once(0))
        .collect();

    let mut hkey = std::ptr::null_mut();
    let status = unsafe {
        RegOpenKeyExW(
            HKEY_LOCAL_MACHINE,
            subkey.as_ptr(),
            0,
            KEY_READ | KEY_WOW64_64KEY,
            &mut hkey,
        )
    };
    if status != 0 {
        return None;
    }

    let mut buf = [0u16; 128];
    let mut bytes_len = (buf.len() * 2) as u32;
    let q_status = unsafe {
        RegQueryValueExW(
            hkey,
            value_name.as_ptr(),
            std::ptr::null(),
            std::ptr::null_mut(),
            buf.as_mut_ptr() as *mut u8,
            &mut bytes_len,
        )
    };
    unsafe {
        RegCloseKey(hkey);
    }
    if q_status != 0 {
        return None;
    }

    let char_len = (bytes_len as usize) / 2;
    let guid = String::from_utf16_lossy(&buf[..char_len])
        .trim_end_matches('\0')
        .trim()
        .to_lowercase();
    if guid.is_empty() {
        return None;
    }

    let hash = Sha256::digest(guid.as_bytes());
    let mut hex = String::with_capacity(64);
    for b in hash {
        use std::fmt::Write;
        let _ = write!(&mut hex, "{b:02x}");
    }
    Some(hex)
}

#[cfg(not(target_os = "windows"))]
fn read_machine_guid_sha256() -> Option<String> {
    None
}

fn find_license_content() -> Option<String> {
    let mut candidates: Vec<PathBuf> = Vec::new();
    if let Ok(exe) = env::current_exe() {
        if let Some(dir) = exe.parent() {
            candidates.push(dir.join("license.key"));
        }
    }
    #[cfg(target_os = "windows")]
    if let Ok(local) = env::var("LOCALAPPDATA") {
        candidates.push(
            PathBuf::from(local)
                .join("JuniorMissionOrion")
                .join("license.key"),
        );
    }
    for path in candidates {
        if let Ok(txt) = fs::read_to_string(path) {
            let trimmed = txt.trim().to_string();
            if !trimmed.is_empty() {
                return Some(trimmed);
            }
        }
    }
    None
}

fn verify_token(token: &str) -> Result<(), String> {
    if LICENSE_PUBKEY.iter().all(|&b| b == 0) {
        return Err(
            "El binario se compilo con license-gate pero falta assets/license_pubkey.hex."
                .to_string(),
        );
    }
    let verifying_key = VerifyingKey::from_bytes(&LICENSE_PUBKEY)
        .map_err(|_| "Clave publica Ed25519 invalida.".to_string())?;

    let parts: Vec<&str> = token.trim().split('.').collect();
    if parts.len() != 3 || parts[0] != "ORION1" {
        return Err("Formato de licencia invalido (se esperaba ORION1.payload.firma).".to_string());
    }

    let payload_bytes = URL_SAFE_NO_PAD
        .decode(parts[1])
        .map_err(|_| "Payload de licencia corrupto.".to_string())?;
    let sig_bytes = URL_SAFE_NO_PAD
        .decode(parts[2])
        .map_err(|_| "Firma de licencia corrupta.".to_string())?;
    let sig_arr: [u8; 64] = sig_bytes
        .try_into()
        .map_err(|_| "Longitud de firma Ed25519 incorrecta.".to_string())?;
    let signature = Signature::from_bytes(&sig_arr);

    verifying_key
        .verify(&payload_bytes, &signature)
        .map_err(|_| "Firma criptografica de licencia no valida o alterada.".to_string())?;

    let payload_str =
        std::str::from_utf8(&payload_bytes).map_err(|_| "Payload no es UTF-8.".to_string())?;
    let mut fields: HashMap<&str, &str> = HashMap::new();
    for line in payload_str.lines() {
        if let Some((k, v)) = line.split_once('=') {
            fields.insert(k.trim(), v.trim());
        }
    }

    if fields.get("app").copied() != Some("junior-mission-orion") {
        return Err("La licencia no corresponde a Junior Mission Orion.".to_string());
    }

    if let Some(exp_str) = fields.get("exp") {
        let exp: u64 = exp_str
            .parse()
            .map_err(|_| "Campo de expiracion invalido.".to_string())?;
        if exp > 0 {
            let now = SystemTime::now()
                .duration_since(UNIX_EPOCH)
                .map(|d| d.as_secs())
                .unwrap_or(0);
            if now > exp {
                return Err("La licencia ha expirado.".to_string());
            }
        }
    }

    if let Some(&hwid) = fields.get("hwid") {
        if !hwid.is_empty() && hwid != "*" {
            let local_hwid = read_machine_guid_sha256()
                .ok_or_else(|| "No se pudo verificar el identificador del equipo.".to_string())?;
            if !local_hwid.eq_ignore_ascii_case(hwid) {
                return Err(format!(
                    "Licencia vinculada a otro equipo.\nID de este equipo (primeros 16): {}",
                    &local_hwid[..16]
                ));
            }
        }
    }

    Ok(())
}

pub fn verify_license_or_exit() {
    let Some(token) = find_license_content() else {
        let extra = read_machine_guid_sha256()
            .map(|h| format!("\nID de equipo: {}", &h[..16]))
            .unwrap_or_default();
        show_error_dialog(&format!(
            "No se encontro el archivo 'license.key' junto al ejecutable ni en %LOCALAPPDATA%\\JuniorMissionOrion\\.{extra}"
        ));
        std::process::exit(1);
    };

    if let Err(err) = verify_token(&token) {
        show_error_dialog(&err);
        std::process::exit(1);
    }
}
