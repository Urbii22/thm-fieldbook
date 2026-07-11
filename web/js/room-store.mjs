export const ROOMS_KEY = "thm-rooms:v1";
export const ACTIVE_KEY = "thm-rooms:active";
export const MIGRATED_KEY = "thm-rooms:migrated";
export const LEGACY_KEY = "thm-room";
export const SCHEMA_VERSION = 1;

const now = () => new Date().toISOString();
const id = () => `room-${Date.now().toString(36)}-${Math.random().toString(36).slice(2, 8)}`;

export function createStorageAdapter(storage = globalThis.localStorage) {
  return {
    get(key) { try { return storage?.getItem(key) ?? null; } catch { return null; } },
    set(key, value) { try { storage?.setItem(key, value); return true; } catch { return false; } },
    remove(key) { try { storage?.removeItem(key); return true; } catch { return false; } },
  };
}

export function normalizeRoom(value = {}) {
  const input = value && typeof value === "object" ? value : {};
  const createdAt = input.createdAt || now();
  return {
    version: SCHEMA_VERSION,
    id: String(input.id || id()),
    name: String(input.name || "Room sin nombre"),
    createdAt,
    updatedAt: input.updatedAt || createdAt,
    targetIp: String(input.targetIp ?? input.ip ?? ""),
    attackerIp: String(input.attackerIp ?? input.attacker ?? ""),
    domain: String(input.domain || ""),
    dcHost: String(input.dcHost || ""),
    dcFqdn: String(input.dcFqdn || ""),
    ports: String(input.ports ?? input.port ?? ""),
    user: String(input.user || ""),
    credentialType: String(input.credentialType || ""),
    notes: String(input.notes || ""),
    progress: { ...(input.progress || {}) },
    checks: { ...(input.checks || {}) },
    reverseShellPreferences: {
      ...(input.reverseShellPreferences || {}),
      ...(input.revType ? { type: String(input.revType) } : {}),
      ...(input.revLport ? { lport: String(input.revLport) } : {}),
    },
  };
}

export function migrateLegacyRoom(legacy, options = {}) {
  const source = legacy && typeof legacy === "object" ? legacy : {};
  return normalizeRoom({
    ...source,
    id: options.id,
    name: options.name || source.name || "Room migrada",
    targetIp: source.targetIp ?? source.ip,
    attackerIp: source.attackerIp ?? source.attacker,
  });
}

export function parseRooms(raw) {
  if (!raw) return [];
  const parsed = typeof raw === "string" ? JSON.parse(raw) : raw;
  if (Array.isArray(parsed)) return parsed.map(normalizeRoom);
  if (parsed && Array.isArray(parsed.rooms)) return parsed.rooms.map(normalizeRoom);
  throw new Error("Formato de rooms invalido");
}

export function validateImport(value, { maxBytes = 1024 * 1024 } = {}) {
  const text = typeof value === "string" ? value : JSON.stringify(value);
  if (text.length > maxBytes) throw new Error("Import demasiado grande");
  let parsed;
  try { parsed = typeof value === "string" ? JSON.parse(value) : value; } catch { throw new Error("JSON de import invalido"); }
  if (parsed?.version != null && parsed.version !== SCHEMA_VERSION) throw new Error("Version de import no soportada");
  const rooms = parseRooms(parsed);
  const ids = new Set();
  for (const room of rooms) {
    if (room.version !== SCHEMA_VERSION) throw new Error("Version de room no soportada");
    if (ids.has(room.id)) throw new Error("IDs de room duplicados");
    ids.add(room.id);
  }
  return rooms;
}

export function createRoomStore({ storage, sessionStorage, legacyKey = LEGACY_KEY } = {}) {
  const adapter = storage?.get ? storage : createStorageAdapter(storage || globalThis.localStorage);
  const session = sessionStorage?.get ? sessionStorage : createStorageAdapter(sessionStorage || globalThis.sessionStorage);
  const read = () => { try { return parseRooms(adapter.get(ROOMS_KEY)); } catch { return []; } };
  const write = (rooms) => adapter.set(ROOMS_KEY, JSON.stringify(rooms.map(normalizeRoom)));
  const list = () => read();
  const activeId = () => adapter.get(ACTIVE_KEY);
  const setActive = (roomId) => { if (!read().some((r) => r.id === roomId)) throw new Error("Room inexistente"); adapter.set(ACTIVE_KEY, roomId); return roomId; };
  const create = (data = {}) => { const room = normalizeRoom(data); const rooms = read(); rooms.push(room); if (!activeId()) adapter.set(ACTIVE_KEY, room.id); if (!write(rooms)) throw new Error("No se pudo guardar la room"); return room; };
  const update = (roomId, patch) => { const rooms = read(); const i = rooms.findIndex((r) => r.id === roomId); if (i < 0) throw new Error("Room inexistente"); rooms[i] = normalizeRoom({ ...rooms[i], ...patch, id: roomId, updatedAt: now() }); if (!write(rooms)) throw new Error("No se pudo guardar la room"); return rooms[i]; };
  const remove = (roomId) => { const rooms = read().filter((r) => r.id !== roomId); if (!write(rooms)) throw new Error("No se pudo guardar la room"); if (activeId() === roomId) adapter.remove(ACTIVE_KEY); return true; };
  const duplicate = (roomId, name) => { const source = read().find((r) => r.id === roomId); if (!source) throw new Error("Room inexistente"); return create({ ...source, id: undefined, name: name || `${source.name} (copia)` }); };
  const migrate = () => { if (adapter.get(MIGRATED_KEY)) return null; const raw = adapter.get(legacyKey); if (!raw) { adapter.set(MIGRATED_KEY, "1"); return null; } let legacy; try { legacy = JSON.parse(raw); } catch { return null; } const room = create(migrateLegacyRoom(legacy)); adapter.set(MIGRATED_KEY, "1"); return room; };
  const exportData = (roomId = activeId()) => { const room = read().find((r) => r.id === roomId); if (!room) throw new Error("Room inexistente"); return JSON.stringify({ version: SCHEMA_VERSION, rooms: [room] }, null, 2); };
  const importData = (value, { activate = false } = {}) => {
    const validated = validateImport(value);
    const rooms = read();
    const existingIds = new Set(rooms.map((room) => room.id));
    const incoming = validated.map((room) => existingIds.has(room.id) ? normalizeRoom({ ...room, id: undefined, name: `${room.name} (importada)` }) : room);
    if (!write([...rooms, ...incoming])) throw new Error("No se pudo guardar la importacion");
    if (activate && incoming[0]) setActive(incoming[0].id);
    return incoming;
  };
  return { list, activeId, setActive, create, update, remove, duplicate, migrate, export: exportData, import: importData, storage: adapter, sessionStorage: session };
}

export function secretStorageKey(roomId) { return `thm-room-secret:${roomId}`; }
