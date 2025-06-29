console.log("SharedArrayBuffer available:", typeof SharedArrayBuffer !== "undefined");


import init, * as wasm from "./pkg/prezentare_licenta.js";

init({ 
  module: new URL("./pkg/prezentare_licenta.wasm", import.meta.url),
  memory: new WebAssembly.Memory({ initial: 200, maximum: 16384, shared: true })
}).then(async () => {
  console.log("WASM module initialized");
  await wasm.initThreadPool(2);

  if (wasm.wasm_main) {
    wasm.wasm_main();
    console.log("wasm_main called");
  }
});