import React, { useState, useEffect, useRef } from 'react';
import './Spreadsheet.css';

// Utility functions for cell references
const colIndexToLetter = (index) => {
  let letter = '';
  while (index >= 0) {
    letter = String.fromCharCode(65 + (index % 26)) + letter;
    index = Math.floor(index / 26) - 1;
  }
  return letter;
};

const cellIdToPosition = (cellId) => {
  const colLetters = cellId.match(/[A-Z]+/)[0];
  const rowNumber = parseInt(cellId.match(/\d+/)[0]);
  
  let colIndex = 0;
  for (let i = 0; i < colLetters.length; i++) {
    colIndex = colIndex * 26 + (colLetters.charCodeAt(i) - 64);
  }
  colIndex -= 1;
  
  return { row: rowNumber - 1, col: colIndex };
};

const positionToCellId = (row, col) => {
  return `${colIndexToLetter(col)}${row + 1}`;
};

// Formula parsing and evaluation
const evaluateFormula = (formula, cellsData) => {
  if (!formula.startsWith('=')) return formula;
  
  try {
    const expression = formula.substring(1).toUpperCase();
    
    // Handle SUM function
    if (expression.startsWith('SUM(') && expression.endsWith(')')) {
      const range = expression.substring(4, expression.length - 1);
      return sumRange(range, cellsData);
    }
    
    // Handle AVERAGE function
    if (expression.startsWith('AVERAGE(') && expression.endsWith(')')) {
      const range = expression.substring(8, expression.length - 1);
      const sum = sumRange(range, cellsData);
      const count = countRange(range, cellsData);
      return count > 0 ? sum / count : 0;
    }
    
    // Handle MAX function
    if (expression.startsWith('MAX(') && expression.endsWith(')')) {
      const range = expression.substring(4, expression.length - 1);
      return maxRange(range, cellsData);
    }
    
    // Handle MIN function
    if (expression.startsWith('MIN(') && expression.endsWith(')')) {
      const range = expression.substring(4, expression.length - 1);
      return minRange(range, cellsData);
    }
    
    // Handle COUNT function
    if (expression.startsWith('COUNT(') && expression.endsWith(')')) {
      const range = expression.substring(6, expression.length - 1);
      return countRange(range, cellsData);
    }
    
    // Handle TRIM function
    if (expression.startsWith('TRIM(') && expression.endsWith(')')) {
      const cellRef = expression.substring(5, expression.length - 1);
      const cellValue = getCellValue(cellRef, cellsData);
      return typeof cellValue === 'string' ? cellValue.trim() : cellValue;
    }
    
    // Handle UPPER function
    if (expression.startsWith('UPPER(') && expression.endsWith(')')) {
      const cellRef = expression.substring(6, expression.length - 1);
      const cellValue = getCellValue(cellRef, cellsData);
      return typeof cellValue === 'string' ? cellValue.toUpperCase() : cellValue;
    }
    
    // Handle LOWER function
    if (expression.startsWith('LOWER(') && expression.endsWith(')')) {
      const cellRef = expression.substring(6, expression.length - 1);
      const cellValue = getCellValue(cellRef, cellsData);
      return typeof cellValue === 'string' ? cellValue.toLowerCase() : cellValue;
    }
    
    // Basic arithmetic operations
    return evaluateExpression(expression, cellsData);
  } catch (error) {
    return '#ERROR!';
  }
};

const sumRange = (range, cellsData) => {
  const cells = expandRange(range);
  let sum = 0;
  
  cells.forEach(cellId => {
    const value = getCellValue(cellId, cellsData);
    if (!isNaN(parseFloat(value))) {
      sum += parseFloat(value);
    }
  });
  
  return sum;
};

const countRange = (range, cellsData) => {
  const cells = expandRange(range);
  let count = 0;
  
  cells.forEach(cellId => {
    const value = getCellValue(cellId, cellsData);
    if (!isNaN(parseFloat(value))) {
      count++;
    }
  });
  
  return count;
};

const maxRange = (range, cellsData) => {
  const cells = expandRange(range);
  let max = Number.NEGATIVE_INFINITY;
  let foundNumber = false;
  
  cells.forEach(cellId => {
    const value = getCellValue(cellId, cellsData);
    if (!isNaN(parseFloat(value))) {
      max = Math.max(max, parseFloat(value));
      foundNumber = true;
    }
  });
  
  return foundNumber ? max : 0;
};

