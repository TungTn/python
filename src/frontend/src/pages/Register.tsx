import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { api } from "../api/api";
import { setToken } from "../api/auth";
import { Button } from "../components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "../components/ui/card";
import { Input } from "../components/ui/input";
import { Label } from "../components/ui/label";

type TokenResponse = { access_token: string; token_type: string };

export default function Register() {
  const nav = useNavigate();
  const [name, setName] = useState("Tung");
  const [age, setAge] = useState<number>(32);
  const [email, setEmail] = useState("tung@example.com");
  const [password, setPassword] = useState("123456");
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(false);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setLoading(true);
    try {
      const res = await api.post<TokenResponse>("/auth/register", {
        name,
        age,
        email,
        password,
      });
      setToken(res.data.access_token);
      nav("/");
    } catch (err: any) {
      setError(err?.response?.data?.detail ?? "Register failed");
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="mx-auto max-w-xl px-6 pb-16">
      <div className="grid gap-6">
        <div className="space-y-2">
          <h1 className="text-4xl font-semibold">Create your account</h1>
          <p className="text-sm text-muted-foreground">
            Build a profile, explore the API, and unlock your private workspace.
          </p>
        </div>

        <Card className="border-white/60 bg-white/80 shadow-xl shadow-amber-100/50 backdrop-blur">
          <CardHeader>
            <CardTitle>Register</CardTitle>
            <CardDescription>Fill in your details to create a new account.</CardDescription>
          </CardHeader>
          <CardContent>
            <form onSubmit={onSubmit} className="grid gap-5">
              <div className="grid gap-2">
                <Label htmlFor="name">Name</Label>
                <Input id="name" value={name} onChange={(e) => setName(e.target.value)} />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="age">Age</Label>
                <Input
                  id="age"
                  value={age}
                  onChange={(e) => setAge(Number(e.target.value))}
                  type="number"
                />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="email">Email</Label>
                <Input id="email" value={email} onChange={(e) => setEmail(e.target.value)} />
              </div>

              <div className="grid gap-2">
                <Label htmlFor="password">Password (&lt; 20, 1 uppercase, 1 special, 4 lowercase)</Label>
                <Input
                  id="password"
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  type="password"
                />
              </div>

              <Button disabled={loading} type="submit" className="w-full">
                {loading ? "Creating..." : "Create account"}
              </Button>

              {error && (
                <div className="rounded-md border border-destructive/40 bg-destructive/10 px-3 py-2 text-sm text-destructive">
                  {error}
                </div>
              )}

              <div className="text-sm text-muted-foreground">
                Already have an account?{" "}
                <Link className="font-medium text-primary hover:underline" to="/login">
                  Login
                </Link>
              </div>
            </form>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
