import { render, screen, waitFor } from '@testing-library/react';
import { describe, it, expect, vi } from 'vitest';
import Dashboard from '../Dashboard';
import { MemoryRouter } from 'react-router-dom';

// Mock dependencies
vi.mock('../../hooks/useCurrentUser', () => ({
    useCurrentUser: () => ({
        user: { name: 'Test User', role: 'student' },
        isAuthenticated: true
    })
}));

// Mock API calls if the component fetches data directly on mount
vi.mock('../../api/attendance', () => ({
    getAttendanceSummary: vi.fn().mockResolvedValue({
        total_classes: 20,
        attended: 18,
        percentage: 90
    }),
    getRecentActivity: vi.fn().mockResolvedValue([])
}));

describe('Dashboard Component', () => {
    it('renders dashboard content', async () => {
        render(
            <MemoryRouter>
                <Dashboard />
            </MemoryRouter>
        );
        
        // Wait for async content or loading state
        await waitFor(() => {
            expect(screen.getByText(/Test User/i)).toBeInTheDocument();
            // Assuming dashboard shows attendance summary
            expect(screen.getByText(/20/i)).toBeInTheDocument(); // total classes
            expect(screen.getByText(/90/i)).toBeInTheDocument(); // percentage
        });
    });
});
