const photoshop = require("photoshop");
const { app, core, action, constants } = photoshop;
const { storage, versions, host } = require("uxp");

const TOOL_ID = "photoshop";
const PLUGIN_VERSION = "1.0.0";
const CAPABILITIES = [
  "probe",
  "layers",
  "masks",
  "smart objects",
  "text",
  "composite",
  "thumbnail",
  "batch export"
];

const cfg = globalThis.CINEFACTORY_BRIDGE_CONFIG || {};
const BASE_URL = String(cfg.baseUrl || "http://127.0.0.1:8791").replace(/\/$/, "");
const TOKEN = String(cfg.token || "");
const statusNode = document.getElementById("status");

function setStatus(message) {
  if (statusNode) statusNode.textContent = String(message);
}

async function bridgeFetch(path, options = {}) {
  if (!TOKEN || TOKEN.includes("REPLACE_")) {
    throw new Error("CineFactory bridge token is not configured");
  }
  const response = await fetch(BASE_URL + path, {
    ...options,
    headers: {
      "Authorization": `Bearer ${TOKEN}`,
      "Content-Type": "application/json",
      ...(options.headers || {})
    }
  });
  if (response.status === 204) return null;
  const text = await response.text();
  const payload = text ? JSON.parse(text) : {};
  if (!response.ok) {
    throw new Error(`Bridge HTTP ${response.status}: ${text}`);
  }
  return payload;
}

function fileUrl(nativePath) {
  const normalized = String(nativePath).replace(/\\/g, "/");
  return normalized.startsWith("/")
    ? `file:${normalized}`
    : `file:/${normalized}`;
}

function activeDocument() {
  const doc = app.activeDocument;
  if (!doc) throw new Error("No active Photoshop document");
  return doc;
}

async function modal(name, fn) {
  return await core.executeAsModal(fn, { commandName: name });
}

async function operationProbe() {
  const doc = app.activeDocument || null;
  return {
    hostName: host.name,
    hostVersion: host.version,
    uxpVersion: versions.uxp,
    pluginVersion: PLUGIN_VERSION,
    activeDocument: doc ? {
      id: doc.id,
      title: doc.title,
      width: Number(doc.width),
      height: Number(doc.height)
    } : null,
    capabilities: CAPABILITIES
  };
}

async function operationSandboxCreate(payload) {
  return await modal("CineFactory create sandbox", async () => {
    const doc = await app.createDocument({
      width: Number(payload.width || 512),
      height: Number(payload.height || 512),
      resolution: 72,
      name: String(payload.name || "CineFactory Photoshop Mastery"),
      fill: "transparent"
    });
    return {
      document_id: doc.id,
      title: doc.title,
      width: Number(doc.width),
      height: Number(doc.height)
    };
  });
}

async function operationSandboxClose() {
  return await modal("CineFactory close sandbox", async () => {
    const doc = activeDocument();
    doc.closeWithoutSaving();
    return { closed: true };
  });
}

async function operationLayers(payload) {
  return await modal("CineFactory create layer", async () => {
    const doc = activeDocument();
    const layer = await doc.createLayer({
      name: String(payload.name || "CineFactory Layer"),
      opacity: Number(payload.opacity || 100)
    });
    if (!layer) throw new Error("Photoshop createLayer returned null");
    return {
      layer_id: layer.id,
      name: layer.name,
      opacity: Number(layer.opacity)
    };
  });
}

async function operationText(payload) {
  return await modal("CineFactory create text", async () => {
    const doc = activeDocument();
    const layer = await doc.createTextLayer({
      name: String(payload.name || "CineFactory Text"),
      contents: String(payload.contents || "CineFactory"),
      fontSize: Number(payload.font_size || 32),
      position: {
        x: Number(payload.x || 128),
        y: Number(payload.y || 256)
      }
    });
    if (!layer) throw new Error("Photoshop createTextLayer returned null");
    return {
      layer_id: layer.id,
      name: layer.name,
      contents: String(payload.contents || "CineFactory")
    };
  });
}

async function operationMasks() {
  return await modal("CineFactory create mask", async () => {
    const doc = activeDocument();
    if (!doc.activeLayers || !doc.activeLayers.length) {
      await doc.createLayer({ name: "CineFactory Mask Layer" });
    }
    await doc.selection.selectRectangle({
      top: 32,
      left: 32,
      bottom: Math.max(64, Number(doc.height) - 32),
      right: Math.max(64, Number(doc.width) - 32)
    });
    await action.batchPlay([
      {
        _obj: "make",
        new: { _class: "channel" },
        at: { _ref: "channel", _enum: "channel", _value: "mask" },
        using: { _enum: "userMaskEnabled", _value: "revealSelection" },
        _options: { dialogOptions: "dontDisplay" }
      }
    ], {});
    await doc.selection.deselect();
    return { mask_created: true };
  });
}

