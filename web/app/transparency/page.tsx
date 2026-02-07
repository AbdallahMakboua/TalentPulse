export default function TransparencyPage() {
  return (
    <div className="space-y-8 max-w-3xl">
      <h1 className="text-3xl font-bold text-slate-900">🔒 Transparency & Privacy</h1>
      <p className="text-slate-500">
        TalentPulse is built on a foundation of privacy, transparency, and human-centered design.
      </p>

      {/* What we collect */}
      <div className="bg-white rounded-xl border p-6">
        <h2 className="text-xl font-semibold text-green-800 mb-4">✅ What Data We Collect</h2>
        <p className="text-sm text-slate-600 mb-4">
          Only aggregated, contextual metadata. Never content or personal communications.
        </p>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {[
            { signal: 'Meeting Count & Duration', why: 'Understand workload patterns' },
            { signal: 'Calendar Free/Busy Status', why: 'Detect focus time availability' },
            { signal: 'Task Completion Counts', why: 'Track delivery velocity trends' },
            { signal: 'Response Time Buckets', why: 'Coarse responsiveness (fast/normal/slow)' },
            { signal: 'Collaboration Breadth', why: 'Unique collaborator count across teams' },
            { signal: 'After-Hours Activity Count', why: 'Detect potential burnout patterns' },
            { signal: 'Learning Hours (self-reported)', why: 'Track growth investment' },
            { signal: 'RSVP Status (accepted/declined)', why: 'Meeting engagement patterns' },
          ].map((item, i) => (
            <div key={i} className="bg-green-50 p-3 rounded-lg">
              <div className="font-medium text-green-900 text-sm">{item.signal}</div>
              <div className="text-xs text-green-700 mt-1">{item.why}</div>
            </div>
          ))}
        </div>
      </div>

      {/* What we NEVER collect */}
      <div className="bg-white rounded-xl border p-6">
        <h2 className="text-xl font-semibold text-red-800 mb-4">❌ What We NEVER Collect</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {[
            'Email subjects, bodies, or attachments',
            'Message or chat content',
            'Meeting transcripts or recordings',
            'Screen recordings or screenshots',
            'Keystrokes or typing patterns',
            'Webcam or microphone feeds',
            'GPS or device location',
            'Application usage tracking',
            'Browser history or URLs visited',
            'File contents or document text',
          ].map((item, i) => (
            <div key={i} className="flex items-center gap-2 text-sm text-red-700 bg-red-50 p-2 rounded-lg">
              <span>❌</span>
              <span>{item}</span>
            </div>
          ))}
        </div>
      </div>

      {/* How AI works */}
      <div className="bg-white rounded-xl border p-6">
        <h2 className="text-xl font-semibold mb-4">🤖 How AI is Used</h2>
        <div className="space-y-3 text-sm text-slate-700">
          <p>TalentPulse uses a <strong>local AI model</strong> (Ollama) that runs entirely on your infrastructure. No data ever leaves your network.</p>
          <p>AI is used ONLY for:</p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li>Generating 1:1 coaching questions from aggregated signals</li>
            <li>Drafting performance review summaries from computed scores</li>
            <li>Translating explainability data into plain language</li>
          </ul>
          <p className="bg-blue-50 p-3 rounded-lg text-blue-800">
            <strong>Important:</strong> AI is decision SUPPORT only. No automated decisions are made.
            Managers must use human judgment and 1:1 conversations.
          </p>
        </div>
      </div>

      {/* Bias awareness */}
      <div className="bg-white rounded-xl border p-6">
        <h2 className="text-xl font-semibold mb-4">⚖️ Bias Awareness</h2>
        <div className="space-y-3 text-sm text-slate-700">
          <p>Every score is computed with bias-aware safeguards:</p>
          <ul className="list-disc list-inside space-y-2 ml-4">
            <li><strong>Self-baseline first:</strong> Primary comparison is against the employee&apos;s own history</li>
            <li><strong>Cohort normalization:</strong> Adjusts for role, seniority, and tenure</li>
            <li><strong>Fairness warnings:</strong> Displayed when comparing across different roles or small groups</li>
            <li><strong>Confidence scores:</strong> Every assessment shows its reliability level</li>
            <li><strong>Limitations disclosed:</strong> System openly states what it cannot determine</li>
          </ul>
        </div>
      </div>

      {/* Data deletion */}
      <div className="bg-white rounded-xl border p-6">
        <h2 className="text-xl font-semibold mb-4">🗑️ Request Data Deletion</h2>
        <p className="text-sm text-slate-600 mb-4">
          Any employee can request complete deletion of their signal data, scores, and derived insights.
        </p>
        <p className="text-sm text-slate-500">
          Contact your administrator or use the API: <code className="bg-slate-100 px-2 py-1 rounded">DELETE /employees/&#123;id&#125;/data</code>
        </p>
      </div>
    </div>
  );
}
