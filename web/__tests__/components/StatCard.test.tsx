import { render, screen } from '@testing-library/react';
import { StatCard } from '@/components/StatCard';

describe('StatCard', () => {
  it('renders title and value', () => {
    render(<StatCard title="Employees" value={42} icon="👥" />);
    expect(screen.getByText('Employees')).toBeInTheDocument();
    expect(screen.getByText('42')).toBeInTheDocument();
    expect(screen.getByText('👥')).toBeInTheDocument();
  });

  it('renders subtitle when provided', () => {
    render(<StatCard title="Alerts" value={3} icon="🔴" subtitle="2 medium risk" />);
    expect(screen.getByText('2 medium risk')).toBeInTheDocument();
  });

  it('applies danger variant styling', () => {
    const { container } = render(<StatCard title="Risk" value={5} icon="⚠️" variant="danger" />);
    const card = container.firstChild as HTMLElement;
    expect(card.className).toContain('border-red');
  });

  it('applies success variant styling', () => {
    const { container } = render(<StatCard title="Stars" value={5} icon="⭐" variant="success" />);
    const card = container.firstChild as HTMLElement;
    expect(card.className).toContain('border-green');
  });

  it('defaults to neutral styling when no variant', () => {
    const { container } = render(<StatCard title="Count" value={10} icon="📊" />);
    const card = container.firstChild as HTMLElement;
    expect(card.className).toContain('bg-white');
  });
});
