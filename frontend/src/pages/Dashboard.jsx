import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import api from "../api/axios";

export default function Dashboard() {
  const [goals, setGoals]         = useState([]);
  const [form, setForm]           = useState({ name: "", description: "", target_amount: "", target_date: "" });
  const [percentages, setPercentages] = useState({});
  const navigate                  = useNavigate();
  const customer_id               = localStorage.getItem("customer_id");

  useEffect(() => {
    fetchGoals();
  }, []);

  const fetchGoals = async () => {
    const res = await api.get(`/goals/${customer_id}`);
    setGoals(res.data);
    // fetch percentages for first goal
    if (res.data.length > 0) {
      fetchPercentages(res.data[0]._id);
    }
  };

  const fetchPercentages = async (goal_id) => {
    try {
      const res = await api.get(`/percentages/${customer_id}/${goal_id}`);
      setPercentages(res.data.effective_percentages);
    } catch (e) {}
  };

  const createGoal = async (e) => {
    e.preventDefault();
    await api.post("/goals/", { ...form, customer_id });
    setForm({ name: "", description: "", target_amount: "", target_date: "" });
    fetchGoals();
  };

  const logout = () => {
    localStorage.clear();
    navigate("/login");
  };

  return (
    <div style={{ maxWidth: 700, margin: "40px auto", padding: 20 }}>

      <div style={{ display: "flex", justifyContent: "space-between" }}>
        <h2>SmartTax Dashboard</h2>
        <button onClick={logout}>Logout</button>
      </div>

      {/* CREATE GOAL */}
      <h3>Create Goal</h3>
      <form onSubmit={createGoal} style={{ display: "flex", flexDirection: "column", gap: 8 }}>
        <input placeholder="Goal name"        value={form.name}          onChange={e => setForm({ ...form, name: e.target.value })}          />
        <input placeholder="Description"      value={form.description}   onChange={e => setForm({ ...form, description: e.target.value })}   />
        <input placeholder="Target amount"    value={form.target_amount} onChange={e => setForm({ ...form, target_amount: e.target.value })} type="number" />
        <input placeholder="Target date"      value={form.target_date}   onChange={e => setForm({ ...form, target_date: e.target.value })}   type="date" />
        <button type="submit">Create Goal + Calculate Tax %</button>
      </form>

      {/* GOALS LIST */}
      <h3>Your Goals</h3>
      {goals.map(g => (
        <div key={g._id} style={{ border: "1px solid #ccc", padding: 12, marginBottom: 10, borderRadius: 6 }}>
          <b>{g.name}</b> — ₹{g.saved_amount} / ₹{g.target_amount}
          <br />
          Target: {g.target_date} | {g.completed ? "✅ Done" : "⏳ In Progress"}
          <br />
          <button onClick={() => fetchPercentages(g._id)}>View Tax %</button>
          <button onClick={() => navigate("/transaction", { state: { goal: g } })} style={{ marginLeft: 8 }}>
            Add Transaction
          </button>
        </div>
      ))}

      {/* PERCENTAGES */}
      {Object.keys(percentages).length > 0 && (
        <div>
          <h3>Tax Percentages</h3>
          <table style={{ width: "100%", borderCollapse: "collapse" }}>
            <thead>
              <tr>
                <th style={th}>Category</th>
                <th style={th}>Tax %</th>
              </tr>
            </thead>
            <tbody>
              {Object.entries(percentages).map(([cat, pct]) => (
                <tr key={cat}>
                  <td style={td}>{cat}</td>
                  <td style={td}>{pct}%</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}

const th = { border: "1px solid #ccc", padding: 8, background: "#f4f4f4" };
const td = { border: "1px solid #ccc", padding: 8 };