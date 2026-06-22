// src/components/Navbar.js

import React from "react";
import "./Navbar.css";
import Logo from "../assets/Logo.jpg";

function Navbar() {
  return (
    <div className="navbar">

  <div className="navbar-container">

    <div className="logo-section">

      <img
        src={Logo}
        alt="Logo"
        className="logo-img"
      />

      <div className="navbar-logo">
        Traceability System
      </div>

    </div>

     <ul className="navbar-links">
        <li><a href="/dashboard">Dashboard</a></li>
        <li><a href="/scan-batch">Scan Batch</a></li>
        <li><a href="/Production">Production</a></li>
        <li><a href="/traceability">Traceability</a></li>
        <li><a href="/records">Records</a></li>
        <li><a href="/components">Components</a></li>
        <li><a href="/final-serial">Final Serial</a></li>
      </ul>


  </div>

</div>
  );
}

export default Navbar;