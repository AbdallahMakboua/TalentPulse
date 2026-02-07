import { render, screen } from '@testing-library/react';
import { PredictiveBurnout } from '@/components/PredictiveBurnout';

describe('PredictiveBurnout', () => {
  it('renders nothing when no data', () => {
    const { container } = render(<PredictiveBurnout />);
    expect(container.firstChild).toBeNull();
  });

  it('renders nothing when prediction is null', () => {
    const { container } = render(<PredictiveBurnout prediction={null} />);
    expect(container.firstChild).toBeNull();
  });

  it('renders at-risk state with high score', () => {
    render(
      <PredictiveBurnout
        data={{
          alert: 'high',
          message: 'Burnout detected',
          current_score: 78,
          projected_weeks: 3,
          pattern_signals: { after_hours: 12, meeting_hours: 30 },
          confidence: 0.82,
          uncertainty: 'moderate',
          recommended_action: 'Reduce meeting load',
        }}
      />
    );
    expect(screen.getByText('Predictive Burnout Alert')).toBeInTheDocument();
    expect(screen.getByText('AT RISK')).toBeInTheDocument();
    expect(screen.getByText('78')).toBeInTheDocument();
    expect(screen.getByText('3w')).toBeInTheDocument();
  });

  it('renders safe state with low score', () => {
    render(
      <PredictiveBurnout
        prediction={{
          at_risk: false,
          score: 20,
          label: 'Low',
          factors: [],
          trend: 'stable',
          current_score: 20,
        }}
      />
    );
    expect(screen.getByText('20')).toBeInTheDocument();
    expect(screen.getByText('Stable')).toBeInTheDocument();
    expect(screen.queryByText('AT RISK')).not.toBeInTheDocument();
  });

  it('shows contributing factors from pattern_signals', () => {
    render(
      <PredictiveBurnout
        data={{
          current_score: 70,
          pattern_signals: { after_hours: 12, weekend_activity: 5 },
          alert: 'high',
          message: 'Risk rising',
          confidence: 0.9,
          uncertainty: 'low',
          recommended_action: 'Take PTO',
        }}
      />
    );
    expect(screen.getByText('after_hours: 12')).toBeInTheDocument();
    expect(screen.getByText('weekend_activity: 5')).toBeInTheDocument();
  });
});
