import { useState } from "react";
import axios from "axios";
import { useNavigate } from "react-router-dom";

const API_BASE = import.meta.env.VITE_API_URL || "/api/v1";

interface Constraints {
  deadline?: string;
  budget_tier?: string;
  team_size?: number;
  must_haves?: string[];
  nice_to_haves?: string[];
}

interface Preferences {
  tech_stack?: string[];
  deployment_target?: string;
  style?: string;
}

export function IdeaForm() {
  const navigate = useNavigate();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [deadline, setDeadline] = useState("");
  const [budgetTier, setBudgetTier] = useState("");
  const [techStack, setTechStack] = useState("");
  const [deploymentTarget, setDeploymentTarget] = useState("");
  const [style, setStyle] = useState("");
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");

    try {
      const constraints: Constraints = {};
      if (deadline) constraints.deadline = deadline;
      if (budgetTier) constraints.budget_tier = budgetTier;

      const preferences: Preferences = {};
      if (techStack) preferences.tech_stack = techStack.split(",").map((s) => s.trim());
      if (deploymentTarget) preferences.deployment_target = deploymentTarget;
      if (style) preferences.style = style;

      await axios.post(
        `${API_BASE}/ideas`,
        { title, description, constraints, preferences },
        { withCredentials: true }
      );
      navigate("/ideas");
    } catch (err) {
      setError("Failed to submit idea. Please try again.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-2xl mx-auto p-6 bg-white rounded-lg shadow">
      <h2 className="text-2xl font-bold mb-6">Submit Your Web App Idea</h2>

      {error && (
        <div className="mb-4 p-3 bg-red-100 text-red-700 rounded">{error}</div>
      )}

      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Project Title *
          </label>
          <input
            type="text"
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            maxLength={120}
            required
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            placeholder="My Awesome App"
          />
          <span className="text-xs text-gray-500">{title.length}/120</span>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Description *
          </label>
          <textarea
            value={description}
            onChange={(e) => setDescription(e.target.value)}
            maxLength={10000}
            required
            rows={6}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            placeholder="Describe your web application idea in detail..."
          />
          <span className="text-xs text-gray-500">{description.length}/10000</span>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Deadline
            </label>
            <input
              type="text"
              value={deadline}
              onChange={(e) => setDeadline(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="e.g., 2 weeks"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Budget Tier
            </label>
            <select
              value={budgetTier}
              onChange={(e) => setBudgetTier(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            >
              <option value="">Select...</option>
              <option value="free">Free</option>
              <option value="starter">Starter</option>
              <option value="pro">Pro</option>
              <option value="enterprise">Enterprise</option>
            </select>
          </div>
        </div>

        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Tech Stack Preferences
            </label>
            <input
              type="text"
              value={techStack}
              onChange={(e) => setTechStack(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
              placeholder="React, TypeScript, etc."
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-1">
              Deployment Target
            </label>
            <select
              value={deploymentTarget}
              onChange={(e) => setDeploymentTarget(e.target.value)}
              className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
            >
              <option value="">Select...</option>
              <option value="vercel">Vercel</option>
              <option value="cloudflare">Cloudflare</option>
              <option value="railway">Railway</option>
              <option value="self_hosted">Self-hosted</option>
            </select>
          </div>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-1">
            Style
          </label>
          <select
            value={style}
            onChange={(e) => setStyle(e.target.value)}
            className="w-full px-3 py-2 border rounded-lg focus:ring-2 focus:ring-blue-500 focus:outline-none"
          >
            <option value="">Select...</option>
            <option value="minimal">Minimal</option>
            <option value="modern">Modern</option>
            <option value="playful">Playful</option>
            <option value="corporate">Corporate</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full py-3 bg-blue-600 text-white font-semibold rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? "Submitting..." : "Submit Idea for Analysis"}
        </button>
      </form>
    </div>
  );
}