const minRange = (range, cellsData) => {
  const cells = expandRange(range);
  let min = Number.POSITIVE_INFINITY;
  let foundNumber = false;
  
  cells.forEach(cellId => {
    const value = getCellValue(cellId, cellsData);
    if (!isNaN(parseFloat(value))) {
      min = Math.min(min, parseFloat(value));
      foundNumber = true;
    }
  });
  
  return foundNumber ? min : 0;
};

const expandRange = (range) => {
  // Handle single cell reference
  if (/^[A-Z]+\d+$/.test(range)) {
    return [range];
  }
  
  // Handle range like 'A1:B3'
  const rangeMatch = range.match(/([A-Z]+\d+):([A-Z]+\d+)/);
  if (rangeMatch) {
    const startCell = rangeMatch[1];
    const endCell = rangeMatch[2];
    const start = cellIdToPosition(startCell);
    const end = cellIdToPosition(endCell);
    
    const cells = [];
    for (let row = Math.min(start.row, end.row); row <= Math.max(start.row, end.row); row++) {
      for (let col = Math.min(start.col, end.col); col <= Math.max(start.col, end.col); col++) {
        cells.push(positionToCellId(row, col));
      }
    }
    return cells;
  }
  
  // Handle comma-separated list like 'A1,B2,C3'
  return range.split(',').map(ref => ref.trim());
};

const getCellValue = (cellId, cellsData) => {
  const cell = cellsData[cellId];
  if (!cell) return '';
  
  if (cell.formula && cell.formula.startsWith('=')) {
    return cell.displayValue;
  }
  
  return cell.value;
};

const evaluateExpression = (expression, cellsData) => {
  // Replace cell references with their values
  const expressionWithValues = expression.replace(/[A-Z]+\d+/g, (match) => {
    const value = getCellValue(match, cellsData);
    if (isNaN(parseFloat(value))) {
      throw new Error('Non-numeric value in expression');
    }
    return parseFloat(value);
  });
  
  // Use Function constructor for safe evaluation
  // eslint-disable-next-line no-new-func
  return Function(`'use strict'; return (${expressionWithValues})`)();
};

