import React from "react";

const StatsCards = ({ stats }) => {
  return (
    <div className="stats-cards">
      {Object.entries(stats).map(([key, value]) => (
        <div key={key} className="card">
          <h3>{key}</h3>
          <p>{value}</p>
        </div>
      ))}
    </div>
  );
};

export default StatsCards;
