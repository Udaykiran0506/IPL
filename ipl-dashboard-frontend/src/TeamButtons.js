import React from "react";

const TeamButtons = ({ teams, onSelect }) => {
  return (
    <div className="button-container">
      {teams.map((team) => (
        <button key={team} onClick={() => onSelect(team)} className="team-button">
          {team}
        </button>
      ))}
    </div>
  );
};

export default TeamButtons;
