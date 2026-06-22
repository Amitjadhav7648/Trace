
// =====================================================
// src/pages/FinalSerial.js
// =====================================================

import React, {
  useState,
  useEffect,
  useRef
} from "react";

import axios from "axios";

import "../styles/FinalSerial.css";

function FinalSerial() {

  const [serialNo, setSerialNo] = useState("");

  const [uidA, setUidA] = useState("");

  const [uidB, setUidB] = useState("");

  const [uidC, setUidC] = useState("");

  const [uidD, setUidD] = useState("");

  const [message, setMessage] = useState("");

  const uidARef = useRef(null);
  const uidBRef = useRef(null);

const uidCRef = useRef(null);

const uidDRef = useRef(null);

  // ==========================================
  // LOAD LATEST TESTER SERIAL
  // ==========================================

 useEffect(() => {

  fetchLatestSerial();

  const interval = setInterval(() => {

    fetchLatestSerial();

  }, 3000); // every 3 seconds

  return () => clearInterval(interval);

}, []);


  useEffect(() => {

  if (uidARef.current) {

    uidARef.current.focus();

  }

}, []);

  const fetchLatestSerial = async () => {

    try {

      const response = await axios.get(

        "http://localhost:5000/api/get-latest-serial"

      );

      setSerialNo(
        response.data.serial_no
      );

    }

    catch (error) {

      console.log(error);

    }

  };

  // ==========================================
  // SAVE TRACEABILITY
  // ==========================================

  const saveTraceability = async () => {

    try {

      const response = await axios.post(

        "http://localhost:5000/api/save-final-serial",

        {

          uid_line_a: uidA,

          uid_line_b: uidB,

          uid_line_c: uidC,

          uid_line_d: uidD

        }

      );

      alert(
        response.data.message
      );
      window.location.reload();

      setMessage(
        response.data.message
      );

      // Clear fields

      setUidA("");
      setUidB("");
      setUidC("");
      setUidD("");

      // Reload latest serial

      fetchLatestSerial();

      // Focus first field

      setTimeout(() => {

  if (uidARef.current) {

    uidARef.current.focus();

  }

}, 100);

    }

    catch (error) {

      alert(

        error.response?.data?.error ||

        "Save Failed"

      );

    }

  };

  return (

    <div className="final-page">

      <div className="final-card">

        <h1>

          Final Serial Traceability

        </h1>

        {/* ================================= */}
        {/* SERIAL NUMBER */}
        {/* ================================= */}

        

        {/* ================================= */}
        {/* UID SCANS */}
        {/* ================================= */}

        <div className="uid-grid">

          <div className="input-group">

            <label>

              UID Line A

            </label>

            <input
  ref={uidARef}
  type="text"
  placeholder="Scan UID A"
  value={uidA}
  onChange={(e) =>
    setUidA(e.target.value)
  }
  onKeyDown={(e) => {

    if (e.key === "Enter") {

      uidBRef.current.focus();

    }

  }}
/>

          </div>

          <div className="input-group">

            <label>

              UID Line B

            </label>

            <input
  ref={uidBRef}
  type="text"
  placeholder="Scan UID B"
  value={uidB}
  onChange={(e) =>
    setUidB(e.target.value)
  }
  onKeyDown={(e) => {

    if (e.key === "Enter") {

      uidCRef.current.focus();

    }

  }}
/>

          </div>

          <div className="input-group">

            <label>

              UID Line C

            </label>

            <input
  ref={uidCRef}
  type="text"
  placeholder="Scan UID C"
  value={uidC}
  onChange={(e) =>
    setUidC(e.target.value)
  }
  onKeyDown={(e) => {

    if (e.key === "Enter") {

      uidDRef.current.focus();

    }

  }}
/>

          </div>

          <div className="input-group">

            <label>

              UID Line D

            </label>

            <input
  ref={uidDRef}
  type="text"
  placeholder="Scan UID D"
  value={uidD}
  onChange={(e) =>
    setUidD(e.target.value)
  }
/>

          </div>

          <div className="input-group">

          <label>

            Latest Tester Serial

          </label>

          <input
            type="text"
            value={serialNo}
            readOnly
          />

        </div>

        </div>

        {/* ================================= */}
        {/* SAVE BUTTON */}
        {/* ================================= */}

        <button
          className="save-btn"
          onClick={saveTraceability}
        >

          Save Traceability

        </button>

        {/* ================================= */}
        {/* MESSAGE */}
        {/* ================================= */}

        {

          message && (

            <div className="success-msg">

              {message}

            </div>

          )

        }

      </div>

    </div>

  );

}

export default FinalSerial;
