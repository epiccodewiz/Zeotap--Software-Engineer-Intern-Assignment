# Google Sheets Clone

A lightweight, React-based spreadsheet application that mimics the core functionality and user interface of Google Sheets. This project implements essential spreadsheet features including formula evaluation, cell formatting, and dynamic cell dependencies.

## Features

### Core Functionality
- Excel-like grid with rows, columns, and editable cells
- Formula bar for inputting and editing cell content
- Support for cell references (e.g., A1, B2)
- Formula evaluation (e.g., =SUM(A1:A5))
- Cell dependency tracking and automatic recalculation

### Supported Formulas
- **SUM** - Adds all values in a range
- **AVERAGE** - Calculates the mean of values in a range
- **MAX** - Returns the maximum value in a range
- **MIN** - Returns the minimum value in a range
- **COUNT** - Counts numerical values in a range
- **TRIM** - Removes leading and trailing spaces
- **UPPER** - Converts text to uppercase
- **LOWER** - Converts text to lowercase
- Basic arithmetic operations (+, -, *, /)

### UI Features
- Responsive grid layout
- Column and row headers (A, B, C... and 1, 2, 3...)
- Cell selection and editing
- Keyboard navigation (arrow keys, Enter, Tab)
- Basic formatting options (bold, italic)
- Google Sheets-inspired toolbar and status bar

## Technologies Used

- **React** - Frontend library for building the user interface
- **React Hooks** - Used for state management and side effects
  - useState - Managing application state
  - useEffect - Handling side effects and initialization
  - useRef - Direct DOM access and value persistence
- **CSS3** - Styling the application
- **JavaScript ES6+** - Core programming language
  - Arrow functions
  - Destructuring
  - Template literals
  - Array and object spread operators

## Getting Started

### Prerequisites
- Node.js (v12 or higher)
- npm (v6 or higher)

### Installation

1. Clone the repository
```bash
git clone https://github.com/epiccodewiz/Zeotap--Software-Engineer-Intern-Assignment.git
cd google-sheets-clone
```

2. Install dependencies
```bash
npm install
```

3. Start the development server
```bash
npm start
```

4. Open your browser and navigate to `http://localhost:3000`

## Implementation Details

### Cell Data Structure

Each cell in the spreadsheet is represented by an object with the following properties:

```javascript
{
  id: "A1",              // Cell identifier
  value: "=SUM(B1:B5)",  // Raw value/formula
  displayValue: "15",    // Calculated/displayed value
  formula: "=SUM(B1:B5)", // Formula if present
  formatting: {          // Cell formatting
    bold: false,
    italic: false,
    fontSize: 12,
    color: "#000000",
    backgroundColor: "#ffffff"
  },
  dependencies: ["B1", "B2", "B3", "B4", "B5"], // Cells this cell depends on
  dependents: ["C1", "D1"]  // Cells that depend on this cell
}
```

### Formula Evaluation Process

The formula evaluation system follows these steps:

1. Detect if a cell contains a formula (starts with '=')
2. Parse the formula to identify function type (SUM, AVERAGE, etc.)
3. Extract cell references and ranges
4. Resolve references to their values
5. Perform the calculation
6. Update dependent cells recursively

### Cell Dependency Management

The application maintains a dependency graph to ensure that when a cell's value changes, all dependent cells are recalculated:

1. When a cell's formula changes, its dependencies are extracted
2. The cell is added as a dependent to each of its dependencies
3. When a cell's value changes, all its dependents are recalculated
4. The process continues recursively through the dependency chain


