import { readFileSync } from "fs";
import { resolve } from "path";

const BANGALORE_ICON = "https://api.mozambiquehe.re/assets/icons/bangalore.png";

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
}

interface LegendStatEntry {
  key: string;
  value: unknown;
}

interface LegendData {
  data?: LegendStatEntry[];
  ImgAssets?: { icon?: string };
}

interface ProfileRank {
  rankName?: string;
  rankDiv?: number;
  rankScore?: number;
  rankImg?: string;
  ALStopIntGlobal?: number | string;
}

interface Profile {
  global?: {
    name?: string;
    level?: number;
    rank?: ProfileRank;
    arena?: ProfileRank;
  };
  legends?: {
    all?: Record<string, LegendData>;
  };
}

function getKills(legend: LegendData): number {
  const stat = legend.data?.find((s) => s.key === "kills");
  return typeof stat?.value === "number" ? stat.value : 0;
}

function parsePlayer(profile: Profile): PlayerStats {
  let totalKills = 0;
  let topLegend: LegendStats = { name: "Bangalore", kills: 0, icon: BANGALORE_ICON };

  for (const [legendName, legendData] of Object.entries(
    profile.legends?.all ?? {}
  )) {
    const kills = getKills(legendData);
    totalKills += kills;
    if (kills > topLegend.kills) {
      topLegend = {
        name: legendName,
        kills,
        icon: legendData.ImgAssets?.icon ?? BANGALORE_ICON,
      };
    }
  }

  const rankInfo = profile.global?.rank ?? {};
  const arenaInfo = profile.global?.arena ?? {};

  return {
    playerName: profile.global?.name ?? "Unknown",
    level: profile.global?.level ?? 0,
    totalKills,
    topLegend,
    rank: {
      name: rankInfo.rankName ?? "Unranked",
      division: rankInfo.rankDiv ?? 0,
      score: rankInfo.rankScore ?? 0,
      image: rankInfo.rankImg ?? "",
      globalRankInt: rankInfo.ALStopIntGlobal ?? "—",
    },
    arenaRank: {
      name: arenaInfo.rankName ?? "Unranked",
      division: arenaInfo.rankDiv ?? 0,
      image: arenaInfo.rankImg ?? "",
    },
  };
}

export function loadPlayers(): PlayerStats[] {
  const dataPath = resolve("retriever/data/latest_profiles.json");
  const raw = readFileSync(dataPath, "utf-8");
  const profiles: Record<string, Profile> = JSON.parse(raw);

  return Object.values(profiles)
    .map(parsePlayer)
    .sort((a, b) => b.totalKills - a.totalKills);
}

