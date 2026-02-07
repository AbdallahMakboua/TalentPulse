import { render, screen } from '@testing-library/react';
import { RiskDistribution } from '@/components/RiskDistribution';

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

describe('RiskDistribution', () => {
  it('renders with distribution prop', () => {
    render(
      <RiskDistribution
        distribution={{ low: 5, medium: 3, high: 2 }}
        title="Burnout Risk"
      />
    );
    expect(screen.getByText('Burnout Risk')).toBeInTheDocument();
  });

  it('renders with data prop (alternative syntax)', () => {
    render(
      <RiskDistribution
        data={{ low: 10, high: 1 }}
        title="Pressure"
      />
    );
    expect(screen.getByText('Pressure')).toBeInTheDocument();
  });

  it('uses default title when none provided', () => {
    render(<RiskDistribution distribution={{ low: 5 }} />);
    expect(screen.getByText('Risk Distribution')).toBeInTheDocument();
  });

  it('renders the chart container', () => {
    render(<RiskDistribution distribution={{ low: 5, medium: 3, high: 2 }} />);
    expect(screen.getByTestId('responsive-container')).toBeInTheDocument();
  });
});
