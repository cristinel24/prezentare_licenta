use std::env;
use std::fs;
use std::path::Path;

fn main() {
    let out_dir = env::var("OUT_DIR").unwrap();
    let dest_path = Path::new(&out_dir).join("slides.rs");

    let slides_dir = "src/surfaces";

    let mut slide_files = Vec::new();

    if let Ok(entries) = fs::read_dir(slides_dir) {
        let entries = entries.flatten();
        for entry in entries {
            let path = entry.path();
            if path.extension().and_then(|s| s.to_str()) == Some("srf") {
                if let Some(file_name) = path.file_name().and_then(|s| s.to_str()) {
                    slide_files.push(file_name.to_string());
                }
            }
        }
    }

    slide_files.sort();

    let mut code = String::new();
    code.push_str("pub fn get_slides() -> Vec<Vec<u8>> {\n");
    code.push_str("    vec![\n");

    for file in &slide_files {
        code.push_str(&format!(
            "        include_bytes!(\"D:/licenta/prezentare_licenta/src/surfaces/{}\").to_vec(),\n",
            file
        ));
    }

    code.push_str("    ]\n");
    code.push_str("}\n");

    fs::write(&dest_path, code).unwrap();

    println!("cargo:rerun-if-changed=src/slides");
}
