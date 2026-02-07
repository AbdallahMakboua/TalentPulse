import { render, screen } from '@testing-library/react';
import { AlertsList } from '@/components/AlertsList';

// Mock next/link
jest.mock('next/link', () => {
  return ({ children, href }: { children: React.ReactNode; href: string }) => (
    <a href={href}>{children}</a>
  );
});

describe('AlertsList', () => {
  it('shows empty state when no alerts', () => {
    render(<AlertsList alerts={[]} />);
    expect(screen.getByText(/No active alerts/)).toBeInTheDocument();
  });

  it('renders alerts with full props', () => {
    render(
      <AlertsList
        alerts={[
          {
            employee_id: 1,
            employee_name: 'Alice Chen',
            type: 'burnout_risk',
            severity: 'critical',
            message: 'Burnout risk increasing rapidly',
          },
        ]}
      />
    );
    expect(screen.getByText('Alice Chen')).toBeInTheDocument();
    expect(screen.getByText('Burnout risk increasing rapidly')).toBeInTheDocument();
    expect(screen.getByText('critical')).toBeInTheDocument();
  });

  it('renders alerts with minimal props (from org overview)', () => {
    render(
      <AlertsList
        alerts={[
          {
            type: 'burnout_risk',
            employee: 'Bob Smith',
            team: 'Engineering',
            score: 78,
            message: 'High burnout risk detected',
          },
        ]}
      />
    );
    expect(screen.getByText('Bob Smith')).toBeInTheDocument();
    expect(screen.getByText('High burnout risk detected')).toBeInTheDocument();
  });

  it('shows alert count', () => {
    render(
      <AlertsList
        alerts={[
          { type: 'burnout_risk', message: 'Alert 1', employee_name: 'A' },
          { type: 'high_pressure', message: 'Alert 2', employee_name: 'B' },
        ]}
      />
    );
    expect(screen.getByText('(2)')).toBeInTheDocument();
  });

  it('links to employee detail page when id provided', () => {
    render(
      <AlertsList
        alerts={[
          { employee_id: 5, employee_name: 'Test', type: 'burnout_risk', message: 'Test msg' },
        ]}
      />
    );
    const link = screen.getByText('Test').closest('a');
    expect(link?.getAttribute('href')).toBe('/employees/5');
  });
});
