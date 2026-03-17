// src/App.tsx
import React from "react";
import MapComponent from "./components/MapComponent";

const App: React.FC = () => {
  return (
    <div className="App">
      <header className="navbar">
        <div className="logo">OutbreakX</div>
        <nav>
          <ul className="nav-links">
            <li>
              <a href="#tracker">Disease Tracker</a>
            </li>
          </ul>
        </nav>
      </header>
      <section id="tracker">
        <MapComponent />
      </section>
    </div>
  );
};

export default App;
