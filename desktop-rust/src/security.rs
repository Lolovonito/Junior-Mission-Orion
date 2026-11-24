use std::env;
use std::time::Duration;

/// Elimina variables de entorno que permiten inyectar depuración remota en WebView2.
pub fn sanitize_webview_env() {
    for var in [
        "WEBVIEW2_ADDITIONAL_BROWSER_ARGUMENTS",
        "WEBVIEW2_BROWSER_EXECUTABLE_FOLDER",
        "WEBVIEW2_USER_DATA_FOLDER",
        "WEBVIEW2_RELEASE_CHANNEL_PREFERENCE",
    ] {
        env::remove_var(var);
    }
}

/// Genera un sello aleatorio por ejecución (128 bits en hexadecimal) para vincular el JS al binario nativo.
pub fn generate_runtime_seal() -> String {
    let mut bytes = [0u8; 16];
    if getrandom::getrandom(&mut bytes).is_err() {
        bytes = [
            0x4f, 0x72, 0x69, 0x6f, 0x6e, 0x53, 0x65, 0x61, 0x6c, 0x32, 0x30, 0x32, 0x36, 0x56,
            0x32, 0x39,
        ];
    }
    let mut out = String::with_capacity(32);
    for b in bytes {
        use std::fmt::Write;
        let _ = write!(&mut out, "{b:02x}");
    }
    out
}

#[cfg(all(target_os = "windows", not(debug_assertions)))]
pub fn debugger_detected() -> bool {
    use std::ffi::c_void;
    use windows_sys::Win32::Foundation::BOOL;
    use windows_sys::Win32::System::Diagnostics::Debug::{
        CheckRemoteDebuggerPresent, IsDebuggerPresent,
    };
    use windows_sys::Win32::System::LibraryLoader::{GetModuleHandleW, GetProcAddress};
    use windows_sys::Win32::System::Threading::GetCurrentProcess;

    type NtQueryInfoFn = unsafe extern "system" fn(
        process_handle: *mut c_void,
        process_information_class: u32,
        process_information: *mut c_void,
        process_information_length: u32,
        return_length: *mut u32,
    ) -> i32;

    unsafe {
        if IsDebuggerPresent() != 0 {
            return true;
        }

        let proc_handle = GetCurrentProcess();
        let mut remote_dbg: BOOL = 0;
        if CheckRemoteDebuggerPresent(proc_handle, &mut remote_dbg) != 0 && remote_dbg != 0 {
            return true;
        }

        // Resolución dinámica en ntdll.dll para ProcessDebugPort (7),
        // ProcessDebugObjectHandle (0x1e) y ProcessDebugFlags (0x1f).
        let ntdll_utf16: [u16; 10] = [
            b'n' as u16,
            b't' as u16,
            b'd' as u16,
            b'l' as u16,
            b'l' as u16,
            b'.' as u16,
            b'd' as u16,
            b'l' as u16,
            b'l' as u16,
            0,
        ];
        let h_ntdll = GetModuleHandleW(ntdll_utf16.as_ptr());
        if !h_ntdll.is_null() {
            if let Some(proc) = GetProcAddress(h_ntdll, b"NtQueryInformationProcess\0".as_ptr()) {
                let nt_query: NtQueryInfoFn = std::mem::transmute(proc);

                let mut debug_port: usize = 0;
                let mut ret_len: u32 = 0;
                if nt_query(
                    proc_handle,
                    7,
                    &mut debug_port as *mut _ as *mut c_void,
                    std::mem::size_of::<usize>() as u32,
                    &mut ret_len,
                ) == 0
                    && debug_port != 0
                {
                    return true;
                }

                let mut debug_obj: usize = 0;
                if nt_query(
                    proc_handle,
                    0x1e,
                    &mut debug_obj as *mut _ as *mut c_void,
                    std::mem::size_of::<usize>() as u32,
                    &mut ret_len,
                ) == 0
                    && debug_obj != 0
                {
                    return true;
                }

                let mut debug_flags: u32 = 1;
                if nt_query(
                    proc_handle,
                    0x1f,
                    &mut debug_flags as *mut _ as *mut c_void,
                    std::mem::size_of::<u32>() as u32,
                    &mut ret_len,
                ) == 0
                    && debug_flags == 0
                {
                    return true;
                }
            }
        }
    }
    false
}

#[cfg(not(all(target_os = "windows", not(debug_assertions))))]
pub fn debugger_detected() -> bool {
    false
}

pub fn enforce_anti_debug_or_exit() {
    if debugger_detected() {
        std::process::exit(0);
    }
}

pub fn start_watchdog_thread() {
    #[cfg(all(target_os = "windows", not(debug_assertions)))]
    {
        std::thread::spawn(|| loop {
            std::thread::sleep(Duration::from_secs(4));
            if debugger_detected() {
                std::process::exit(0);
            }
        });
    }
    #[cfg(not(all(target_os = "windows", not(debug_assertions))))]
    {
        let _ = Duration::from_secs(4);
    }
}
