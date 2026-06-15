import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import Login       from "./pages/Login";
import Dashboard   from "./pages/Dashboard";
import Transaction from "./pages/Transaction";

const PrivateRoute = ({ children }) => {
  const token = localStorage.getItem("token");
  return token ? children : <Navigate to="/login" />;
};

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/login"       element={<Login />} />
        <Route path="/dashboard"   element={
          <PrivateRoute><Dashboard /></PrivateRoute>
        } />
        <Route path="/transaction" element={
          <PrivateRoute><Transaction /></PrivateRoute>
        } />
        <Route path="*" element={<Navigate to="/login" />} />
      </Routes>
    </BrowserRouter>
  );
}