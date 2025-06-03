import React, { useState, useRef } from 'react'
import arrowUp from '../assets/arrowUp.svg';
import { Link, useParams, useNavigate, useOutletContext } from 'react-router-dom';
import { useQuery, useMutation } from '@tanstack/react-query'
import axios from 'axios'

function JobDiscripPage() {
  const {padding} = useOutletContext()
  const navigate = useNavigate()
  const prompt = useRef('')
  const { projectId } = useParams();  // Get projectId from URL

  const [activeIndex, setActiveIndex] = useState(); 
  const [isDialogOpen, setIsDialogOpen] = useState(false);


  const data = [
    { id: 101, title: "Frontend Developer Project" },
    { id: 102, title: "Data Analyst Role" },
    { id: 103, title: "Backend Engineer Hiring" },
    { id: 104, title: "ML Engineer Opening" },
    { id: 105, title: "Product Manager Recruitment" }
  ];


  const { mutate } = useMutation({
    mutationFn: async ({ prompt, projectId }) => {
      const res = await axios.post("http://localhost:5001/prompt", {
        prompt,
        project_id: projectId  // 👈 Send project ID
      });
      return res.data;
    }
  });

  const { data: historyData, isLoading, isError, error } = useQuery({
    queryKey: ['prompt-history', projectId], // include projectId in cache key
    queryFn: async () => {
      const res = await axios.get(
        `http://localhost:5001/history/prompt_history?project_id=${projectId}`
      );
      return res.data.History_data;
    },
    enabled: isDialogOpen && !!projectId, // only fetch if modal is open and projectId exists
  });


  function send() {
    const value = prompt.current.value.trim();
    if (!value) {
      alert("Prompt is empty");
      console.warn("Prompt is empty");
      return;
    }

    mutate(
      { prompt: value, projectId },  // 👈 Send both values
      {
        onSuccess: (data) => {
          console.log("Posted:", data);
          navigate(`/new/project/priority/${projectId}/${data.prompt_id}`);
        },
        onError: (error) => {
          console.error("Error posting:", error);
        },
      }
    );
  }

  
  console.log("Project ID:", projectId); // Log the projectId
  console.log("History Data:", historyData); // Log the fetched history data

  if (isLoading) return <p>Loading...</p>;
  if (isError) return <p>{error.message}</p>;

  return (
    <div className={`main-container ${padding}`}>

        <div className='content'>
            <div className='contain'>   
              <Link onClick={() => setIsDialogOpen(true)}>History</Link>
            </div>

            <h2>Enter Your job Description</h2>
            <div className='prompt-part'>
                <textarea ref={prompt} placeholder='Enter prompt' className='textarea-prop' rows="5" 
                  onKeyDown={(e) => {
                    if (e.key === 'Enter' && !e.shiftKey) {
                      e.preventDefault(); // Prevents newline from being added
                      send();
                    }
                }}/>
                <div className='submit-btn' onClick={()=> send()}>
                    <img src={arrowUp} alt="arrow-up-Icon"/>
                </div>
            </div>
        </div>

            {isDialogOpen && (
              <div className="dialog-overlay">
                <div className="dialog-box">
                  <h3>Prompt History</h3>


                  <div className='nav-item'>
                    <ul>
                        {historyData.map((prompt, index) => (
                          <li
                            key={prompt.id}
                            className={activeIndex === index ? 'active' : ''}
                            onClick={() => {
                              setActiveIndex(index);
                              navigate(`/new/project/profile/${projectId}/${prompt.id}`);
                            }}
                          >
                            <a className={activeIndex === index ? 'active' : ''} href="#">
                              {prompt.prompt}
                            </a>
                          </li>
                        ))}
                    </ul> 
                  </div>


                  <button onClick={() => setIsDialogOpen(false)} className="close-btn">Close</button>
                </div>
              </div>
            )}

    </div>
  )
}

export default JobDiscripPage