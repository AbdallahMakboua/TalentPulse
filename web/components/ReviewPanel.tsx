'use client';

import { useState } from 'react';
import { FileText, Loader2, Copy, Check, Sparkles } from 'lucide-react';
import { api } from '@/lib/api';

interface ReviewData {
  employee_name?: string;
  period?: string;
  highlights?: string[];
  growth_areas?: string[];
  risks?: string[];
  suggested_goals?: string[];
  summary?: string;
  review_draft?: string;
  generated_by?: string;
  source?: string;
}

interface Props {
  employeeId?: number;
  data?: ReviewData;
}

export function ReviewPanel({ employeeId, data: initialData }: Props) {
  const formatReview = (d: ReviewData): string => {
    if (d.review_draft) return d.review_draft;
    const parts: string[] = [];
    if (d.summary) parts.push(d.summary);
    if (d.highlights?.length) parts.push('\nHighlights:\n' + d.highlights.map(h => `• ${h}`).join('\n'));
    if (d.growth_areas?.length) parts.push('\nGrowth Areas:\n' + d.growth_areas.map(g => `• ${g}`).join('\n'));
    if (d.suggested_goals?.length) parts.push('\nSuggested Goals:\n' + d.suggested_goals.map(g => `• ${g}`).join('\n'));
    return parts.join('\n') || 'No review data available.';
  };

  const [review, setReview] = useState<string | null>(initialData ? formatReview(initialData) : null);
  const [tone, setTone] = useState<string>('balanced');
  const [loading, setLoading] = useState(false);
  const [source, setSource] = useState<string>(initialData?.generated_by || '');
  const [copied, setCopied] = useState(false);

  const generate = async () => {
    if (!employeeId) return;
    setLoading(true);
    try {
      const res = await api.employeeReview(String(employeeId));
      setReview(formatReview(res));
      setSource(res.generated_by || 'template');
    } catch {
      setReview('Failed to generate review — please try again.');
    } finally {
      setLoading(false);
    }
  };

  const copyToClipboard = async () => {
    if (!review) return;
    await navigator.clipboard.writeText(review);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-emerald-500" />
          <h3 className="text-sm font-semibold text-slate-700">Review Draft Generator</h3>
        </div>
        {source && (
          <span className="text-[10px] bg-emerald-100 text-emerald-600 px-2 py-0.5 rounded-full">
            {source === 'ollama' ? 'AI-Generated' : 'Template'}
          </span>
        )}
      </div>

      <div className="flex items-center gap-2 mb-4">
        <label className="text-xs text-slate-500">Tone:</label>
        {['balanced', 'supportive', 'direct'].map((t) => (
          <button
            key={t}
            onClick={() => setTone(t)}
            className={`text-xs px-3 py-1 rounded-full border transition-colors ${
              tone === t
                ? 'bg-emerald-600 text-white border-emerald-600'
                : 'bg-white text-slate-600 border-slate-200 hover:border-emerald-300'
            }`}
          >
            {t.charAt(0).toUpperCase() + t.slice(1)}
          </button>
        ))}
      </div>

      {!review && (
        <button
          onClick={generate}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-emerald-600 text-white rounded-lg text-sm font-medium hover:bg-emerald-700 transition-colors disabled:opacity-50"
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <FileText className="w-4 h-4" />
          )}
          Generate Review Draft
        </button>
      )}

      {review && (
        <div className="space-y-3">
          <div className="bg-slate-50 border border-slate-200 rounded-lg p-4 text-sm text-slate-700 whitespace-pre-wrap leading-relaxed">
            {review}
          </div>
          <div className="flex items-center gap-3">
            <button
              onClick={copyToClipboard}
              className="flex items-center gap-1.5 text-xs text-slate-500 hover:text-slate-700"
            >
              {copied ? (
                <Check className="w-3 h-3 text-green-500" />
              ) : (
                <Copy className="w-3 h-3" />
              )}
              {copied ? 'Copied!' : 'Copy to clipboard'}
            </button>
            <button
              onClick={generate}
              disabled={loading}
              className="text-xs text-emerald-600 hover:text-emerald-700 font-medium"
            >
              {loading ? 'Regenerating…' : '↻ Regenerate'}
            </button>
          </div>
          <p className="text-[11px] text-slate-400 italic">
            This is a starting point, not a final review. Always add your personal observations.
          </p>
        </div>
      )}
    </div>
  );
}
