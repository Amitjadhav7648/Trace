import React from "react";
import { BrowserRouter } from "react-router-dom";

import Navbar from "./components/Navbar";
import RoutesPage from "./routes";

function App() {

  return (
    <BrowserRouter>

      <Navbar />

      <RoutesPage />

    </BrowserRouter>
  );
}

export default App;