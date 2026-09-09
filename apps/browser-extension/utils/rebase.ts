export function rebaseRows<T extends { updatedAt: number }>(
  local: T[],
  remote: T[],
  keyOf: (row: T) => string,
): T[] {
  const byKey = new Map(local.map((row) => [keyOf(row), row]));
  for (const remoteRow of remote) {
    const localRow = byKey.get(keyOf(remoteRow));
    if (!localRow || remoteRow.updatedAt > localRow.updatedAt) {
      byKey.set(keyOf(remoteRow), remoteRow);
    }
  }
  return [...byKey.values()];
}

export function rowsToPush<T extends { updatedAt: number }>(
  local: T[],
  acked: Record<string, number>,
  keyOf: (row: T) => string,
): T[] {
  return local.filter((row) => {
    const ackedAt = acked[keyOf(row)];
    return ackedAt == null || row.updatedAt > ackedAt;
  });
}
