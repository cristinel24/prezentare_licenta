console.log("SharedArrayBuffer available:", typeof SharedArrayBuffer !== "undefined");

import init, * as wasm from "./pkg/prezentare_licenta.js";

init().then(() => {
  console.log("WASM module initialized");
  
  if (wasm.wasm_main) {
    wasm.wasm_main();
    console.log("wasm_main called");
  }
}).catch(error => {
  console.error("Failed to initialize WASM:", error);
});