async function operationSmartObjects() {
  return await modal("CineFactory smart object", async () => {
    const doc = activeDocument();
    if (!doc.activeLayers || !doc.activeLayers.length) {
      await doc.createLayer({ name: "CineFactory Smart Layer" });
    }
    await action.batchPlay([
      {
        _obj: "newPlacedLayer",
        _options: { dialogOptions: "dontDisplay" }
      }
    ], {});
    const layer = doc.activeLayers[0];
    return {
      converted: true,
      layer_id: layer ? layer.id : null,
      layer_kind: layer ? String(layer.kind) : null
    };
  });
}

async function operationComposite() {
  return await modal("CineFactory composite", async () => {
    const doc = activeDocument();
    const base = await doc.createLayer({
      name: "CineFactory Composite Base",
      opacity: 100
    });
    const overlay = await doc.createLayer({
      name: "CineFactory Composite Overlay",
      opacity: 50,
      blendMode: constants.BlendMode.MULTIPLY
    });
    return {
      base_layer_id: base.id,
      overlay_layer_id: overlay.id,
      blend_mode: String(overlay.blendMode),
      opacity: Number(overlay.opacity)
    };
  });
}

async function operationThumbnail(payload) {
  return await modal("CineFactory thumbnail resize", async () => {
    const doc = activeDocument();
    const width = Number(payload.width || 320);
    const height = Number(payload.height || 180);
    await doc.resizeImage(width, height);
    return {
      width: Number(doc.width),
      height: Number(doc.height)
    };
  });
}

async function operationBatchExport(payload) {
  return await modal("CineFactory batch export", async () => {
    const doc = activeDocument();
    const fs = storage.localFileSystem;
    const pngPath = String(payload.png_path || "");
    const psdPath = String(payload.psd_path || "");
    if (!pngPath || !psdPath) {
      throw new Error("batch export requires png_path and psd_path");
    }
    const pngEntry = await fs.createEntryWithUrl(
      fileUrl(pngPath),
      { overwrite: true }
    );
    const psdEntry = await fs.createEntryWithUrl(
      fileUrl(psdPath),
      { overwrite: true }
    );
    await doc.saveAs.png(pngEntry, {}, true);
    await doc.saveAs.psd(psdEntry, {}, true);
    return {
      artifacts: [pngPath, psdPath],
      png_path: pngPath,
      psd_path: psdPath
    };
  });
}

const OPERATIONS = {
  "sandbox create": operationSandboxCreate,
  "sandbox close": operationSandboxClose,
  "probe": operationProbe,
  "layers": operationLayers,
  "masks": operationMasks,
  "smart objects": operationSmartObjects,
  "text": operationText,
  "composite": operationComposite,
  "thumbnail": operationThumbnail,
  "batch export": operationBatchExport
};

async function executeCommand(command) {
  const handler = OPERATIONS[command.operation];
  if (!handler) {
    throw new Error(`Unsupported Photoshop operation: ${command.operation}`);
  }
  return await handler(command.payload || {});
}

async function register() {
  const probe = await operationProbe();
  await bridgeFetch("/v1/register", {
    method: "POST",
    body: JSON.stringify({
      tool_id: TOOL_ID,
      host_version: String(probe.hostVersion || ""),
      plugin_version: PLUGIN_VERSION,
      capabilities: CAPABILITIES
    })
  });
  setStatus(
    `Connected\nPhotoshop ${probe.hostVersion || "unknown"}\nBridge ${BASE_URL}`
  );
}

async function pollOnce() {
  const command = await bridgeFetch(
    `/v1/commands/next?tool_id=${encodeURIComponent(TOOL_ID)}`
  );
  if (!command) return;
  let result;
  try {
    const payload = await executeCommand(command);
    result = {
      command_id: command.command_id,
      tool_id: TOOL_ID,
      operation: command.operation,
      ok: true,
      payload
    };
  } catch (error) {
    result = {
      command_id: command.command_id,
      tool_id: TOOL_ID,
      operation: command.operation,
      ok: false,
      payload: {},
      error: String(error && error.stack ? error.stack : error)
    };
  }
  await bridgeFetch("/v1/results", {
    method: "POST",
    body: JSON.stringify(result)
  });
}

async function mainLoop() {
  while (true) {
    try {
      await register();
      await pollOnce();
    } catch (error) {
      setStatus(`Bridge error\n${String(error)}`);
    }
    await new Promise((resolve) => setTimeout(resolve, 500));
  }
}

mainLoop();
