// src/pages/CreateUID.js

import React, {
  useState
} from "react";

import axios from "axios";

function CreateUID() {

  const [uid,
    setUid] =
    useState("");

  const [barcode,
    setBarcode] =
    useState("");

  const [message,
    setMessage] =
    useState("");

  const createUID = async () => {

    try {

      const response =
      await axios.post(

        "http://localhost:5000/api/create-uid/A"

      );

      setUid(
        response.data.uid
      );

      setBarcode(
        response.data.barcode
      );

      setMessage(
        response.data.message
      );

    } catch (error) {

      setMessage(

        error.response?.data?.error ||

        "UID Creation Failed"

      );
    }
  };

  return (

    <div>

      <h1>Create UID</h1>

      <button onClick={createUID}>

        Create UID

      </button>

      <h2>{message}</h2>

      <h3>{uid}</h3>

      {

        barcode && (

          <img
            src={barcode}
            alt="barcode"
            width="400"
          />

        )

      }

    </div>
  );
}

export default CreateUID;