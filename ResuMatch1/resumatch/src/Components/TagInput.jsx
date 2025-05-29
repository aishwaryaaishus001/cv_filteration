import React, { useState } from 'react';
import '../App.css';

function TagInput() {
  const [inputValue, setInputValue] = useState('');
  const [tags, setTags] = useState([]);

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && inputValue.trim() !== '') {
      e.preventDefault();
      setTags([...tags, inputValue.trim()]);
      setInputValue('');
    }
  };

  const removeTag = (indexToRemove) => {
    setTags(tags.filter((_, index) => index !== indexToRemove));
  };

  return (
    <div className="tag-input-wrapper">
      {tags.map((tag, index) => (
        <div key={index} className="tag">
          {tag}
          <span className="remove-tag" onClick={() => removeTag(index)}>×</span>
        </div>
      ))}
      <input
        type="text"
        className="tag-input"
        value={inputValue}
        onChange={(e) => setInputValue(e.target.value)}
        onKeyDown={handleKeyDown}
        placeholder="Type and press Enter"
      />
    </div>
  );
}

export default TagInput;
