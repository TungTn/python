import { BrowserRouter, Routes, Route, Navigate, Link } from "react-router-dom";
import Login from "./pages/Login";
import Register from "./pages/Register";
import Home from "./pages/Home";
import ProtectedRoute from "./components/ProtectedRoute";
import { clearToken, isLoggedIn } from "./api/auth";
import { Button } from "./components/ui/button";

export default function App() {
  return (
    <BrowserRouter>
      <div className="mx-auto max-w-6xl px-6 py-6">
        <nav className="flex flex-wrap items-center justify-between gap-3 rounded-2xl border bg-white/70 px-5 py-3 shadow-sm backdrop-blur">
          <div className="flex items-center gap-3">
            <span className="text-sm font-semibold uppercase tracking-[0.25em] text-muted-foreground">
              Aurora Stack
            </span>
          </div>
          <div className="flex flex-wrap items-center gap-2">
            <Button variant="ghost" asChild>
              <Link to="/">Home</Link>
            </Button>
            <Button variant="outline" asChild>
              <Link to="/login">Login</Link>
            </Button>
            <Button asChild>
              <Link to="/register">Register</Link>
            </Button>
            {isLoggedIn() && (
              <Button
                variant="ghost"
                onClick={() => {
                  clearToken();
                  window.location.href = "/login";
                }}
              >
                Logout
              </Button>
            )}
          </div>
        </nav>
      </div>

      <Routes>
        <Route
          path="/"
          element={
            <ProtectedRoute>
              <Home />
            </ProtectedRoute>
          }
        />
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </BrowserRouter>
  );
}