// Main Spreadsheet component
const Spreadsheet = () => {
  const [rowCount, setRowCount] = useState(20);
  const [colCount, setColCount] = useState(10);
  const [cells, setCells] = useState({});
  const [selectedCell, setSelectedCell] = useState(null);
  const [editingCell, setEditingCell] = useState(null);
  const [editValue, setEditValue] = useState('');
  const [formulaBarValue, setFormulaBarValue] = useState('');
  
  const cellRefs = useRef({});
  const formulaInputRef = useRef(null);
  
  // Initialize cells if empty
  useEffect(() => {
    if (Object.keys(cells).length === 0) {
      const initialCells = {};
      for (let row = 0; row < rowCount; row++) {
        for (let col = 0; col < colCount; col++) {
          const cellId = positionToCellId(row, col);
          initialCells[cellId] = {
            id: cellId,
            value: '',
            displayValue: '',
            formula: '',
            formatting: {
              bold: false,
              italic: false,
              fontSize: 12,
              color: '#000000',
              backgroundColor: '#ffffff'
            },
            dependencies: [],
            dependents: []
          };
        }
      }
      setCells(initialCells);
    }
  }, [rowCount, colCount, cells]);
  
  // Update cell dependencies and recalculate dependent cells
  const updateCellAndDependents = (cellId, newValue) => {
    const updatedCells = { ...cells };
    const oldDependencies = updatedCells[cellId]?.dependencies || [];
    
    // Update the cell value
    updatedCells[cellId] = {
      ...updatedCells[cellId],
      value: newValue,
      formula: newValue.startsWith('=') ? newValue : '',
      displayValue: newValue.startsWith('=') 
        ? evaluateFormula(newValue, updatedCells)
        : newValue
    };
    
    // Extract new dependencies
    const newDependencies = [];
    if (newValue.startsWith('=')) {
      const matches = newValue.match(/[A-Z]+\d+/g) || [];
      matches.forEach(match => {
        if (!newDependencies.includes(match)) {
          newDependencies.push(match);
        }
      });
    }
    
    // Update dependencies
    updatedCells[cellId].dependencies = newDependencies;
    
    // Remove this cell from old dependencies' dependents
    oldDependencies.forEach(depId => {
      if (updatedCells[depId] && updatedCells[depId].dependents) {
        updatedCells[depId].dependents = updatedCells[depId].dependents.filter(id => id !== cellId);
      }
    });
    
    // Add this cell to new dependencies' dependents
    newDependencies.forEach(depId => {
      if (!updatedCells[depId]) {
        // Create the cell if it doesn't exist yet
        updatedCells[depId] = {
          id: depId,
          value: '',
          displayValue: '',
          formula: '',
          formatting: {
            bold: false,
            italic: false,
            fontSize: 12,
            color: '#000000',
            backgroundColor: '#ffffff'
          },
          dependencies: [],
          dependents: []
        };
      }
      
      if (!updatedCells[depId].dependents) {
        updatedCells[depId].dependents = [];
      }
      
      if (!updatedCells[depId].dependents.includes(cellId)) {
        updatedCells[depId].dependents.push(cellId);
      }
    });
    
    // Recalculate all dependent cells
    const recalculateDependents = (id) => {
      const dependents = updatedCells[id]?.dependents || [];
      dependents.forEach(depId => {
        if (updatedCells[depId] && updatedCells[depId].formula) {
          updatedCells[depId].displayValue = evaluateFormula(
            updatedCells[depId].formula,
            updatedCells
          );
          recalculateDependents(depId);
        }
      });
    };
    
    recalculateDependents(cellId);
    
    setCells(updatedCells);
  };
  
  // Handle cell selection
  const handleCellClick = (row, col) => {
    const cellId = positionToCellId(row, col);
    setSelectedCell(cellId);
    setEditingCell(null);
    
    const cell = cells[cellId] || { value: '', formula: '' };
    setFormulaBarValue(cell.formula || cell.value);
  };
  
  // Handle double click to start editing
  const handleCellDoubleClick = (row, col) => {
    const cellId = positionToCellId(row, col);
    setSelectedCell(cellId);
    setEditingCell(cellId);
    
    const cell = cells[cellId] || { value: '', formula: '' };
    setEditValue(cell.formula || cell.value);
  };
  
  // Handle cell edit confirmation
  const handleCellConfirm = () => {
    if (editingCell) {
      updateCellAndDependents(editingCell, editValue);
      setEditingCell(null);
    }
  };
  
  // Handle keydown events for navigation and editing
  const handleCellKeyDown = (e, row, col) => {
    const currentCellId = positionToCellId(row, col);
    
    if (e.key === 'Enter') {
      if (editingCell) {
        handleCellConfirm();
      } else {
        setEditingCell(currentCellId);
        setEditValue(cells[currentCellId]?.formula || cells[currentCellId]?.value || '');
      }
      e.preventDefault();
    } else if (e.key === 'Escape' && editingCell) {
      setEditingCell(null);
      e.preventDefault();
    } else if (e.key === 'Tab') {
      handleCellClick(row, col + 1);
      e.preventDefault();
    } else if (e.key === 'ArrowUp' && !editingCell) {
      if (row > 0) handleCellClick(row - 1, col);
      e.preventDefault();
    } else if (e.key === 'ArrowDown' && !editingCell) {
      if (row < rowCount - 1) handleCellClick(row + 1, col);
      e.preventDefault();
    } else if (e.key === 'ArrowLeft' && !editingCell) {
      if (col > 0) handleCellClick(row, col - 1);
      e.preventDefault();
    } else if (e.key === 'ArrowRight' && !editingCell) {
      if (col < colCount - 1) handleCellClick(row, col + 1);
      e.preventDefault();
    }
  };
  
  // Handle formula bar input
  const handleFormulaBarChange = (e) => {
    setFormulaBarValue(e.target.value);
  };
  
  // Handle formula bar confirmation
  const handleFormulaBarConfirm = () => {
    if (selectedCell) {
      updateCellAndDependents(selectedCell, formulaBarValue);
    }
  };
  
  // Get cell display style based on formatting
  const getCellStyle = (cellId) => {
    const cell = cells[cellId];
    if (!cell) return {};
    
    return {
      fontWeight: cell.formatting.bold ? 'bold' : 'normal',
      fontStyle: cell.formatting.italic ? 'italic' : 'normal',
      fontSize: `${cell.formatting.fontSize}px`,
      color: cell.formatting.color,
      backgroundColor: cell.formatting.backgroundColor
    };
  };
  
  // Toggle cell formatting option
  const toggleFormatting = (option) => {
    if (!selectedCell) return;
    
    const updatedCells = { ...cells };
    updatedCells[selectedCell].formatting = {
      ...updatedCells[selectedCell].formatting,
      [option]: !updatedCells[selectedCell].formatting[option]
    };
    
    setCells(updatedCells);
  };
  
  // Render the spreadsheet
  return (
    <div className="spreadsheet-container">
      <div className="toolbar">
        <button className="toolbar-button file-button">File</button>
        <button className="toolbar-button">Edit</button>
        <button className="toolbar-button">View</button>
        <button className="toolbar-button">Insert</button>
        <button className="toolbar-button">Format</button>
        <button className="toolbar-button">Data</button>
        <button className="toolbar-button">Tools</button>
        <button className="toolbar-button">Add-ons</button>
        <button className="toolbar-button">Help</button>
        <div className="toolbar-separator"></div>
        <button className="toolbar-button formatting-button" onClick={() => toggleFormatting('bold')}>
          <span className="icon">B</span>
        </button>
        <button className="toolbar-button formatting-button" onClick={() => toggleFormatting('italic')}>
          <span className="icon">I</span>
        </button>
        <div className="toolbar-separator"></div>
        <select className="font-selector">
          <option>Arial</option>
        </select>
        <select className="font-size-selector">
          <option>10</option>
        </select>
      </div>
      
      <div className="formula-bar">
        <div className="formula-icon">fx</div>
        <input
          type="text"
          className="formula-input"
          value={formulaBarValue}
          onChange={handleFormulaBarChange}
          onBlur={handleFormulaBarConfirm}
          onKeyDown={(e) => e.key === 'Enter' && handleFormulaBarConfirm()}
          ref={formulaInputRef}
        />
      </div>
      
      <div className="spreadsheet-grid">
        <div className="corner-header"></div>
        
        <div className="column-headers">
          {Array.from({ length: colCount }).map((_, col) => (
            <div key={`header-col-${col}`} className="column-header">
              {colIndexToLetter(col)}
            </div>
          ))}
        </div>
        
        <div className="row-headers">
          {Array.from({ length: rowCount }).map((_, row) => (
            <div key={`header-row-${row}`} className="row-header">
              {row + 1}
            </div>
          ))}
        </div>
        
        <div className="grid">
          {Array.from({ length: rowCount }).map((_, row) => (
            <div key={`row-${row}`} className="grid-row">
              {Array.from({ length: colCount }).map((_, col) => {
                const cellId = positionToCellId(row, col);
                const cell = cells[cellId] || {};
                const isSelected = selectedCell === cellId;
                const isEditing = editingCell === cellId;
                
                return (
                  <div
                    key={cellId}
                    className={`grid-cell ${isSelected ? 'selected' : ''}`}
                    style={getCellStyle(cellId)}
                    onClick={() => handleCellClick(row, col)}
                    onDoubleClick={() => handleCellDoubleClick(row, col)}
                    onKeyDown={(e) => handleCellKeyDown(e, row, col)}
                    tabIndex="0"
                    ref={(el) => (cellRefs.current[cellId] = el)}
                  >
                    {isEditing ? (
                      <input
                        type="text"
                        className="cell-editor"
                        value={editValue}
                        onChange={(e) => setEditValue(e.target.value)}
                        onBlur={handleCellConfirm}
                        onKeyDown={(e) => {
                          if (e.key === 'Enter') {
                            handleCellConfirm();
                            e.preventDefault();
                          } else if (e.key === 'Escape') {
                            setEditingCell(null);
                            e.preventDefault();
                          }
                        }}
                        autoFocus
                      />
                    ) : (
                      <div className="cell-content">
                        {cell.displayValue !== undefined ? cell.displayValue : cell.value}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
          ))}
        </div>
      </div>
      
      <div className="status-bar">
        <div className="sheet-tabs">
          <div className="sheet-tab active">Sheet1</div>
          <div className="sheet-tab">Sheet2</div>
          <div className="sheet-tab">Sheet3</div>
        </div>
      </div>
    </div>
  );
};

export default Spreadsheet;