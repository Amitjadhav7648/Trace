import React from "react";
import { Routes, Route } from "react-router-dom";
import { Navigate } from "react-router-dom";

import Dashboard from "./pages/Dashboard";
import Components from "./pages/Components";
import ScanBatch from './pages/ScanBatch';
import Production from "./pages/Production";
import CreateUID from "./pages/CreateUID";
import Traceability from "./pages/Traceability";
import Records from "./pages/Records";
import ProductionLineB from "./pages/ProductionLineB";
import ProductionLineC from "./pages/ProductionLineC";
import ProductionLineD from "./pages/ProductionLineD";
import FinalSerial from "./pages/FinalSerial";



function RoutesPage() {
  return (
    <Routes>

      <Route
    path="/"
    element={<Navigate to="/dashboard" />}
  />

  <Route path="/dashboard" element={<Dashboard />} />
      <Route path="/scan-batch" element={<ScanBatch />} />
      <Route path="/components" element={<Components />} />
      <Route path="/records" element={<Records />}/>
      <Route path="/Production" element={<Production />} />
      <Route path="/production-line-b" element={<ProductionLineB />}/>
      <Route path="/production-line-c" element={<ProductionLineC />}/>
      <Route path="/production-line-d" element={<ProductionLineD />}/>
      <Route path="/createUID" element={<CreateUID />} />
      <Route path="/traceability" element={<Traceability />} />
      <Route path="/final-serial" element={<FinalSerial />}/>
    </Routes>
  );
}

export default RoutesPage;