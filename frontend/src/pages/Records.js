// =====================================================
// src/pages/Records.js
// FULL FINAL WORKING CODE
// =====================================================

import React, {
  useState,
  useEffect,
  useCallback
} from "react";

import axios from "axios";

import "../styles/Records.css";

function Records() {

  // ===================================================
  // STATES
  // ===================================================

  const [records, setRecords] = useState([]);

  const [fromDate, setFromDate] = useState("");

  const [toDate, setToDate] = useState("");

  const [uid, setUid] = useState("");

  const [message, setMessage] = useState("");

  const [loading, setLoading] = useState(false);

  // ===================================================
  // LOAD RECORDS
  // ===================================================

  const loadRecords = useCallback(async () => {

    try {

      setLoading(true);

      const response = await axios.get(

        "http://localhost:5000/api/get-records",

        {

          params: {

            from_date: fromDate,

            to_date: toDate,

            uid: uid

          }

        }

      );

      setRecords(response.data);

      setLoading(false);

    }

    catch(error) {

      setLoading(false);

      setMessage(

        error.response?.data?.error ||

        "Failed To Load Records"

      );

      setTimeout(() => {

        setMessage("");

      }, 3000);

    }

  }, [fromDate, toDate, uid]);

  // ===================================================
  // AUTO LOAD
  // ===================================================

  useEffect(() => {

    loadRecords();

  }, [loadRecords]);

  // ===================================================
  // RESET FILTER
  // ===================================================

  const resetFilters = () => {

    setFromDate("");

    setToDate("");

    setUid("");

  };

  // ===================================================
  // JSX
  // ===================================================

  return (

    <div className="records-page">

      {/* ========================================= */}
      {/* HEADER */}
      {/* ========================================= */}

      <div className="records-header">

        <h1>

          Production Records

        </h1>

      </div>

      {/* ========================================= */}
      {/* FILTER SECTION */}
      {/* ========================================= */}

      <div className="filter-container">

        {/* FROM DATE */}

        <div className="filter-box">

          <label>

            From Date

          </label>

          <input
            type="date"
            value={fromDate}
            onChange={(e) =>
              setFromDate(e.target.value)
            }
          />

        </div>

        {/* TO DATE */}

        <div className="filter-box">

          <label>

            To Date

          </label>

          <input
            type="date"
            value={toDate}
            onChange={(e) =>
              setToDate(e.target.value)
            }
          />

        </div>

        {/* UID */}

        <div className="filter-box uid-box">

          <label>

            UID

          </label>

          <input
            type="text"
            placeholder="Search UID"
            value={uid}
            onChange={(e) =>
              setUid(
                e.target.value.toUpperCase()
              )
            }
          />

        </div>

        {/* BUTTONS */}

        <div className="filter-buttons">

          <button
            className="search-btn"
            onClick={loadRecords}
          >

            SEARCH

          </button>

          <button
            className="reset-btn"
            onClick={resetFilters}
          >

            RESET

          </button>

        </div>

      </div>

      {/* ========================================= */}
      {/* MESSAGE */}
      {/* ========================================= */}

      {

        message && (

          <div className="message-box">

            {message}

          </div>

        )

      }

      {/* ========================================= */}
      {/* LOADING */}
      {/* ========================================= */}

      {

        loading && (

          <div className="loading-text">

            Loading Records...

          </div>

        )

      }

      {/* ========================================= */}
      {/* TABLE */}
      {/* ========================================= */}

      <div className="table-container">

        <table>

          <thead>

            <tr>

              <th>UID</th>

              <th>Line</th>

              <th>Product</th>

              <th>Torque</th>

              <th>Torque Result</th>

              <th>Resistance</th>

              <th>Continuity</th>

              <th>Actuator</th>

              <th>Electrical Result</th>

              <th>Date & Time</th>

            </tr>

          </thead>

          <tbody>

            {

              records.length > 0

              ?

              records.map((item, index) => (

                <tr key={index}>

                  {/* UID */}

                  <td>

                    {item.uid}

                  </td>

                  {/* LINE */}

                  <td>

                    {item.line}

                  </td>

                  {/* PRODUCT */}

                  <td>

                    {item.product_name}

                  </td>

                  {/* TORQUE */}

                  <td>

                    {item.torque_value}

                  </td>

                  {/* TORQUE RESULT */}

                  <td>

                    <span
                      className={
                        item.torque_result === "OK"

                        ?

                        "ok-status"

                        :

                        "ng-status"
                      }
                    >

                      {item.torque_result}

                    </span>

                  </td>

                  {/* RESISTANCE */}

                  <td>

                    {item.resistance}

                  </td>

                  {/* CONTINUITY */}

                  <td>

                    {item.continuity}

                  </td>

                  {/* ACTUATOR */}

                  <td>

                    {item.actuator}

                  </td>

                  {/* ELECTRICAL RESULT */}

                  <td>

                    <span
                      className={
                        item.electrical_result === "OK"

                        ?

                        "ok-status"

                        :

                        "ng-status"
                      }
                    >

                      {item.electrical_result}

                    </span>

                  </td>

                  {/* DATE TIME */}

                  <td>

                    {item.created_at}

                  </td>

                </tr>

              ))

              :

              (

                <tr>

                  <td
                    colSpan="10"
                    style={{
                      textAlign: "center",
                      padding: "30px"
                    }}
                  >

                    No Records Found

                  </td>

                </tr>

              )

            }

          </tbody>

        </table>

      </div>

    </div>

  );

}

export default Records;