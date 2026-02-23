import { readFileSync } from "fs";
import { resolve } from "path";

export interface LegendStats {
  name: string;
  kills: number;
  icon: string;
}

export interface RankInfo {
  name: string;
  division: number;
  score: number;
  image: string;
  globalRankInt: number | string;
}

export interface ArenaRankInfo {
  name: string;
  division: number;
  image: string;
}

export interface PlayerStats {
  playerName: string;
  level: number;
  totalKills: number;
  topLegend: LegendStats;
  rank: RankInfo;
  arenaRank: ArenaRankInfo;
  collectedAtUtc: string;
}

export function loadPlayers(): PlayerStats[] {
  const dataPath = resolve("retriever/data/latest_profiles.json");
  const raw = readFileSync(dataPath, "utf-8");
  const players = JSON.parse(raw) as PlayerStats[];
  return [...players].sort((a, b) => b.totalKills - a.totalKills);
}
