'use client';

import { useEffect, useState } from 'react';
import { useParams } from 'next/navigation';
import {
  api, EmployeeInsights, QuestionsResponse, ReviewDraftResponse,
} from '@/lib/api';
import { ScoreBadge } from '@/components/ScoreBadge';
import { SignalChart } from '@/components/SignalChart';
import { ExplainCard } from '@/components/ExplainCard';
import { CoachingPanel } from '@/components/CoachingPanel';
import { ReviewPanel } from '@/components/ReviewPanel';
import { PredictiveBurnout } from '@/components/PredictiveBurnout';
import { HiddenTalent } from '@/components/HiddenTalent';

export default function EmployeeDetailPage() {
  const { id } = useParams<{ id: string }>();
  const [insights, setInsights] = useState<EmployeeInsights | null>(null);
  const [questions, setQuestions] = useState<QuestionsResponse | null>(null);
  const [review, setReview] = useState<ReviewDraftResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [activeTab, setActiveTab] = useState<'manager' | 'employee'>('manager');
  const [genLoading, setGenLoading] = useState({ questions: false, review: false });

  useEffect(() => {
    if (id) {
      api.employeeInsights(id).then(setInsights).finally(() => setLoading(false));
    }
  }, [id]);

  const generateQuestions = async () => {
    setGenLoading(p => ({ ...p, questions: true }));
    try {
      const q = await api.employeeQuestions(id);
      setQuestions(q);
    } catch (e) { console.error(e); }
    setGenLoading(p => ({ ...p, questions: false }));
  };

  const generateReview = async () => {
    setGenLoading(p => ({ ...p, review: true }));
    try {
      const r = await api.employeeReview(id);
      setReview(r);
    } catch (e) { console.error(e); }
    setGenLoading(p => ({ ...p, review: false }));
  };

  if (loading) return <div className="animate-pulse text-lg">Loading employee insights...</div>;
  if (!insights) return <div className="text-red-600">Employee not found</div>;

  const emp = insights.employee;

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-bold text-slate-900">{emp.name}</h1>
          <p className="text-slate-500">{emp.role} • {emp.seniority} • {emp.team_name} • {emp.tenure_months}mo tenure</p>
        </div>
        <div className="flex gap-2">
          <button
            onClick={() => setActiveTab('manager')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === 'manager' ? 'bg-pulse-600 text-white' : 'bg-white border text-slate-600 hover:bg-slate-50'}`}
          >
            👔 Manager View
          </button>
          <button
            onClick={() => setActiveTab('employee')}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${activeTab === 'employee' ? 'bg-pulse-600 text-white' : 'bg-white border text-slate-600 hover:bg-slate-50'}`}
          >
            👤 Employee View
          </button>
        </div>
      </div>

      {/* Score cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        {insights.scores.map((s) => (
          <div key={s.score_name} className="bg-white rounded-xl border p-4 text-center">
            <div className="text-sm text-slate-500 mb-1 capitalize">
              {s.score_name.replace(/_/g, ' ')}
            </div>
            <ScoreBadge
              score={s.score}
              label={s.label}
              reversed={s.score_name === 'high_potential'}
              large
            />
            <div className="text-xs text-slate-400 mt-1">
              Confidence: {(s.confidence * 100).toFixed(0)}%
            </div>
          </div>
        ))}
      </div>

      {/* Blow-their-minds features */}
      {insights.predictive_burnout && (
        <PredictiveBurnout data={insights.predictive_burnout} />
      )}
      {insights.hidden_talent && <HiddenTalent name={emp.name} />}

      {/* Signal Charts */}
      <div className="bg-white rounded-xl border p-6">
        <h2 className="text-xl font-semibold mb-4">📊 Signal Timeline (8 weeks)</h2>
        <SignalChart signals={insights.signals} />
      </div>

      {/* Explainability Cards */}
      <div>
        <h2 className="text-xl font-semibold mb-4">🔍 Explainability – Why These Scores?</h2>
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {insights.scores.map((s) => (
            <ExplainCard key={s.score_name} card={s} />
          ))}
        </div>
      </div>

      {/* Recommendations */}
      <div className="bg-white rounded-xl border p-6">
        <h2 className="text-xl font-semibold mb-4">💡 Recommendations</h2>
        <ul className="space-y-3">
          {insights.recommendations.map((rec, i) => (
            <li key={i} className="flex items-start gap-3 p-3 bg-slate-50 rounded-lg">
              <span className="text-lg">{rec.charAt(0) === '🔴' || rec.charAt(0) === '⚠' ? '' : ''}</span>
              <span className="text-sm text-slate-700">{rec}</span>
            </li>
          ))}
        </ul>
      </div>

      {/* Skills */}
      {insights.skills.length > 0 && (
        <div className="bg-white rounded-xl border p-6">
          <h2 className="text-xl font-semibold mb-4">🎯 Skills Matrix</h2>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {insights.skills.map((sk, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-slate-50 rounded-lg">
                <div>
                  <span className="text-sm font-medium">{sk.skill_name}</span>
                  {sk.is_growing && <span className="ml-2 text-xs text-green-600">📈 Growing</span>}
                </div>
                <div className="flex gap-0.5">
                  {[1, 2, 3, 4, 5].map(n => (
                    <div key={n} className={`w-2 h-6 rounded-sm ${n <= sk.proficiency ? 'bg-pulse-500' : 'bg-slate-200'}`} />
                  ))}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* Manager-only: Generation buttons */}
      {activeTab === 'manager' && (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="bg-white rounded-xl border p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">🤝 1:1 Coaching Agenda</h2>
              <button
                onClick={generateQuestions}
                disabled={genLoading.questions}
                className="px-4 py-2 bg-pulse-600 text-white rounded-lg hover:bg-pulse-700 disabled:opacity-50 text-sm"
              >
                {genLoading.questions ? '⏳ Generating...' : '✨ Generate'}
              </button>
            </div>
            {questions && <CoachingPanel data={questions} />}
          </div>

          <div className="bg-white rounded-xl border p-6">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-xl font-semibold">📝 Performance Review Draft</h2>
              <button
                onClick={generateReview}
                disabled={genLoading.review}
                className="px-4 py-2 bg-pulse-600 text-white rounded-lg hover:bg-pulse-700 disabled:opacity-50 text-sm"
              >
                {genLoading.review ? '⏳ Generating...' : '✨ Generate'}
              </button>
            </div>
            {review && <ReviewPanel data={review} />}
          </div>
        </div>
      )}

      {/* Employee view: Transparency */}
      {activeTab === 'employee' && (
        <div className="bg-blue-50 border border-blue-200 rounded-xl p-6">
          <h2 className="text-xl font-semibold text-blue-800 mb-3">🔒 Your Data Transparency</h2>
          <div className="space-y-3 text-sm text-blue-700">
            <p>This view shows exactly what signals are collected about you and how they influence your scores.</p>
            <div className="bg-white p-4 rounded-lg">
              <h3 className="font-semibold mb-2">What we collect (aggregated metadata only):</h3>
              <ul className="list-disc list-inside space-y-1">
                <li>Meeting counts and durations (NOT content, topics, or recordings)</li>
                <li>Task completion trends (NOT what you&apos;re working on)</li>
                <li>Collaboration breadth (who you interact with, NOT conversations)</li>
                <li>Working hour patterns (NOT keystrokes, screens, or location)</li>
              </ul>
            </div>
            <div className="bg-white p-4 rounded-lg">
              <h3 className="font-semibold mb-2">What we NEVER collect:</h3>
              <ul className="list-disc list-inside space-y-1 text-red-600">
                <li>❌ Message bodies, email subjects, or attachments</li>
                <li>❌ Screen recordings, screenshots, or webcam feed</li>
                <li>❌ Keystrokes or application usage</li>
                <li>❌ GPS location or device tracking</li>
                <li>❌ Meeting transcripts or chat content</li>
              </ul>
            </div>
            {insights.scores[0]?.fairness_warning && (
              <div className="bg-amber-50 p-4 rounded-lg border border-amber-200">
                <h3 className="font-semibold text-amber-800">Fairness Note:</h3>
                <p className="text-amber-700">{insights.scores[0].fairness_warning}</p>
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
