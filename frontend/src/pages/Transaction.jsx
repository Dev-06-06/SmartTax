import { useState, useEffect } from "react";
import { useLocation, useNavigate } from "react-router-dom";
import api from "../api/axios";

export default function Transaction() {
  const { state }           = useLocation();
  const navigate            = useNavigate();
  const goal                = state?.goal;
  const customer_id         = localStorage.getItem("customer_id");

  const categories = [
    "food", "travel", "shopping", "education",
    "utilities", "entertainment", "healthcare",
    "government", "personal_care", "other"
  ];

  const [amount, setAmount]       = useState("");
  const [category, setCategory]   = useState("food");
  const [percentages, setPercentages] = useState({});
  const [selected, setSelected]   = useState({});
  const [goals, setGoals]         = useState([]);
  const [allPercentages, setAllPercentages] = useState({});

  useEffect(() => {
    fetchGoals();
  }, []);

  const fetchGoals = async () => {
    const res = await api.get(`/goals/${customer_id}`);
    setGoals(res.data);
    // fetch percentages for all goals
    const allPct = {};
    for (const g of res.data) {
      try {
        const r = await api.get(`/percentages/${customer_id}/${g._id}`);
        allPct[g._id] = r.data.effective_percentages;
      } catch (e) {}
    }
    setAllPercentages(allPct);
  };

  // when amount or category changes → compute taxes
  useEffect(() => {
    if (!amount || !category) return;
    const taxes = {};
    const sel   = {};
    goals.forEach(g => {
      const pct    = allPercentages[g._id]?.[category] || 0;
      const taxAmt = (parseFloat(amount) * pct / 100).toFixed(2);
      taxes[g._id] = { name: g.name, percent: pct, amount: taxAmt };
      sel[g._id]   = true; // default selected
    });
    setPercentages(taxes);
    setSelected(sel);
  }, [amount, category, allPercentages]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    const taxes_applied = goals.map(g => ({
      goal_id      : g._id,
      goal_name    : g.name,
      percent      : allPercentages[g._id]?.[category] || 0,
      user_selected: selected[g._id] || false
    }));

    await api.post("/transactions/", {
      customer_id,
      amount  : parseFloat(amount),
      category,
      taxes_applied
    });

    alert("Transaction saved!");
    navigate("/dashboard");
  };

  return (
    <div style={{ maxWidth: 500, margin: "40px auto", padding: 20 }}>
      <h2>Add Transaction</h2>
      <form onSubmit={handleSubmit} style={{ display: "flex", flexDirection: "column", gap: 10 }}>

        <input
          type="number"
          placeholder="Amount (₹)"
          value={amount}
          onChange={e => setAmount(e.target.value)}
        />

        <select value={category} onChange={e => setCategory(e.target.value)}>
          {categories.map(c => <option key={c} value={c}>{c}</option>)}
        </select>

        {/* TAX SELECTOR */}
        {Object.keys(percentages).length > 0 && (
          <div style={{ border: "1px solid #ccc", padding: 12, borderRadius: 6 }}>
            <b>Taxes Applied:</b>
            {goals.map(g => (
              <div key={g._id} style={{ display: "flex", justifyContent: "space-between", marginTop: 8 }}>
                <label>
                  <input
                    type="checkbox"
                    checked={selected[g._id] || false}
                    onChange={e => setSelected({ ...selected, [g._id]: e.target.checked })}
                  />
                  {" "}@ {g.name} — {percentages[g._id]?.percent}% = ₹{percentages[g._id]?.amount}
                </label>
              </div>
            ))}
          </div>
        )}

        <button type="submit">Pay & Save</button>
        <button type="button" onClick={() => navigate("/dashboard")}>Cancel</button>
      </form>
    </div>
  );
}