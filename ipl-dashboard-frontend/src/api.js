const BASE_URL = "http://localhost:5000"; // or your deployed backend

export async function fetchTeams() {
  const res = await fetch(`${BASE_URL}/teams`);
  return res.json();
}

export async function fetchTeamAnalytics(team) {
  const res = await fetch(`${BASE_URL}/analytics?team=${encodeURIComponent(team)}`);
  return res.json();
}

export async function fetchTeamVisuals(team) {
  const res = await fetch(`${BASE_URL}/visuals?team=${encodeURIComponent(team)}`);
  return res.json(); // contains base64 images
}

export async function fetchTopPlayers(team) {
  const res = await fetch(`${BASE_URL}/top-players?team=${encodeURIComponent(team)}`);
  return res.json(); // { top_batsmen, top_bowlers }
}


