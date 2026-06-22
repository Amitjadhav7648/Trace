// =====================================================
// src/pages/ScanBatch.js
// FULL FINAL WORKING CODE
// =====================================================

import React, {
  useState,
  useEffect,
  useRef,
  useCallback
} from "react";

import axios from "axios";

import { useNavigate } from "react-router-dom";

import "../styles/ScanBatch.css";

function ScanBatch() {

  // ===================================================
  // NAVIGATION
  // ===================================================

  const navigate = useNavigate();

  // ===================================================
  // REFS
  // ===================================================

  const scanInputRef = useRef(null);

  const replaceInputRef = useRef(null);

  // ===================================================
  // STATES
  // ===================================================

  const [scanValue, setScanValue] =
    useState("");

  const [line, setLine] =
    useState("");

  const [productId, setProductId] =
    useState("");

  const [products, setProducts] =
    useState([]);

  const [batches, setBatches] =
    useState([]);

  const [message, setMessage] =
    useState("");

  // ===================================================
  // REPLACE POPUP
  // ===================================================

  const [showReplacePopup,
    setShowReplacePopup] =
    useState(false);

  const [selectedBatchId,
    setSelectedBatchId] =
    useState("");

  const [replaceQR,
    setReplaceQR] =
    useState("");

  // ===================================================
  // AUTO CLEAR MESSAGE
  // ===================================================

  useEffect(() => {

    if (message) {

      const timer = setTimeout(() => {

        setMessage("");

      }, 3000);

      return () => clearTimeout(timer);

    }

  }, [message]);

  // ===================================================
  // LOAD PRODUCTS
  // ===================================================

  useEffect(() => {

    loadProducts();

  }, []);


  // ===================================================
  // LOAD PRODUCTS
  // ===================================================

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
  // LOAD BATCHES
  // ===================================================

  const loadBatches = useCallback(async () => {

  if (!line || !productId) {

    setBatches([]);
    return;

  }

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

  catch (error) {

    console.log(error);

  }

}, [line, productId]);

useEffect(() => {

  loadBatches();

}, [loadBatches]);

  // ===================================================
  // GO TO PRODUCTION
  // ===================================================

  const goToProduction = () => {

    navigate("/production");

  };

  // ===================================================
  // SCAN BATCH
  // ===================================================

  const scanBatch = async () => {

    if (!productId) {

      setMessage(
        "Please Select Product"
      );

      return;

    }

    if (!line) {

      setMessage(
        "Please Select Line"
      );

      return;

    }

    if (!scanValue) {

      setMessage(
        "Please Scan Batch QR"
      );

      return;

    }

    try {

      const response = await axios.post(

        "http://localhost:5000/api/scan-batch",

        {

          scan_value:
          scanValue.toUpperCase(),

          line: line,

          product_id:
          Number(productId)

        }

      );

      setMessage(
        response.data.message
      );

      setScanValue("");

      loadBatches();

      setTimeout(() => {

        if (scanInputRef.current) {

          scanInputRef.current.focus();

        }

      }, 100);

    }

    catch(error) {

      setMessage(

        error.response?.data?.error ||

        "Batch Scan Failed"

      );

    }

  };

  // ===================================================
  // ENTER KEY MAIN SCAN
  // ===================================================

  const handleKeyPress = (e) => {

    if (e.key === "Enter") {

      scanBatch();

    }

  };

  // ===================================================
  // OPEN REPLACE POPUP
  // ===================================================

  const openReplacePopup = (batchId) => {

    setSelectedBatchId(batchId);

    setReplaceQR("");

    setShowReplacePopup(true);

    // AUTO FOCUS

    setTimeout(() => {

      if (replaceInputRef.current) {

        replaceInputRef.current.focus();

      }

    }, 100);

  };

  // ===================================================
  // CHANGE SINGLE BATCH
  // ===================================================

  const changeSingleBatch = async (
    oldBatchId,
    newQR
  ) => {

    if (!newQR) {

      alert("Scan New Batch QR");

      return;

    }

    try {

      const response = await axios.post(

        "http://localhost:5000/api/change-single-batch",

        {

          old_batch_id: oldBatchId,

          scan_value:
          newQR.toUpperCase(),

          line: line,

          product_id:
          Number(productId)

        }

      );

      // SUCCESS MESSAGE

      setMessage(
        response.data.message
      );

      // CLOSE POPUP

      setShowReplacePopup(false);

      setReplaceQR("");

      // RELOAD BATCHES

      loadBatches();

      // FOCUS MAIN SCAN BOX

      setTimeout(() => {

        if (scanInputRef.current) {

          scanInputRef.current.focus();

        }

      }, 200);

    }

    catch(error) {

      alert(

        error.response?.data?.error ||

        "Batch Replace Failed"

      );

    }

  };

  // ===================================================
  // ENTER KEY FOR REPLACE
  // ===================================================

  const handleReplaceEnter = (e) => {

    if (e.key === "Enter") {

      changeSingleBatch(
        selectedBatchId,
        replaceQR
      );

    }

  };

  // ===================================================
  // REPLACE ALL
  // ===================================================

  const replaceAllBatches = async () => {

  try {

    const response = await axios.post(

      "http://localhost:5000/api/reset-active-batches",

      {
        line: line
      }

    );

    alert(response.data.message);
    window.location.reload();

  }

  catch (error) {

    alert(
      error.response?.data?.error ||
      "Replace Failed"
    );

  }

};
  // ===================================================
  // JSX
  // ===================================================

  return (

    <div className="batch-page">

      {/* HEADER */}

      <div className="top-header">

        <h1>

          Batch Scan

        </h1>

        <div>

          <button
            className="replace-all-btn"
            onClick={replaceAllBatches}
          >

            REPLACE ALL

          </button>

          <button
            className="production-btn"
            onClick={goToProduction}
          >

            GO TO PRODUCTION

          </button>

        </div>

      </div>

      {/* SCAN SECTION */}

      <div className="scan-container">

        {/* LINE */}

        <select
          value={line}
          onChange={(e) =>
            setLine(e.target.value)
          }
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

        {/* QR */}

        <input
          ref={scanInputRef}

          className="scan-qr-input"

          type="text"

          placeholder="Scan Batch QR"

          value={scanValue}

          onChange={(e) =>
            setScanValue(
              e.target.value.toUpperCase()
            )
          }

          onKeyDown={handleKeyPress}
        />

        {/* BUTTON */}

        <button
          className="scan-btn"
          onClick={scanBatch}
        >

          SCAN BATCH

        </button>

      </div>

      {/* MESSAGE */}

      {

        message && (

          <div className="message-box">

            {message}

          </div>

        )

      }

      {/* BATCH LIST */}

      <div className="batch-box-container">

        {

          batches.map((item) => (

            <div
              key={item.batch_id}
              className="batch-box"
            >

              <div className="batch-title">

                {item.batch_code}

              </div>

              <div className="batch-row">

                <span>

                  Product

                </span>

                <span>

                  {item.product_name}

                </span>

              </div>

              <div className="batch-row">

                <span>

                  Component

                </span>

                <span>

                  {item.component_code}

                </span>

              </div>

              <div className="batch-row">

                <span>

                  Total

                </span>

                <span>

                  {item.total_quantity}

                </span>

              </div>

              <div className="batch-row">

                <span>

                  Used

                </span>

                <span>

                  {item.used_quantity}

                </span>

              </div>

              <div className="batch-row">

                <span>

                  Remaining

                </span>

                <span>

                  {item.remaining_quantity}

                </span>

              </div>

              <div className="batch-row">

                <span>

                  Status

                </span>

                <span className="status-active">

                  {item.status}

                </span>

              </div>

              <div className="line-tag">

                Line {item.line}

              </div>

              {/* REPLACE BUTTON */}

              <button
                className="replace-btn"
                onClick={() =>
                  openReplacePopup(
                    item.batch_id
                  )
                }
              >

                REPLACE

              </button>

            </div>

          ))

        }

      </div>

      {/* REPLACE POPUP */}

      {

        showReplacePopup && (

          <div className="popup-overlay">

            <div className="popup-box">

              <h2>

                Replace Batch

              </h2>

              <input
                ref={replaceInputRef}

                type="text"

                placeholder="Scan New Batch QR"

                value={replaceQR}

                onChange={(e) =>
                  setReplaceQR(
                    e.target.value.toUpperCase()
                  )
                }

                onKeyDown={handleReplaceEnter}
              />

              <div className="popup-buttons">

                <button

                  onClick={() =>

                    changeSingleBatch(
                      selectedBatchId,
                      replaceQR
                    )

                  }

                >

                  CONFIRM

                </button>

                <button

                  onClick={() => {

                    setShowReplacePopup(false);

                    setReplaceQR("");

                  }}

                >

                  CANCEL

                </button>

              </div>

            </div>

          </div>

        )

      }

    </div>

  );

}

export default ScanBatch;