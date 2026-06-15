import { useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";

export default function Login() {
  const [form, setForm]     = useState({ name: "", email: "", password: "" });
  const [isReg, setIsReg]   = useState(false);
  const [error, setError]   = useState("");
  const navigate            = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const endpoint = isReg ? "/auth/register" : "/auth/login";
      const payload  = isReg
        ? { name: form.name, email: form.email, password: form.password }
        : { email: form.email, password: form.password };

      const res = await api.post(endpoint, payload);
      localStorage.setItem("token",       res.data.token);
      localStorage.setItem("customer_id", res.data.customer_id);
      navigate("/dashboard");
    } catch (err) {
      setError(err.response?.data?.error || "Something went wrong");
    }
  };

  return (
    <div style={styles.container}>
      <h2>{isReg ? "Register" : "Login"}</h2>
      <form onSubmit={handleSubmit} style={styles.form}>
        {isReg && (
          <input
            placeholder="Name"
            value={form.name}
            onChange={e => setForm({ ...form, name: e.target.value })}
            style={styles.input}
          />
        )}
        <input
          placeholder="Email"
          value={form.email}
          onChange={e => setForm({ ...form, email: e.target.value })}
          style={styles.input}
        />
        <input
          type="password"
          placeholder="Password"
          value={form.password}
          onChange={e => setForm({ ...form, password: e.target.value })}
          style={styles.input}
        />
        {error && <p style={{ color: "red" }}>{error}</p>}
        <button type="submit" style={styles.btn}>
          {isReg ? "Register" : "Login"}
        </button>
      </form>
      <p
        onClick={() => setIsReg(!isReg)}
        style={{ cursor: "pointer", color: "blue" }}
      >
        {isReg ? "Already have account? Login" : "No account? Register"}
      </p>
    </div>
  );
}

const styles = {
  container: { maxWidth: 400, margin: "100px auto", padding: 20 },
  form     : { display: "flex", flexDirection: "column", gap: 10 },
  input    : { padding: 10, fontSize: 16 },
  btn      : { padding: 10, background: "#4CAF50", color: "white", border: "none", cursor: "pointer" }
};