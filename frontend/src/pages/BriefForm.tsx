import { api } from "@/lib/api";
import { useNavigate } from "react-router-dom";
import { useState } from "react";

export default function BriefForm() {
  const nav = useNavigate();
  const [topic, setTopic] = useState("");

  const submit = async () => {
    const res = await api.post("/generate", {
      brief: { topic, audience: "general", objectives: [] },
      outputs: ["podcast", "outline"]
    });
    nav(`/job/${res.data.job_id}`);
  };

  return (
    <div className="max-w-xl mx-auto p-8 flex flex-col gap-4">
      <input
        placeholder="Topic"
        className="input input-bordered w-full"
        value={topic}
        onChange={e => setTopic(e.target.value)}
      />
      <button className="btn btn-primary" onClick={submit}>
        Generate
      </button>
    </div>
  );
} 