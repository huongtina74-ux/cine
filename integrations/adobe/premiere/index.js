const ppro = require("premierepro");
const uxp = require("uxp");

const TOOL_ID = "premiere";
const PLUGIN_VERSION = "1.0.0";
const CAPABILITIES = [
  "probe",
  "import media",
  "create sequence",
  "place clip",
  "trim",
  "markers",
  "audio edit",
  "effects",
  "export"
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

async function activeProject() {
  const project = await ppro.Project.getActiveProject();
  if (!project) throw new Error("No active Premiere project");
  return project;
}

async function activeSequence(project) {
  const sequence = await project.getActiveSequence();
  if (!sequence) throw new Error("No active Premiere sequence");
  return sequence;
}

async function rootItems(project) {
  const root = await project.getRootItem();
  return { root, items: await root.getItems() };
}

async function collectClipItems(folder, out = []) {
  const items = await folder.getItems();
  for (const item of items) {
    let isFolder = false;
    try {
      const childFolder = ppro.FolderItem.cast(item);
      const children = await childFolder.getItems();
      isFolder = true;
      await collectClipItems(childFolder, out);
      void children;
    } catch (_) {
      // Not a folder.
    }
    if (isFolder) continue;
    try {
      const clip = ppro.ClipProjectItem.cast(item);
      out.push(clip);
    } catch (_) {
      // Ignore non-clip items.
    }
  }
  return out;
}

async function findClipByMediaPath(project, mediaPath) {
  const root = await project.getRootItem();
  const clips = await collectClipItems(root, []);
  const normalized = String(mediaPath).toLowerCase();
  for (const clip of clips) {
    try {
      const path = await clip.getMediaFilePath();
      if (String(path).toLowerCase() === normalized) return clip;
    } catch (_) {
      // Continue.
    }
  }
  return null;
}

function executeActions(project, label, createActions) {
  let success = false;
  project.lockedAccess(() => {
    const actions = createActions();
    success = project.executeTransaction((compoundAction) => {
      for (const action of actions) compoundAction.addAction(action);
    }, label);
  });
  return success;
}

async function operationSandboxCreate(payload) {
  const projectPath = String(payload.project_path || "");
  if (!projectPath) throw new Error("sandbox create requires project_path");
  const project = await ppro.Project.createProject(projectPath);
  if (!project) throw new Error("Premiere failed to create sandbox project");
  return { project_path: project.path, project_name: project.name, guid: String(project.guid) };
}

async function operationSandboxClose(payload) {
  const project = await activeProject();
  const expected = payload.project_path ? String(payload.project_path).toLowerCase() : null;
  if (expected && String(project.path).toLowerCase() !== expected) {
    throw new Error("Refusing to close non-sandbox active project");
  }
  const options = new ppro.CloseProjectOptions()
    .setPromptIfDirty(false)
    .setSaveWorkspace(false)
    .setShowCancelButton(false)
    .setIsAppBeingPreparedToQuit(false);
  const closed = await project.close(options);
  if (!closed) throw new Error("Premiere failed to close sandbox project");
  return { closed: true, project_path: project.path };
}

async function operationProbe() {
  const project = await ppro.Project.getActiveProject();
  const sequence = project ? await project.getActiveSequence() : null;
  return {
    hostName: uxp.host.name,
    hostVersion: uxp.host.version,
    uxpVersion: uxp.versions.uxp,
    pluginVersion: uxp.versions.plugin || PLUGIN_VERSION,
    activeProject: project ? { name: project.name, path: project.path, guid: String(project.guid) } : null,
    activeSequence: sequence ? { name: sequence.name, guid: String(sequence.guid) } : null,
    capabilities: CAPABILITIES,
    delegatedOperations: { captions: "ffmpeg" }
  };
}

async function operationImportMedia(payload) {
  const project = await activeProject();
  const root = await project.getRootItem();
  const target = ppro.ProjectItem.cast(root);
  const paths = Array.isArray(payload.paths) ? payload.paths : [payload.path].filter(Boolean);
  if (!paths.length) throw new Error("import media requires path(s)");
  const ok = await project.importFiles(paths, true, target, false);
  if (!ok) throw new Error("Premiere importFiles returned false");
  return { imported: paths };
}

async function operationCreateSequence(payload) {
  const project = await activeProject();
  const root = await project.getRootItem();
  const target = ppro.ProjectItem.cast(root);
  const name = String(payload.name || "CineFactory Sequence");
  const mediaPaths = Array.isArray(payload.media_paths) ? payload.media_paths : [];
  let sequence;
  if (mediaPaths.length) {
    const clips = [];
    for (const path of mediaPaths) {
      let clip = await findClipByMediaPath(project, path);
      if (!clip) {
        const ok = await project.importFiles([path], true, target, false);
        if (!ok) throw new Error(`Failed to import ${path}`);
        clip = await findClipByMediaPath(project, path);
      }
      if (!clip) throw new Error(`Imported clip not found: ${path}`);
      clips.push(clip);
    }
    sequence = await project.createSequenceFromMedia(name, clips, target);
  } else if (payload.preset_path && typeof project.createSequenceWithPresetPath === "function") {
    sequence = await project.createSequenceWithPresetPath(name, payload.preset_path);
  } else {
    sequence = await project.createSequence(name, payload.preset_path || "");
  }
  if (!sequence) throw new Error("Premiere failed to create sequence");
  await project.setActiveSequence(sequence);
  return { name: sequence.name, guid: String(sequence.guid) };
}

async function operationPlaceClip(payload) {
  const project = await activeProject();
  const sequence = await activeSequence(project);
  const clip = await findClipByMediaPath(project, payload.media_path);
  if (!clip) throw new Error(`Clip not found: ${payload.media_path}`);
  const editor = ppro.SequenceEditor.getEditor(sequence);
  const time = ppro.TickTime.createWithSeconds(Number(payload.seconds || 0));
  const videoTrack = Number(payload.video_track || 0);
  const audioTrack = Number(payload.audio_track || 0);
  const insert = payload.mode !== "overwrite";
  const ok = executeActions(project, "CineFactory place clip", () => {
    const action = insert
      ? editor.createInsertProjectItemAction(clip, time, videoTrack, audioTrack, false)
      : editor.createOverwriteItemAction(clip, time, videoTrack, audioTrack);
    return [action];
  });
  if (!ok) throw new Error("Premiere transaction failed while placing clip");
  return { media_path: payload.media_path, seconds: time.seconds, mode: insert ? "insert" : "overwrite" };
}

async function firstVideoClip(sequence, trackIndex = 0) {
  const track = await sequence.getVideoTrack(trackIndex);
  const items = track.getTrackItems(ppro.Constants.TrackItemType.CLIP, false);
  if (!items || !items.length) throw new Error("No video clip track item found");
  return items[0];
}

async function operationTrim(payload) {
  const project = await activeProject();
  const sequence = await activeSequence(project);
  const item = await firstVideoClip(sequence, Number(payload.video_track || 0));
  const actions = [];
  const ok = executeActions(project, "CineFactory trim clip", () => {
    if (payload.in_seconds !== undefined) {
      actions.push(item.createSetInPointAction(ppro.TickTime.createWithSeconds(Number(payload.in_seconds))));
    }
    if (payload.out_seconds !== undefined) {
      actions.push(item.createSetOutPointAction(ppro.TickTime.createWithSeconds(Number(payload.out_seconds))));
    }
    if (!actions.length) throw new Error("trim requires in_seconds and/or out_seconds");
    return actions;
  });
  if (!ok) throw new Error("Premiere trim transaction failed");
  return { trimmed: true };
}

async function operationMarkers(payload) {
  const project = await activeProject();
  const sequence = await activeSequence(project);
  const markers = await ppro.Markers.getMarkers(sequence);
  const start = ppro.TickTime.createWithSeconds(Number(payload.seconds || 0));
  const duration = ppro.TickTime.createWithSeconds(Number(payload.duration_seconds || 0));
  const ok = executeActions(project, "CineFactory add marker", () => [
    markers.createAddMarkerAction(
      String(payload.name || "CineFactory"),
      String(payload.marker_type || "Comment"),
      start,
      duration,
      String(payload.comments || "")
    )
  ]);
  if (!ok) throw new Error("Premiere marker transaction failed");
  return { marker: payload.name || "CineFactory", seconds: start.seconds };
}

async function operationAudioEdit(payload) {
  const project = await activeProject();
  const sequence = await activeSequence(project);
  const index = Number(payload.audio_track || 0);
  const track = await sequence.getAudioTrack(index);
  const mute = Boolean(payload.mute);
  const ok = await track.setMute(mute);
  if (!ok) throw new Error("Premiere AudioTrack.setMute returned false");
  return { audio_track: index, muted: await track.isMuted() };
}

async function operationEffects(payload) {
  const project = await activeProject();
  const sequence = await activeSequence(project);
  const item = await firstVideoClip(sequence, Number(payload.video_track || 0));
  const matchName = String(payload.match_name || "");
  if (!matchName) throw new Error("effects requires match_name");
  const component = await ppro.VideoFilterFactory.createComponent(matchName);
  if (!component) throw new Error(`Video filter not available: ${matchName}`);
  const chain = await item.getComponentChain();
  const ok = executeActions(project, "CineFactory append effect", () => [
    chain.createAppendComponentAction(component)
  ]);
  if (!ok) throw new Error("Premiere effect transaction failed");
  return { match_name: matchName, component_count: chain.getComponentCount() };
}

async function operationExport(payload) {
  const project = await activeProject();
  const sequence = await activeSequence(project);
  const manager = ppro.EncoderManager.getManager();
  const output = String(payload.output_file || "");
  if (!output) throw new Error("export requires output_file");
  const preset = String(payload.preset_file || "");
  const ok = await manager.exportSequence(
    sequence,
    ppro.Constants.ExportType.IMMEDIATELY,
    output,
    preset,
    payload.export_full !== false
  );
  if (!ok) throw new Error("Premiere exportSequence returned false");
  return { output_file: output, preset_file: preset || null };
}

const OPERATIONS = {
  "sandbox create": operationSandboxCreate,
  "sandbox close": operationSandboxClose,
  "probe": operationProbe,
  "import media": operationImportMedia,
  "create sequence": operationCreateSequence,
  "place clip": operationPlaceClip,
  "trim": operationTrim,
  "markers": operationMarkers,
  "audio edit": operationAudioEdit,
  "effects": operationEffects,
  "export": operationExport
};

async function executeCommand(command) {
  const handler = OPERATIONS[command.operation];
  if (!handler) {
    throw new Error(`Unsupported Premiere operation: ${command.operation}`);
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
  setStatus(`Connected\nPremiere ${probe.hostVersion || "unknown"}\nBridge ${BASE_URL}`);
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
