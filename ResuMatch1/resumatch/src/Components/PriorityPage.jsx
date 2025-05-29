import React, { useEffect, useState } from 'react';
import { useQuery, useMutation } from '@tanstack/react-query'
import axios from 'axios';
import { Link, useOutletContext, useNavigate, useParams } from 'react-router-dom';


function PriorityPage() {
    const { padding } = useOutletContext();
    const navigate = useNavigate();
    const { projectId, promptId } = useParams();

    const { data, isLoading, isError, error } = useQuery({
    queryKey: ['criteria-data'],
    queryFn: async ()=>{
        const res = await axios.get("http://localhost:5001/keywords")
        return res.data.keywords
    }
    })

    const { mutate, isPending } = useMutation({
      mutationFn: async (data) => {
        const res = await axios.post("http://localhost:5001/send-data", {
          promptId: promptId, 
          projectId: projectId,  
          Json: data
        });
        return res.data;
      }
    });


    const [fields, setFields] = useState([
        { id: 1, label: 'Skills', tags: [], input: '' },
        { id: 2, label: 'Education', tags: [], input: '' },
        { id: 3, label: 'Projects', tags: [], input: '' },
        { id: 4, label: 'Experience', tags: [], input: '' },
        { id: 5, label: 'Certifications', tags: [], input: '' },
    ]);

    useEffect(() => {
        if (data) {
        const updatedFields = fields.map((field) => ({
            ...field,
            tags: data[field.label] || [], 
        }));
        setFields(updatedFields);
        }
    }, [data]);



    if (isLoading) return <p>Loading...</p>;
    if (isError) return <p>{error.message}</p>;

    function send() {
        const isEmpty = fields.every(field => field.tags.length === 0);
        if (isEmpty) {
            alert("All fields are empty.");
            return;
        }

        // Transform fields to an object like { Skills: [...], Education: [...], ... }
        const formattedData = fields.reduce((acc, field) => {
            acc[field.label] = field.tags;
            return acc;
        }, {});

        mutate(formattedData, {
            onSuccess: (data) => {
                console.log("Posted:", data);
                navigate(`/new/project/profile/${projectId}`);
            },
            onError: (error) => {
                console.error("Error:", error);
            },
        });
    }


    const handleInputChange = (index, value) => {
    const updated = [...fields];
    updated[index].input = value;
    setFields(updated);
    };

    const handleKeyDown = (e, index) => {
    if (e.key === 'Enter') {
        e.preventDefault();
        const trimmed = fields[index].input.trim();
        if (!trimmed) return;

        const updated = [...fields];
        updated[index].tags.push(trimmed);
        updated[index].input = '';
        setFields(updated);
    }
    };

    const removeTag = (fieldIndex, tagIndex) => {
    const updated = [...fields];
    updated[fieldIndex].tags.splice(tagIndex, 1);
    setFields(updated);
    };

    console.log("Project ID:", projectId); // Log the projectId
    console.log("----------:", data); // Log the projectId

  return (
    <div className={`main-container ${padding}`}>

      {isPending && (
        <div className="loading-overlay">
          <div className="loader"></div>
          <p>Processing and Ranking...</p>
        </div>
      )}

      <div className="content">
        <div className="contain">      
          <Link to='#' onClick={()=> send()}>Go</Link>
        </div>

        <div className="sub-content">
          <div className="sub-container">
            {fields.map((field, fieldIndex) => (
              <div className="form-group" key={field.id}>
                <label htmlFor={field.label}>{field.label}</label>
                <div className="tag-input-wrapper">
                  {field.tags.map((tag, tagIndex) => (
                    <div key={tagIndex} className="tag">
                      <span className="name-tag">{tag}</span>
                      <span className="remove-tag" onClick={() => removeTag(fieldIndex, tagIndex)}>×</span>
                    </div>
                  ))}
                  <input
                    id= {field.label}
                    type="text"
                    className="tag-input"
                    value={field.input}
                    onChange={(e) => handleInputChange(fieldIndex, e.target.value)}
                    onKeyDown={(e) => handleKeyDown(e, fieldIndex)}
                    placeholder="Type and press Enter"
                  />
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default PriorityPage;
