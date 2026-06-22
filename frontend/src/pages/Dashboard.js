
// =====================================================
// src/pages/Dashboard.js
// =====================================================

import React, {
  useEffect,
  useState
} from "react";

import axios from "axios";

import { useNavigate } from "react-router-dom";

import "../styles/Dashboard.css";

function Dashboard() {

  const navigate = useNavigate();

  const [summary, setSummary] = useState({

    line_a: 0,
    line_b: 0,
    line_c: 0,
    line_d: 0,

    total_uid: 0,
    total_serial: 0

  });

  // ===================================================
  // LOAD DASHBOARD DATA
  // ===================================================

  useEffect(() => {

    loadDashboard();

  }, []);

  const loadDashboard = async () => {

    try {

      const response = await axios.get(

        "http://localhost:5000/api/dashboard-summary"

      );

      setSummary(response.data);

    }

    catch (error) {

      console.log(error);

    }

  };

  // ===================================================
  // NAVIGATION
  // ===================================================

  const goToLineA = () => {

    navigate("/Production");

  };

  const goToProductionLineB = () => {

    navigate("/production-line-b");

  };

  const goToProductionLineC = () => {

    navigate("/production-line-c");

  };

  const goToProductionLineD = () => {

    navigate("/production-line-d");

  };

  return (

    <div className="dashboard-container">

      <h1 className="dashboard-title">

        Dashboard

      </h1>

      {/* ========================================= */}
      {/* SUMMARY */}
      {/* ========================================= */}

      <div className="summary-container">

        <div className="summary-card">

          <h3>Total UID Today</h3>

          <span>

            {summary.total_uid}

          </span>

        </div>

        <div className="summary-card">

          <h3>Total Serial Today</h3>

          <span>

            {summary.total_serial}

          </span>

        </div>

      </div>

      {/* ========================================= */}
      {/* LINES */}
      {/* ========================================= */}

      <div className="line-grid">

        {/* LINE A */}

        <div
          className="line-card"
          onClick={goToLineA}
        >

          <h2>Line A</h2>

          <p>

            CCS2 Honda Charge Inlet

          </p>

          <div className="uid-counter">

            Today's UID

            <span>

              {summary.line_a}

            </span>

          </div>

        </div>

        {/* LINE B */}

        <div
          className="line-card"
          onClick={goToProductionLineB}
        >

          <h2>Line B</h2>

          <p>

            CCS2 Honda

          </p>

          <div className="uid-counter">

            Today's UID

            <span>

              {summary.line_b}

            </span>

          </div>

        </div>

        {/* LINE C */}

        <div
          className="line-card"
          onClick={goToProductionLineC}
        >

          <h2>Line C</h2>

          <p>

            CCS2 Honda

          </p>

          <div className="uid-counter">

            Today's UID

            <span>

              {summary.line_c}

            </span>

          </div>

        </div>

        {/* LINE D */}

        <div
          className="line-card"
          onClick={goToProductionLineD}
        >

          <h2>Line D</h2>

          <p>

            CCS2 Honda

          </p>

          <div className="uid-counter">

            Today's UID

            <span>

              {summary.line_d}

            </span>

          </div>

        </div>

      </div>

    </div>

  );

}

export default Dashboard;
