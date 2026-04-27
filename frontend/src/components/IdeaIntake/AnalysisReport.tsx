interface AnalysisReportProps {
  analysis: {
    scope_score: string;
    complexity_score: string;
    tech_feasibility: {
      verdict: string;
      challenges: string[];
      suggestions: string[];
    };
    estimated_effort_hours: {
      min: number;
      max: number;
      confidence: string;
    };
    recommended_stack: {
      frontend: string;
      backend: string | null;
      database: string | null;
      deployment: string;
    };
    feature_breakdown: Array<{
      feature: string;
      estimated_hours: number;
      priority: string;
    }>;
    risks: Array<{
      description: string;
      severity: string;
      mitigation: string;
    }>;
    summary: string;
  };
}

export function AnalysisReport({ analysis }: AnalysisReportProps) {
  const verdictColor = {
    feasible: "bg-green-100 text-green-800",
    risky: "bg-yellow-100 text-yellow-800",
    not_feasible: "bg-red-100 text-red-800",
  }[analysis.tech_feasibility.verdict] || "bg-gray-100 text-gray-800";

  const scopeColor = {
    small: "text-green-600",
    medium: "text-blue-600",
    large: "text-orange-600",
    xlarge: "text-red-600",
  }[analysis.scope_score] || "text-gray-600";

  const severityBadge = (severity: string) => {
    const colors = {
      low: "bg-green-100 text-green-800",
      medium: "bg-yellow-100 text-yellow-800",
      high: "bg-red-100 text-red-800",
    };
    return colors[severity] || "bg-gray-100 text-gray-800";
  };

  return (
    <div className="space-y-6">
      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-4">Executive Summary</h3>
        <p className="text-gray-700">{analysis.summary}</p>
      </div>

      <div className="grid grid-cols-3 gap-4">
        <div className="bg-white rounded-lg shadow p-4">
          <span className="text-sm text-gray-500">Scope</span>
          <p className={`text-2xl font-bold capitalize ${scopeColor}`}>
            {analysis.scope_score}
          </p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <span className="text-sm text-gray-500">Complexity</span>
          <p className="text-2xl font-bold capitalize">{analysis.complexity_score}</p>
        </div>
        <div className="bg-white rounded-lg shadow p-4">
          <span className="text-sm text-gray-500">Tech Feasibility</span>
          <span className={`inline-block px-2 py-1 rounded text-sm font-semibold mt-1 ${verdictColor}`}>
            {analysis.tech_feasibility.verdict}
          </span>
        </div>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-3">Estimated Effort</h3>
        <p className="text-2xl font-bold">
          {analysis.estimated_effort_hours.min}–{analysis.estimated_effort_hours.max} hours
        </p>
        <p className="text-sm text-gray-500 mt-1">
          Confidence: {analysis.estimated_effort_hours.confidence}
        </p>
      </div>

      <div className="bg-white rounded-lg shadow p-6">
        <h3 className="text-lg font-semibold mb-3">Recommended Stack</h3>
        <div className="grid grid-cols-2 gap-2 text-sm">
          <div><span className="font-medium">Frontend:</span> {analysis.recommended_stack.frontend}</div>
          {analysis.recommended_stack.backend && (
            <div><span className="font-medium">Backend:</span> {analysis.recommended_stack.backend}</div>
          )}
          {analysis.recommended_stack.database && (
            <div><span className="font-medium">Database:</span> {analysis.recommended_stack.database}</div>
          )}
          <div><span className="font-medium">Deployment:</span> {analysis.recommended_stack.deployment}</div>
        </div>
      </div>

      {analysis.tech_feasibility.challenges.length > 0 && (
        <div className="bg-yellow-50 rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-3">Challenges</h3>
          <ul className="list-disc list-inside space-y-1">
            {analysis.tech_feasibility.challenges.map((c, i) => (
              <li key={i} className="text-gray-700">{c}</li>
            ))}
          </ul>
        </div>
      )}

      {analysis.tech_feasibility.suggestions.length > 0 && (
        <div className="bg-blue-50 rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-3">Suggestions</h3>
          <ul className="list-disc list-inside space-y-1">
            {analysis.tech_feasibility.suggestions.map((s, i) => (
              <li key={i} className="text-gray-700">{s}</li>
            ))}
          </ul>
        </div>
      )}

      {analysis.feature_breakdown.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-3">Feature Breakdown</h3>
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b">
                <th className="text-left py-2">Feature</th>
                <th className="text-right py-2">Hours</th>
                <th className="text-right py-2">Priority</th>
              </tr>
            </thead>
            <tbody>
              {analysis.feature_breakdown.map((f, i) => (
                <tr key={i} className="border-b last:border-0">
                  <td className="py-2">{f.feature}</td>
                  <td className="py-2 text-right">{f.estimated_hours}h</td>
                  <td className="py-2 text-right">
                    <span className={`px-2 py-0.5 rounded text-xs font-medium ${
                      f.priority === "must" ? "bg-red-100 text-red-800" :
                      f.priority === "should" ? "bg-yellow-100 text-yellow-800" :
                      "bg-gray-100 text-gray-800"
                    }`}>
                      {f.priority}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {analysis.risks.length > 0 && (
        <div className="bg-white rounded-lg shadow p-6">
          <h3 className="text-lg font-semibold mb-3">Risks</h3>
          <div className="space-y-3">
            {analysis.risks.map((r, i) => (
              <div key={i} className="flex items-start gap-3">
                <span className={`px-2 py-0.5 rounded text-xs font-medium shrink-0 ${severityBadge(r.severity)}`}>
                  {r.severity}
                </span>
                <div>
                  <p className="font-medium text-sm">{r.description}</p>
                  <p className="text-xs text-gray-500 mt-0.5">Mitigation: {r.mitigation}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}