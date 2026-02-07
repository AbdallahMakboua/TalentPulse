import { render, screen } from '@testing-library/react';
import { HiddenTalent } from '@/components/HiddenTalent';

describe('HiddenTalent', () => {
  it('renders nothing when no data and no name', () => {
    const { container } = render(<HiddenTalent />);
    expect(container.firstChild).toBeNull();
  });

  it('renders with name only (uses default signals)', () => {
    render(<HiddenTalent name="Alice" />);
    expect(screen.getByText('Hidden Talent Detected')).toBeInTheDocument();
    expect(screen.getByText('QUIET IMPACT')).toBeInTheDocument();
    expect(screen.getByText(/Alice/)).toBeInTheDocument();
  });

  it('renders with full data', () => {
    render(
      <HiddenTalent
        data={{
          detected: true,
          signals: ['High peer support score', 'Cross-team collaboration above average'],
          recommendation: 'Consider for tech lead role',
        }}
      />
    );
    expect(screen.getByText('High peer support score')).toBeInTheDocument();
    expect(screen.getByText('Cross-team collaboration above average')).toBeInTheDocument();
    expect(screen.getByText('Consider for tech lead role')).toBeInTheDocument();
  });

  it('shows privacy disclaimer', () => {
    render(<HiddenTalent name="Bob" />);
    expect(screen.getByText(/quiet-impact scoring/)).toBeInTheDocument();
  });
});
