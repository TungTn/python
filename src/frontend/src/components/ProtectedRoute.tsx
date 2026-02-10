import { Navigate } from "react-router-dom";
import { isLoggedIn } from "../api/auth";

export default function ProtectedRoute({ children }: { children: JSX.Element }) {
  if (!isLoggedIn()) return <Navigate to="/login" replace />;
  return children;
}