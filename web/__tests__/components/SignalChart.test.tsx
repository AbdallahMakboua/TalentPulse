import { render, screen } from '@testing-library/react';
import { SignalChart } from '@/components/SignalChart';

// Mock recharts to avoid canvas issues in jsdom
jest.mock('recharts', () => {
  const OriginalModule = jest.requireActual('recharts');
  return {
    ...OriginalModule,
    ResponsiveContainer: ({ children }: { children: React.ReactNode }) => (
      <div data-testid="responsive-container">{children}</div>
    ),
  };
});

describe('SignalChart', () => {
  const signals = [
    { week_start: '2026-02-02', meeting_hours: 20, focus_hours: 15, after_hours: 5, collab_hours: 10 },
    { week_start: '2026-02-09', meeting_hours: 22, focus_hours: 13, after_hours: 7, collab_hours: 11 },
    { week_start: '2026-02-16', meeting_hours: 25, focus_hours: 10, after_hours: 9, collab_hours: 12 },
  ];

  it('renders empty state when no signals', () => {
    render(<SignalChart signals={[]} />);
    expect(screen.getByText('No signal data available yet.')).toBeInTheDocument();
  });

  it('renders chart with data', () => {
    render(<SignalChart signals={signals} />);
    expect(screen.getByText('Weekly Signals')).toBeInTheDocument();
    expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
  });

  it('renders custom title', () => {
    render(<SignalChart signals={signals} title="Custom Title" />);
    expect(screen.getByText('Custom Title')).toBeInTheDocument();
  });

  it('renders with custom metrics', () => {
    render(
      <SignalChart
        signals={signals}
        metrics={['meeting_hours', 'after_hours']}
      />
    );
    expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
  });
});
