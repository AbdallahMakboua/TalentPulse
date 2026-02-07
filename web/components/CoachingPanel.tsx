'use client';

import { useState } from 'react';
import { MessageSquare, Loader2, Lightbulb, Sparkles } from 'lucide-react';
import { api } from '@/lib/api';

interface QuestionsData {
  employee_name?: string;
  questions: string[];
  listening_cues?: string[];
  follow_up_actions?: string[];
  context_notes?: string[];
  context_summary?: string;
  generated_by?: string;
  source?: string;
}

interface Props {
  employeeId?: number;
  data?: QuestionsData;
}

export function CoachingPanel({ employeeId, data: initialData }: Props) {
  const [questions, setQuestions] = useState<string[] | null>(initialData?.questions || null);
  const [context, setContext] = useState<string>(initialData?.context_summary || initialData?.context_notes?.join('; ') || '');
  const [loading, setLoading] = useState(false);
  const [source, setSource] = useState<string>(initialData?.generated_by || initialData?.source || '');

  const generate = async () => {
    if (!employeeId) return;
    setLoading(true);
    try {
      const res = await api.employeeQuestions(String(employeeId));
      setQuestions(res.questions);
      setContext(res.context_notes?.join('; ') || '');
      setSource(res.generated_by || 'template');
    } catch {
      setQuestions(['Failed to generate — try again later.']);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-white rounded-xl border border-slate-200 p-6 shadow-sm">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center gap-2">
          <Sparkles className="w-4 h-4 text-violet-500" />
          <h3 className="text-sm font-semibold text-slate-700">Coaching Copilot</h3>
        </div>
        {source && (
          <span className="text-[10px] bg-violet-100 text-violet-600 px-2 py-0.5 rounded-full">
            {source === 'ollama' ? 'AI-Generated' : 'Template'}
          </span>
        )}
      </div>
      <p className="text-xs text-slate-400 mb-4">
        Generate a data-informed 1:1 agenda with coaching questions.
      </p>

      {!questions && (
        <button
          onClick={generate}
          disabled={loading}
          className="flex items-center gap-2 px-4 py-2 bg-violet-600 text-white rounded-lg text-sm font-medium hover:bg-violet-700 transition-colors disabled:opacity-50"
        >
          {loading ? (
            <Loader2 className="w-4 h-4 animate-spin" />
          ) : (
            <MessageSquare className="w-4 h-4" />
          )}
          Generate 1:1 Agenda
        </button>
      )}

      {questions && (
        <div className="space-y-3">
          {context && (
            <div className="bg-violet-50 border border-violet-100 rounded-lg p-3">
              <div className="flex items-center gap-1.5 mb-1">
                <Lightbulb className="w-3 h-3 text-violet-500" />
                <span className="text-[11px] font-medium text-violet-600">Context</span>
              </div>
              <p className="text-xs text-slate-600">{context}</p>
            </div>
          )}
          <ol className="space-y-2">
            {questions.map((q, i) => (
              <li key={i} className="flex items-start gap-2">
                <span className="text-xs font-bold text-violet-500 mt-0.5 shrink-0">
                  {i + 1}.
                </span>
                <span className="text-sm text-slate-700">{q}</span>
              </li>
            ))}
          </ol>
          <button
            onClick={generate}
            disabled={loading}
            className="text-xs text-violet-600 hover:text-violet-700 font-medium mt-2"
          >
            {loading ? 'Regenerating…' : '↻ Regenerate'}
          </button>
        </div>
      )}
    </div>
  );
}
