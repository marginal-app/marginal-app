export function bumpUpdatedAt(lastUpdatedAt: number, now = Date.now()): number {
  return Math.max(now, lastUpdatedAt + 1);
}
