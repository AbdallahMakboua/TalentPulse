import { render, screen } from '@testing-library/react';
import { ExplainCard } from '@/components/ExplainCard';

describe('ExplainCard', () => {
  const explanations = [
    {
      dimension: 'burnout_risk',
      score: 72,
      label: 'High',
      top_factors: ['After-hours events trending up', 'Focus hours declining'],
      bias_note: 'Score adjusted for seniority cohort',
    },
    {
      dimension: 'high_potential',
      score: 45,
      label: 'Medium',
      top_factors: ['Strong cross-team collaboration'],
    },
  ];

  it('renders nothing when no explanations', () => {
    const { container } = render(<ExplainCard explanations={[]} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders all explanation cards', () => {
    render(<ExplainCard explanations={explanations} />);
    expect(screen.getByText('Burnout Risk')).toBeInTheDocument();
    expect(screen.getByText('High Potential')).toBeInTheDocument();
  });

  it('shows score and label', () => {
    render(<ExplainCard explanations={explanations} />);
    expect(screen.getByText('72 — High')).toBeInTheDocument();
    expect(screen.getByText('45 — Medium')).toBeInTheDocument();
  });

  it('shows top factors', () => {
    render(<ExplainCard explanations={explanations} />);
    expect(screen.getByText('After-hours events trending up')).toBeInTheDocument();
    expect(screen.getByText('Focus hours declining')).toBeInTheDocument();
  });

  it('shows bias note when present', () => {
    render(<ExplainCard explanations={explanations} />);
    expect(screen.getByText('Score adjusted for seniority cohort')).toBeInTheDocument();
  });

  it('works in single-card mode', () => {
    render(<ExplainCard card={{
      score_name: 'high_pressure',
      score: 60,
      label: 'Medium',
      top_contributors: [{ signal: 'meeting_hours', value: 25, direction: 'up', delta: '+3', normalized: 0.7, weight: 0.3, contribution: 0.21 }],
      trend_explanation: 'Meetings increased last 3 weeks',
      confidence: 0.85,
      limitations: 'Limited data points',
      fairness_warning: 'Cohort baseline applied',
    }} />);
    expect(screen.getByText(/high pressure/i)).toBeInTheDocument();
    expect(screen.getByText('meeting_hours: 25 (up +3)')).toBeInTheDocument();
    expect(screen.getByText('Meetings increased last 3 weeks')).toBeInTheDocument();
    expect(screen.getByText('Cohort baseline applied')).toBeInTheDocument();
    expect(screen.getByText(/Confidence: 85%/)).toBeInTheDocument();
  });
});
