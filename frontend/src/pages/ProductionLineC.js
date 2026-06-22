// =====================================================
// src/pages/Production.js
// FRONTEND FOR FULL PRODUCTION FLOW
// =====================================================

import React, {
  useRef,
  useEffect,
  useState,
  useCallback
} from "react";

import axios from "axios";
import { useNavigate } from "react-router-dom";

import "../styles/Production.css";


function ProductionLineC() {

  // ===================================================
  // REFS
  // ===================================================

  const station1UIDRef = useRef(null);

  // ===================================================
  // COMMON
  // ===================================================
  const navigate = useNavigate();
  const [line, setLine] = useState("C");
  const [message, setMessage] = useState("");
const [batches, setBatches] = useState([]);
const [selectedBatches, setSelectedBatches] = useState([]);

const [productId, setProductId] = useState("");
const [products, setProducts] = useState([]);
const [currentStation] = useState(1);

// =====================================================
// STATES
// ADD INSIDE Production.js
// =====================================================

const [showRejectLogin, setShowRejectLogin] = useState(false);

const [adminUsername, setAdminUsername] = useState("");

const [adminPassword, setAdminPassword] = useState("");

const [rejectReason, setRejectReason] = useState("");

  // ===================================================
  // STATION 1
  // ===================================================
  
  const [finishedBatches, setFinishedBatches] = useState([]);

  const [uid, setUid] = useState("");

  const [barcode, setBarcode] = useState("");

  const [station1UID, setStation1UID] = useState("");

  const [tableData, setTableData] = useState([]);

  const [station1Done, setStation1Done] = useState(false);



const loadProducts = async () => {

  try {

    const response = await axios.get(
      "http://localhost:5000/api/get-products"
    );

    setProducts(response.data);

  }

  catch(error) {

    console.log(error);

  }

};

// ===================================================
// AUTO HIDE MESSAGE
// ===================================================

useEffect(() => {

  if (message) {

    const timer = setTimeout(() => {

      setMessage("");

    }, 3000);

    return () => clearTimeout(timer);

  }

}, [message]);

useEffect(() => {

  loadProducts();

}, []);

// =====================================================
// OPEN LOGIN WINDOW
// =====================================================

const openRejectWindow = () => {

  setShowRejectLogin(true);

};

const fetchFinishedBatches = useCallback(async () => {

  if (!productId) return;

  try {

    const response = await axios.get(
      "http://localhost:5000/api/finished-batches-alert",
      {
        params: {
          line,
          product_id: productId
        }
      }
    );

    setFinishedBatches(response.data || []);

  }
  catch(error) {

    console.log(error);

    setFinishedBatches([]);

  }

}, [line, productId]);

useEffect(() => {

  fetchFinishedBatches();

  const interval = setInterval(() => {

    fetchFinishedBatches();

  }, 3000);

  return () => clearInterval(interval);

}, [fetchFinishedBatches]);

// =====================================================
// REJECT BATCH WITH ADMIN LOGIN
// =====================================================

const rejectBatch = async () => {

  try {

    await axios.post(

      "http://localhost:5000/api/reject-batch",

      {

        batch_ids:
        selectedBatches,

        reject_reason:
        rejectReason,

        username:
        adminUsername,

        password:
        adminPassword

      }

    );

    alert(

          `${selectedBatches.length} Batch Rejected Successfully`

    );

    // ===========================================
    // CLOSE WINDOW
    // ===========================================

    setShowRejectLogin(false);

    setAdminUsername("");

    setAdminPassword("");

    setRejectReason("");

    fetchBatches();

  }

  catch (error) {

    alert(

      error.response?.data?.error ||

      "Reject Failed"

    );

  }

};

//========================
//Fetch Batches
//========================
const fetchBatches = useCallback(async () => {

  try {

    const response = await axios.get(
      "http://localhost:5000/api/get-batches",
      {
        params: {
          line,
          product_id: productId
        }
      }
    );

    setBatches(response.data || []);

  }

  catch(error) {

    console.log(error);

  }

}, [line, productId]);

useEffect(() => {

  fetchBatches();

}, [fetchBatches]);

  // ===================================================
  // CREATE UID
  // ===================================================
const createUID = async () => {

try {


// ==========================================
// CREATE UID
// ==========================================

const response = await axios.post(

  "http://localhost:5000/api/line-c/create-uid",

  {
    line: line,
    product_id: productId
  }

);

const generatedUID = response.data.uid;

// ==========================================
// SET UID
// ==========================================

setUid(generatedUID);

setStation1UID(generatedUID);

// ==========================================
// BARCODE
// ==========================================

setBarcode(

  `http://localhost:5000/${response.data.barcode}`

);

// ==========================================
// AUTO MAP BATCHES
// ==========================================

const mapResponse = await axios.post(

  "http://localhost:5000/api/station-1",

  {
    uid: generatedUID
  }

);

// ==========================================
// TABLE DATA
// ==========================================

setTableData(
  mapResponse.data.table
);

// ==========================================
// STATION DONE
// ==========================================

setStation1Done(true);

// ==========================================
// MESSAGE
// ==========================================

setMessage(
  "UID Created Successfully"
);



}

catch (error) {


// ==========================================
// FINISHED BATCH ERROR
// ==========================================

if (

  error.response?.data?.finished_batches

) {

  const finishedBatches =

    error.response.data.finished_batches;

  let msg = "Replace Finished Batches\n";

finishedBatches.forEach((item) => {

  msg +=
    `${item.component_code} - ${item.batch_code}\n`;

});

setMessage(msg);

}

// ==========================================
// NORMAL ERROR
// ==========================================

else {

  setMessage(

    error.response?.data?.error ||

    "UID Create Failed"

  );

}

}

};

  
//======================================
//Refresh Button
//======================================

const refreshStation1 = () => {

  // =====================================
  // CLEAR UID
  // =====================================

  setUid("");

  setStation1UID("");

  // =====================================
  // CLEAR BARCODE
  // =====================================

  setBarcode("");

  // =====================================
  // CLEAR TABLE
  // =====================================

  setTableData([]);

  // =====================================
  // HIDE MAP BUTTON
  // =====================================



  // =====================================
  // RESET DONE
  // =====================================

  setStation1Done(false);

  // =====================================
  // CLEAR MESSAGE
  // =====================================

  setMessage("");

  // =====================================
  // AUTO FOCUS
  // =====================================

  setTimeout(() => {

    if (station1UIDRef.current) {

      station1UIDRef.current.focus();

    }

  }, 200);

};


const handleBatchSelection = (batchId) => {

  if (selectedBatches.includes(batchId)) {

    setSelectedBatches(

      selectedBatches.filter(
        (id) => id !== batchId
      )

    );

  }

  else {

    setSelectedBatches([

      ...selectedBatches,

      batchId

    ]);

  }

};
  // ===================================================
  // PRINT
  // ===================================================
  const printUID = () => {

  const barcodeImage = document.getElementById(
    "print-barcode-image"
  ).src;

  const uidText = document.getElementById(
    "print-uid-text"
  ).innerText;

  const printWindow = window.open(
    "",
    "",
    "width=400,height=600"
  );

  printWindow.document.write(`

    <html>

      <head>

        <title>
          Print
        </title>

        <style>

          @media print {

            @page {
              margin: 0;
              size: auto;
            }

            body {
              margin: 0;
            }

          }

          body {

            display: flex;
            justify-content: center;
            align-items: center;
            flex-direction: column;

            height: 100vh;

            font-family: Arial;

            overflow: hidden;

          }

          h2 {

            margin-bottom: 10px;
            font-size: 18px;

          }

          img {

            width: 280px;

          }

        </style>

      </head>

      <body>

        <h2>${uidText}</h2>

        <img src="${barcodeImage}" />

        <script>

          window.onload = function() {

            window.print();

            window.onafterprint = function() {

              window.close();

            }

          }

        </script>

      </body>

    </html>

  `);

  printWindow.document.close();

};
  // ===================================================
  // JSX
  // ===================================================

  return (

    <div className="production-page">
        <div className="top-header">
          
  <h1>

    Production Line C

  </h1>
  <div className="production-buttons">

  <button
  className="reject-btn"
  onClick={openRejectWindow}
>
  Reject
</button>

{
  showRejectLogin && (

    <div className="reject-popup-overlay">

      <div className="reject-popup">

        <h2>

          Reject Batch

        </h2>

        {/* ===================================== */}
        {/* SELECT BATCH */}
        {/* ===================================== */}
<div className="batch-selection-list">

  {

    (batches || []).map((item) =>(

      <label
        key={item.batch_id}
        className="batch-checkbox"
      >

        <input
          type="checkbox"

          checked={selectedBatches.includes(
            item.batch_id
          )}

          onChange={() =>
            handleBatchSelection(
              item.batch_id
            )
          }
        />

        {item.batch_code}
        {" - "}
        {item.component_code}

      </label>

    ))

  }

</div>

        {/* ===================================== */}
        {/* USERNAME */}
        {/* ===================================== */}

        <input
          type="text"
          placeholder="Username"
          value={adminUsername}
          onChange={(e) =>
            setAdminUsername(e.target.value)
          }
        />

        {/* ===================================== */}
        {/* PASSWORD */}
        {/* ===================================== */}

        <input
          type="password"
          placeholder="Password"
          value={adminPassword}
          onChange={(e) =>
            setAdminPassword(e.target.value)
          }
        />

        {/* ===================================== */}
        {/* REASON */}
        {/* ===================================== */}

        <textarea
          placeholder="Reject Reason"
          value={rejectReason}
          onChange={(e) =>
            setRejectReason(e.target.value)
          }
        />

        {/* ===================================== */}
        {/* BUTTONS */}
        {/* ===================================== */}

        <div className="popup-buttons">

          <button
            className="confirm-btn"
            onClick={rejectBatch}
          >

            Confirm Reject

          </button>

          <button
            className="cancel-btn"
            onClick={() =>
              setShowRejectLogin(false)
            }
          >

            Cancel

          </button>

        </div>

      </div>

    </div>

  )
}
</div>

  {/* ===================================== */}
  {/* RIGHT SIDE */}
  {/* ===================================== */}
<div className="header-right">

  {/* LINE */}

  <select

  value={line}

  onChange={(e) => {

    const selectedLine = e.target.value;

    setLine(selectedLine);

    // =========================================
    // NAVIGATION
    // =========================================

    if (selectedLine === "A") {

      navigate("/production");

    }

    else if (selectedLine === "B") {

      navigate("/production-line-b");

    }

    else if (selectedLine === "C") {

      navigate("/production-line-c");

    }

    else if (selectedLine === "D") {

      navigate("/production-line-d");

    }

  }}

>
   <option value="">
    Select Line
  </option>
  <option value="A">

    Line A

  </option>

  <option value="B">

    Line B

  </option>

  <option value="C">

    Line C

  </option>

  <option value="D">

    Line D

  </option>

</select>

  {/* PRODUCT */}

  <select
    value={productId}
    onChange={(e) =>
      setProductId(e.target.value)
    }
  >

    <option value="">
      Select Product
    </option>

    {

      products.map((item) => (

        <option
          key={item.product_id}
          value={item.product_id}
        >

          {item.product_name}

        </option>

      ))

    }

  </select>

</div>

</div>
      
            {/* ========================================= */}
      {/* MESSAGE */}
      {/* ========================================= */}

     <div

  className={`message-box ${
    
    message.includes("Replace Finished Batches")

    ?

    "finished"

    :

    "success"

  }`}
>

 {message}

</div>
  {/* ========================================= */}
      {/* FINISHED BATCHES*/}
      {/* ========================================= */}
  {
  finishedBatches.length > 0 && (

    <div className="finished-batch-alert">

      <h2>

        Finished Batches

      </h2>

      <div className="finished-row">

       {
  finishedBatches.map((item) => (

    <div
      key={item.batch_id}
      className="finished-badge"
    >

      <b>{item.component_code}</b>

      <br />

      Batch : {item.batch_code}

      <br />

      {item.component_name}

    </div>

  ))
}
      </div>

    </div>

  )
}



      {/* ========================================= */}
      {/* STATIONS */}
      {/* ========================================= */}

      <div className="stations-wrapper">

        {/* ===================================== */}
        {/* STATION 1 */}
        {/* ===================================== */}

        <div className={`station-card line-c-card ${currentStation === 1 ? "active-card" : ""}`}>

          <h2>

            Station 1

          </h2>

          <p>

            UID Creation & Batch Mapping

          </p>

          <button
            className="green-btn"
            onClick={createUID}
          >

            Create UID

          </button>

          <input
            ref={station1UIDRef}
            type="text"
            placeholder="UID"
            value={station1UID}
            onChange={(e) =>
              setStation1UID(e.target.value)
            }
          />

          
          {
  station1Done && (

    <button
      className="next-btn"
      onClick={refreshStation1}
    >

      NEXT

    </button>

  )
}

          {

            uid && (

              <div
            className="barcode-box"
            id="barcode-print-area">

                <h3 id="print-uid-text">

                  {uid}
                
                </h3>

                <img
                 id="print-barcode-image"
                 src={barcode}
                 alt="barcode"
                />

                <button
                  className="dark-btn"
                  onClick={printUID}
                >

                  PRINT UID

                </button>

              </div>

            )

          }

          {/* ================================= */}
          {/* TABLE */}
          {/* ================================= */}

          <table>

            <thead>

              <tr>

                <th>Component</th>

                <th>Batch</th>
                 <th>Status</th>

              </tr>

            </thead>

            <tbody>

              {

                tableData.map((item, index) => (

                  <tr key={index}>

                    <td>

                      {item.component_code}

                    </td>

                    <td>

                      {item.batch_code}

                    </td>
                    
                     <td>

            {item.batch_status}

          </td>
                  </tr>

                ))

              }

            </tbody>

          </table>

        </div>

      </div>

    </div>

  );

}

export default ProductionLineC;