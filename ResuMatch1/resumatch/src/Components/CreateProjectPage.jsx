import React from 'react'
import { Link, useOutletContext } from 'react-router-dom';

function CreateProjectPage() {
  const { padding } = useOutletContext();
  
  return (
    <div className={`main-container ${padding}`}>
        <div className='content'>
            <h2>Let’s Start with new project</h2>
            <Link to='/new/project'>Create new project</Link>
        </div>
    </div>
  )
}

export default CreateProjectPage




