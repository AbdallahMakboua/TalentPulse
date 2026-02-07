import { render, screen } from '@testing-library/react';
import { ScoreBadge } from '@/components/ScoreBadge';

describe('ScoreBadge', () => {
  it('renders score value', () => {
    render(<ScoreBadge score={72.4} label="High" />);
    expect(screen.getByText('72')).toBeInTheDocument();
    expect(screen.getByText('High')).toBeInTheDocument();
  });

  it('applies red color for High label (default non-reversed)', () => {
    const { container } = render(<ScoreBadge score={80} label="High" />);
    const badge = container.querySelector('.rounded-full');
    expect(badge?.className).toContain('bg-red');
  });

  it('applies green color for High label when reversed', () => {
    const { container } = render(<ScoreBadge score={80} label="High" reversed />);
    const badge = container.querySelector('.rounded-full');
    expect(badge?.className).toContain('bg-green');
  });

  it('applies amber color for Medium label', () => {
    const { container } = render(<ScoreBadge score={50} label="Medium" />);
    const badge = container.querySelector('.rounded-full');
    expect(badge?.className).toContain('bg-amber');
  });

  it('applies green color for Low label (non-reversed)', () => {
    const { container } = render(<ScoreBadge score={20} label="Low" />);
    const badge = container.querySelector('.rounded-full');
    expect(badge?.className).toContain('bg-green');
  });

  it('renders large variant', () => {
    const { container } = render(<ScoreBadge score={90} label="High" large />);
    const scoreEl = container.querySelector('.text-2xl');
    expect(scoreEl).toBeInTheDocument();
  });

  it('handles unknown labels gracefully', () => {
    const { container } = render(<ScoreBadge score={0} label="N/A" />);
    const badge = container.querySelector('.rounded-full');
    expect(badge?.className).toContain('bg-slate');
  });
});
