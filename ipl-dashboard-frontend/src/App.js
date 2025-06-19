import React, { useEffect, useState } from "react";
import {
  fetchTeams,
  fetchTeamAnalytics,
  fetchTeamVisuals,
  fetchTopPlayers
} from "./api";
import StatsCards from "./StatsCards";
import "./App.css";

function App() {
  const [teams, setTeams] = useState([]);
  const [filteredTeams, setFilteredTeams] = useState([]);
  const [selectedTeam, setSelectedTeam] = useState("All Teams");
  const [analytics, setAnalytics] = useState({});
  const [visuals, setVisuals] = useState(null);
  const [topPlayers, setTopPlayers] = useState({ top_batsmen: [], top_bowlers: [] });
  const [loading, setLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(false);
  const [searchTerm, setSearchTerm] = useState("");

  useEffect(() => {
    fetchTeams().then((data) => {
      setTeams(data);
      setFilteredTeams(data);
    });
  }, []);

  useEffect(() => {
    if (selectedTeam) {
      setLoading(true);
      Promise.all([
        fetchTeamAnalytics(selectedTeam),
        fetchTeamVisuals(selectedTeam),
        fetchTopPlayers(selectedTeam)
      ])
        .then(([analyticsData, visualsData, playersData]) => {
          setAnalytics(analyticsData);
          setVisuals(visualsData);
          setTopPlayers(playersData);
          setLoading(false);
        })
        .catch(err => {
          console.error("Error loading data", err);
          setLoading(false);
        });
    }
  }, [selectedTeam]);

  const getTeamLogoPath = (team) => {
    const filename = team.replace(/ /g, "_") + ".png";
    return `/logos/${filename}`;
  };

  const handleSearch = (e) => {
    const value = e.target.value.toLowerCase();
    setSearchTerm(value);
    const filtered = teams.filter(team => team.toLowerCase().includes(value));
    setFilteredTeams(filtered);
  };

  return (
    <div className={`App ${darkMode ? "dark-mode" : ""}`} style={{ padding: "20px" }}>
      <h1 style={{ textAlign: "center" }}>🏏 IPL Team Analytics Dashboard</h1>

      <div style={{ textAlign: "center", marginBottom: "15px" }}>
        <button
          onClick={() => setDarkMode(!darkMode)}
          style={{
            padding: "8px 16px",
            borderRadius: "20px",
            background: darkMode ? "#f3f4f6" : "#1e293b",
            color: darkMode ? "#1e293b" : "#fff",
            border: "none",
            cursor: "pointer"
          }}
        >
          {darkMode ? "☀️ Light Mode" : "🌙 Dark Mode"}
        </button>
      </div>

      <div style={{ textAlign: "center", marginBottom: "20px" }}>
        <input
          type="text"
          placeholder="Search team..."
          value={searchTerm}
          onChange={handleSearch}
          style={{
            padding: "10px",
            width: "60%",
            maxWidth: "300px",
            borderRadius: "8px",
            border: "1px solid #ccc",
            outline: "none"
          }}
        />
      </div>

      {/* Team Logo Grid */}
      <div className="logo-grid">
        {filteredTeams.map((team) => (
          <div
            key={team}
            className={`logo-card ${selectedTeam === team ? "active" : ""}`}
            onClick={() => setSelectedTeam(team)}
          >
            <img
              src={getTeamLogoPath(team)}
              alt={team}
              onError={(e) => {
                e.target.onerror = null;
                e.target.src = "/logos/All_Teams.png";
              }}
            />
            <p>{team}</p>
          </div>
        ))}
      </div>

      {loading && <p style={{ textAlign: "center" }}>Loading data...</p>}

      {!loading && analytics && <StatsCards stats={analytics} />}

      {!loading && topPlayers && (
        <div style={{ marginTop: "30px" }}>
          <h2>Top Batsmen</h2>
          <div className="flex-wrap-grid">
            {topPlayers.top_batsmen.map(player => (
              <div key={player.name} className="stat-card">
                <strong>{player.name}</strong>
                <p>{player.runs} Runs</p>
              </div>
            ))}
          </div>

          <h2 style={{ marginTop: "30px" }}>Top Bowlers</h2>
          <div className="flex-wrap-grid">
            {topPlayers.top_bowlers.map(player => (
              <div key={player.name} className="stat-card">
                <strong>{player.name}</strong>
                <p>{player.wickets} Wickets</p>
              </div>
            ))}
          </div>
        </div>
      )}

      {!loading && visuals && (
        <div className="visual-section">
          <h2 style={{ textAlign: "center" }}>Team Visualizations</h2>
          {Object.entries(visuals).map(([title, img]) => (
            <div key={title} style={{ marginBottom: "25px", textAlign: "center" }}>
              <h3>{title.replace(/_/g, " ").toUpperCase()}</h3>
              <img src={`data:image/png;base64,${img}`} alt={title} width="90%" />
            </div>
          ))}
        </div>
      )}

    <footer style={{ textAlign: "center", marginTop: "40px", fontSize: "14px", color: "#6b7280" }}>
        © 2025 IPL Analytics Dashboard by <strong>VVS UDAY KIRAN</strong>
      </footer>
    </div>
  );
}

export default App;
