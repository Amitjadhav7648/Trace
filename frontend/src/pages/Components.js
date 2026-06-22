// src/pages/Components.js

import React, { useEffect, useState } from "react";
import API from "../api/api";
import "../styles/components.css"

function Components() {

  const [components, setComponents] = useState([]);

  useEffect(() => {

    fetchComponents();

  }, []);

  const fetchComponents = async () => {

    try {

      // BACKEND API CALL
      const response = await API.get("/components");

      console.log(response.data);

      setComponents(response.data.components);

    } catch (error) {

      console.log(error);
    }
  };

  return (
    <div className="component-page">

      <h2 className="component-title">
        Component Master
      </h2>

      <table className="component-table">

        <thead>

          <tr>

            <th>ID</th>

            <th>Component Name</th>

            <th>Component Code</th>

            <th>Description</th>

            <th>Usage Station</th>

          </tr>

        </thead>

        <tbody>

          {components.map((item, index) => (

            <tr key={index}>

              <td>{item.component_id}</td>

              <td>{item.component_name}</td>

              <td>{item.component_code}</td>

              <td>{item.description}</td>

              <td>{item.usage_station}</td>

            </tr>

          ))}

        </tbody>

      </table>

    </div>
  );
}

export default Components;