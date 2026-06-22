
// =====================================================
// src/pages/SerialTraceability.js
// UID + SERIAL TRACEABILITY
// =====================================================

import React, {
  useState,
  useRef,
  useEffect
} from "react";

import axios from "axios";

import "../styles/Traceability.css";

function Traceability() {

  const serialRef = useRef(null);

  const [serialNo, setSerialNo] = useState("");

  const [traceData, setTraceData] = useState(null);

  const [traceType, setTraceType] = useState("");

  const [error, setError] = useState("");

  useEffect(() => {

    serialRef.current?.focus();

  }, []);

  // =====================================================
  // SEARCH UID OR SERIAL
  // =====================================================

  const searchTraceability = async () => {

    try {

      setError("");

      let response;

      const value = serialNo.trim();

      if (
        value.toUpperCase().startsWith("SN")
      ) {

        response = await axios.get(

          `http://localhost:5000/api/trace-serial/${value}`

        );

        setTraceType("serial");

      }

      else {

        response = await axios.get(

          `http://localhost:5000/api/trace/${value}`

        );

        setTraceType("uid");

      }

      setTraceData(
        response.data
      );

    }

    catch (err) {

      setTraceData(null);

      setError(

        err.response?.data?.error ||

        "Traceability Not Found"

      );

    }

  };

  // =====================================================
  // RENDER UID DATA
  // =====================================================

  const renderUID = (title, data) => {

    if (!data) return null;

    return (

      <div className="uid-section">

        <h2>{title}</h2>

        <div className="uid-card">

          <p>

            <strong>UID:</strong>

            {" "}

            {data.uid}

          </p>

          <p>

            <strong>Line:</strong>

            {" "}

            {data.line}

          </p>

          <p>

            <strong>Product:</strong>

            {" "}

            {data.product_name}

          </p>

          <p>

            <strong>Created:</strong>

            {" "}

            {data.created_at}

          </p>

        </div>

        {/* ========================= */}
        {/* BATCH DETAILS */}
        {/* ========================= */}

        <h3>

          Batch Details

        </h3>

        <table className="batch-table">

          <thead>

            <tr>

              <th>Component</th>

              <th>Batch</th>

              <th>Line</th>

              <th>Status</th>

              <th>Usage Station</th>

            </tr>

          </thead>

          <tbody>

            {data.batches?.map(

              (row, index) => (

                <tr key={index}>

                  <td>

                    {row.component_code}

                  </td>

                  <td>

                    {row.batch_code}

                  </td>

                  <td>

                    {row.line}

                  </td>

                  <td>

                    {row.status}

                  </td>

                  <td>

                    {row.usage_station}

                  </td>

                </tr>

              )

            )}

          </tbody>

        </table>

        {/* ========================= */}
        {/* TORQUE RESULTS */}
        {/* ========================= */}

        {

          
          data.line === "A" &&
          data.torque_results?.length > 0 && (

            <>

              <h3>

                Torque Results

              </h3>

              <div className="station-list">

                {data.torque_results.map(

                  (row, index) => (

                    <div
                      className="station-card"
                      key={index}
                    >

                      <p>

                        <strong>

                          Station:

                        </strong>

                        {" "}

                        {row.station_id}

                      </p>

                      <p>

                        <strong>

                          Torque:

                        </strong>

                        {" "}

                        {row.torque_value}

                      </p>

                      <p>

                        <strong>

                          Result:

                        </strong>

                        {" "}

                        {row.result}

                      </p>

                    </div>

                  )

                )}

              </div>

            </>

          )

        }

        {/* ========================= */}
        {/* TEST RESULTS */}
        {/* ========================= */}

        {

          data.line === "A" &&
          data.torque_results?.length > 0 && (

            <>

              <h3>

                Test Results

              </h3>

              <div className="station-list">

                {data.test_results.map(

                  (row, index) => (

                    <div
                      className="station-card"
                      key={index}
                    >

                      <p>

                        <strong>

                          Station:

                        </strong>

                        {" "}

                        {row.station_id}

                      </p>

                      <p>

                        <strong>

                          Resistance:

                        </strong>

                        {" "}

                        {row.resistance}

                      </p>

                      <p>

                        <strong>

                          Continuity:

                        </strong>

                        {" "}

                        {row.continuity}

                      </p>

                      <p>

                        <strong>

                          Actuator:

                        </strong>

                        {" "}

                        {row.actuator}

                      </p>

                      <p>

                        <strong>

                          Result:

                        </strong>

                        {" "}

                        {row.result}

                      </p>

                    </div>

                  )

                )}

              </div>

            </>

          )

        }

      </div>

    );

  };

  return (

    <div className="trace-page">

      <div className="trace-header">

        <h1>

          UID / Serial Traceability

        </h1>

      </div>

      <div className="trace-search">

        <input

          ref={serialRef}

          type="text"

          placeholder="Scan UID or Enter Serial Number"

          value={serialNo}

          onChange={(e) =>

            setSerialNo(
              e.target.value
            )

          }

          onKeyDown={(e) => {

            if (
              e.key === "Enter"
            ) {

              searchTraceability();

            }

          }}

        />

        <button
          onClick={searchTraceability}
        >

          Search

        </button>

      </div>

      {

        error && (

          <div className="error-box">

            {error}

          </div>

        )

      }

      {/* ========================= */}
      {/* SERIAL TRACE */}
      {/* ========================= */}

      {

        traceData &&
        traceType === "serial" && (

          <>

            <div className="serial-card">

              <h2>

                Serial No :

                {" "}

                {traceData.serial_no}

              </h2>

            </div>

            {

              renderUID(
                "UID LINE A",
                traceData.uid_line_a
              )

            }

            {

              renderUID(
                "UID LINE B",
                traceData.uid_line_b
              )

            }

            {

              renderUID(
                "UID LINE C",
                traceData.uid_line_c
              )

            }

            {

              renderUID(
                "UID LINE D",
                traceData.uid_line_d
              )

            }

          </>

        )

      }

      {/* ========================= */}
      {/* UID TRACE */}
      {/* ========================= */}

      {

        traceData &&
        traceType === "uid" && (

          renderUID(
            "UID DETAILS",
            traceData
          )

        )

      }

    </div>

  );

}

export default Traceability;
