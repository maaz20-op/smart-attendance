import { render, screen } from '@testing-library/react';
import { describe, it, expect } from 'vitest';
import { MemoryRouter } from 'react-router-dom';
import MarkAttendance from '../MarkAttendance';

vi.mock('../../hooks/useCurrentUser', () => ({
    useCurrentUser: () => ({
        user: { name: 'Test Student', role: 'student' },
        isAuthenticated: true
    })
}));

describe('MarkAttendance Component', () => {
    it('renders correctly', () => {
        // This test assumes MarkAttendance renders something identifiable
        // We'll wrap in error boundary or just see if it mounts without crashing
        
        const { container } = render(
            <MemoryRouter>
                <MarkAttendance />
            </MemoryRouter>
        );
        
        expect(container).toBeInTheDocument();
    });
});
