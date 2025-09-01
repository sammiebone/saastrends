import React from 'react';
import { render, screen } from '@testing-library/react';
import InventoryManager from './InventoryManager';

test('renders inventory manager component', () => {
  render(<InventoryManager />);
  const headingElement = screen.getByText(/Inventory Management/i);
  expect(headingElement).toBeInTheDocument();
});
